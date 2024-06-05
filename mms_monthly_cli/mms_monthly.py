# A program to scrape and download data from AEMO's Monthly Data Archive
# Copyright (C) <2023>  <Abhijith Prakash>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging
import shutil
from functools import cache
from pathlib import Path
from re import match
from time import sleep
from typing import Dict, List, Union
from zipfile import BadZipFile, ZipFile

import requests
from bs4 import BeautifulSoup
from tqdm.auto import tqdm
from user_agent import generate_user_agent

logger = logging.getLogger(__name__)

# Data

MMSDM_ARCHIVE_URL = (
    "https://www.nemweb.com.au/Data_Archive/Wholesale_Electricity/MMSDM/"
)
"""Wholesale electricity data archive base URL"""

# requests session, to re-use TLS and HTTP connection across requests
# for speed improvement
_session = requests.Session()
_session.headers.update(
    {
        "User-Agent": generate_user_agent(),
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;"
            + "q=0.9,image/avif,image/webp,*/*;q=0.8"
        ),
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
)

# Functions to handle requests and scraped soup


def _request_content(url: str, additional_header: Dict = {}) -> requests.Response:
    """Initiates a GET request.

    Args:
        url: URL for GET request.
    Returns:
        requests Response object.
    """
    r = _session.get(url, headers=additional_header)
    return r


def _rerequest_to_obtain_soup(url: str, additional_header: Dict = {}) -> BeautifulSoup:
    """Continually launches requests until a 200 (OK) code is returned.

    Args:
        url: URL for GET request.

    Returns:
        BeautifulSoup object with parsed HTML.

    """
    r = _request_content(url, additional_header)

    # retry configuration
    initial_wait = 0.1
    max_wait = 10
    backoff = 2
    wait = initial_wait

    while (ok := r.status_code == requests.status_codes.codes["OK"]) < 1:
        r = _request_content(url, additional_header)
        if r.status_code == requests.status_codes.codes["OK"]:
            ok += 1
        else:
            logging.info("Relaunching request")
            sleep(wait)
            wait = min(wait * backoff, max_wait)

    soup = BeautifulSoup(r.content, "html.parser")
    return soup


def _get_all_links_from_soup(
    year: int, month: int, data_dir: Union[str, None]
) -> List[str]:
    """Gets all links from scraped Data Archive year-month URL
    Args:
        year: Year
        month: Month
        data_dir : Directory within monthly archives, or None
    Returns:
        All scraped links
    """
    available_years_and_months = get_years_and_months()
    if (
        year not in available_years_and_months.keys()
        or month not in available_years_and_months[year]
    ):
        raise ValueError(f"Monthly Data Archive does not have data for {month}/{year}")
    url = _construct_yearmonth_url(year, month, data_dir)
    soup = _rerequest_to_obtain_soup(url)
    links = [link.get("href") for link in soup.find_all("a")]
    return links


# Functions to construct filenames and URLs


def _construct_filename(year: int, month: int, table: str) -> str:
    """Constructs filename without file type

    Args:
        year: Year
        month: Month
        table: The name of the table required
    Returns:
        Filename string without file type
    """
    (stryear, strmonth) = (str(year), str(month).rjust(2, "0"))
    prefix = f"PUBLIC_DVD_{table}"
    fn = prefix + f"_{stryear}{strmonth}010000"
    return fn


def _construct_yearmonth_url(year: int, month: int, data_dir: Union[str, None]) -> str:
    """Constructs URL that points to a MMSDM Historical Data Archive zip file

    Args:
        year: Year
        month: Month
        data_dir : Directory within monthly archives, or None
    Returns:
        URL to zip file
    """
    url = (
        MMSDM_ARCHIVE_URL
        + f"{year}/MMSDM_{year}_"
        + f'{str(month).rjust(2, "0")}/MMSDM_Historical_Data_SQLLoader/'
    )
    if data_dir is not None:
        url += data_dir + "/"
    return url


def _construct_table_url(year: int, month: int, data_dir: str, table: str) -> str:
    """Constructs URL that points to a MMSDM Historical Data Archive zip file

    Args:
        year: Year
        month: Month
        data_dir : Directory within monthly archives
        table: Table of interest
    Returns:
        URL to zip file
    """
    data_url = _construct_yearmonth_url(year, month, data_dir)
    fn = _construct_filename(year, month, table)
    url = data_url + fn + ".zip"
    return url


# Functions to obtain table properties


def _get_filesize(url: str) -> int:
    """Gets size of zip file that URL points to (in bytes)

    Args:
        url: URL of zip
    Returns:
        File size in bytes
    """
    h = _session.head(url)
    total_length = int(h.headers.get("Content-Length", 0))
    return total_length


def _get_table_names(year: int, month: int, data_dir: str, regex: str) -> List[str]:
    """Returns table names from MMSDM Historical Data Archive page

    For a year and month in the MMSDM Historical Data Archive, returns a list of
    table names (obtained via captured regex group)

    Args:
        year: Year
        month: Month
        data_dir : Directory within monthly archives
        regex: Regular expression pattern, with one group capture
    Returns:
        List of table names
    """
    names = []
    links = _get_all_links_from_soup(year, month, data_dir)
    for link in links:
        if mo := match(regex, link):
            name = mo.group(1).lstrip("_")
            names.append(name)
    return list(set(names))


# Validator functions


def _validate_data_dir(year: int, month: int, data_dir: str) -> None:
    """Validates user `data_dir` specification

    Args:
        year: Year
        month: Month
        data_dir : Directory within monthly archives
    Errors:
        ValueError: If `data_dir` does not exist
    """
    links = _get_all_links_from_soup(year, month, None)
    links = [Path(link).name for link in links]
    if data_dir not in links:
        raise ValueError(
            f"{data_dir} not in Monthly Data Archive for {year} {month}. "
            + f"Possible dirs: {links}"
        )


# Main functions to find available data, or to obtain data


@cache
def get_years_and_months() -> Dict[int, List[int]]:
    """Years and months with data on NEMWeb MMSDM Historical Data Archive
    Returns:
        Months mapped to each year. Data is available for each of these months.
    """

    def _get_months(url: str) -> List[int]:
        """Pull months from scraped links with YYYY-MM date format

        Args:
            url: url for GET request.
        Returns:
            List of unique months (as integers).
        """
        referer_header = {"Referer": MMSDM_ARCHIVE_URL}
        soup = _rerequest_to_obtain_soup(url, additional_header=referer_header)
        months = []
        for link in soup.find_all("a"):
            url = link.get("href")
            findmonth = match(r".*[0-9]{4}_([0-9]{2})", url)
            if not findmonth:
                continue
            else:
                month = findmonth.group(1)
                months.append(int(month))
        unique = list(set(months))
        return unique

    soup = _rerequest_to_obtain_soup(MMSDM_ARCHIVE_URL)
    links = soup.find_all("a")
    yearmonths = {}
    for link in links:
        url = link.get("href")
        findyear = match(r".*([0-9]{4}).*", url)
        if not findyear:
            continue
        else:
            year = int(findyear.group(1))
            months = _get_months(MMSDM_ARCHIVE_URL + f"{year}/")
            yearmonths[year] = months
    return yearmonths


@cache
def get_available_tables(year: int, month: int, data_dir: str) -> List[str]:
    """Tables that can be requested from MMSDM Historical Data Archive for a
       particular month and year.
    Args:
        year: Year
        month: Month
        data_dir : Directory within monthly archives

    Returns:
        List of tables associated with that forecast type for that period
    """
    _validate_data_dir(year, month, data_dir)
    table_regex = ".*/PUBLIC_DVD_([A-Z_0-9]*)_[0-9]*.zip"
    names = _get_table_names(year, month, data_dir, table_regex)
    return sorted(names)


@cache
def get_table_names_and_sizes(year: int, month: int, data_dir: str) -> Dict:
    """Returns table names and sizes from MMSDM Historical Data Archive page

    For a year and month in the MMSDM Historical Data Archive, returns a list of
    tuples each consisting of:
    - A table name (obtained via captured regex group)
    - The size of the associated zip file

    Args:
        year: Year
        month: Month
        data_dir : Directory within monthly archives
    Returns:
        Tuple of table names and file sizes
    """
    regex = ".*/PUBLIC_DVD_([A-Z_0-9]*)_[0-9]*.zip"
    names_and_sizes = []
    links = _get_all_links_from_soup(year, month, data_dir)
    for link in links:
        if mo := match(regex, link):
            name = mo.group(1).lstrip("_")
            table_url = _construct_table_url(year, month, data_dir, name)
            size = _get_filesize(table_url)
            names_and_sizes.append((name, size))
    names_and_size = list(set(names_and_sizes))
    name_size_dict = {}
    for name, size in names_and_size:
        name_size_dict[name] = size
    return name_size_dict


def get_and_unzip_table_csv(
    year: int, month: int, data_dir: str, table: str, cache: Path
) -> None:
    """Unzipped (single) csv file downloaded from `url` to `cache`

    This function:

    1. Downloads zip file in chunks to limit memory use and enable progress bar
    2. Validates that the zip contains a single file that has the same name as the zip

    Args:
        year: Year
        month: Month
        data_dir : Directory within monthly archives
        table: Table name
        cache: Path to save zip.
    Returns:
        None. Extracts csv to `cache`
    """
    available_tables = get_available_tables(year, month, data_dir)
    if table not in available_tables:
        raise ValueError(f"Table not in available tables for {month}/{year}")
    if not (cache_path := Path(cache)).exists():
        cache_path.mkdir(parents=True)
    url = _construct_table_url(year, month, data_dir, table)
    file_name = Path(url).name
    file_path = cache / Path(file_name)
    with _session.get(url, stream=True) as resp:
        total_length = int(resp.headers.get("Content-Length", 0))
        resp.raise_for_status()
        with tqdm.wrapattr(resp.raw, "read", desc=file_name, total=total_length) as raw:
            with open(file_path, "wb") as fout:
                shutil.copyfileobj(raw, fout)
    z = ZipFile(file_path)
    if (
        len(csvfn := z.namelist()) == 1
        and (zfn := match(".*DATA/(.*).zip", url))
        and (fn := match("(.*).[cC][sS][vV]", csvfn.pop()))
        and (fn.group(1) == zfn.group(1))
    ):
        try:
            z.extractall(cache)
            z.close()
        except BadZipFile:
            logger.error(f"{z.testzip()} invalid or corrupted")
        Path(file_path).unlink()
    else:
        raise ValueError(f"Unexpected contents in zipfile from {url}")
