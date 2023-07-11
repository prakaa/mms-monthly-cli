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
from pathlib import Path
from re import match
from typing import Dict, List
from zipfile import BadZipFile, ZipFile

import requests
from bs4 import BeautifulSoup
from tqdm.auto import tqdm
from user_agent import generate_user_agent

logger = logging.getLogger(__name__)

# Data

MMSDM_ARCHIVE_URL = "http://www.nemweb.com.au/Data_Archive/Wholesale_Electricity/MMSDM/"
"""Wholesale electricity data archive base URL"""

# Functions to handle requests and scraped soup


def _build_nemweb_get_header(useragent: str) -> Dict[str, str]:
    """Builds request header for GET requests from NEMWeb

    Args:
        useragent: User-Agent string to use
    Returns:
        Dict that can be used as a request header
    """
    header = {
        "Host": "www.nemweb.com.au",
        "User-Agent": useragent,
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;"
            + "q=0.9,image/avif,image/webp,*/*;q=0.8"
        ),
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    return header


def _request_content(
    url: str, useragent: str, additional_header: Dict = {}
) -> requests.Response:
    """Initiates a GET request with header information.

    Args:
        url: URL for GET request.
        useragent: User-Agent to use in header.
        additional_header: Empty dictionary as default. Can be used to add
            additional header information to GET request.
    Returns:
        requests Response object.
    """
    header = _build_nemweb_get_header(useragent)
    if additional_header:
        header.update(additional_header)
    r = requests.get(url, headers=header)
    return r


def _rerequest_to_obtain_soup(url: str, additional_header: Dict = {}) -> BeautifulSoup:
    """Continually launches requests until a 200 (OK) code is returned.

    Args:
        url: URL for GET request.
        useragent: User-Agent to use in header.
        additional_header: Empty dictionary as default. Can be used to add
                           additional header information to GET request.

    Returns:
        BeautifulSoup object with parsed HTML.

    """
    useragent = generate_user_agent()
    r = _request_content(url, useragent, additional_header=additional_header)
    while (ok := r.status_code == requests.status_codes.codes["OK"]) < 1:
        r = _request_content(url, useragent, additional_header=additional_header)
        if r.status_code == requests.status_codes.codes["OK"]:
            ok += 1
        else:
            logging.info("Relaunching request")
            useragent = generate_user_agent()
    soup = BeautifulSoup(r.content, "html.parser")
    return soup


def _get_all_links_from_soup(year: int, month) -> List[str]:
    """Gets all links from scraped Data Archive year-month URL
    Args:
        year: Year
        month: Month
    Returns:
        All scraped links
    """
    available_years_and_months = get_years_and_months()
    if (
        year not in available_years_and_months.keys()
        or month not in available_years_and_months[year]
    ):
        raise ValueError(f"Monthly Data Archive does not have data for {month}/{year}")
    url = _construct_yearmonth_url(year, month)
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


def _construct_yearmonth_url(year: int, month: int) -> str:
    """Constructs URL that points to a MMSDM Historical Data Archive zip file

    Args:
        year: Year
        month: Month
    Returns:
        URL to zip file
    """
    url = (
        MMSDM_ARCHIVE_URL
        + f"{year}/MMSDM_{year}_"
        + f'{str(month).rjust(2, "0")}/MMSDM_Historical_Data_SQLLoader/'
        + "DATA/"
    )
    return url


def _construct_table_url(year: int, month: int, table: str) -> str:
    """Constructs URL that points to a MMSDM Historical Data Archive zip file

    Args:
        year: Year
        month: Month
        table: Table of interest
    Returns:
        URL to zip file
    """
    data_url = _construct_yearmonth_url(year, month)
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
    h = requests.head(url, headers=_build_nemweb_get_header(generate_user_agent()))
    total_length = int(h.headers.get("Content-Length", 0))
    return total_length


def _get_table_names(year: int, month: int, regex: str) -> List[str]:
    """Returns table names from MMSDM Historical Data Archive page

    For a year and month in the MMSDM Historical Data Archive, returns a list of
    table names (obtained via captured regex group)

    Args:
        year: Year
        month: Month
        regex: Regular expression pattern, with one group capture
    Returns:
        List of table names
    """
    names = []
    links = _get_all_links_from_soup(year, month)
    for link in links:
        if mo := match(regex, link):
            name = mo.group(1).lstrip("_")
            names.append(name)
    return list(set(names))


# Main functions to find available data, or to obtain data


def get_years_and_months() -> Dict[int, List[int]]:
    """Years and months with data on NEMWeb MMSDM Historical Data Archive
    Returns:
        Months mapped to each year. Data is available for each of these months.
    """

    def _get_months(url: str) -> List[int]:
        """Pull months from scraped links with YYYY-MM date format

        Args:
            url: url for GET request.
            header: useragent to pass to GET request.
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


def get_available_tables(
    year: int,
    month: int,
) -> List[str]:
    """Tables that can be requested from MMSDM Historical Data Archive for a
       particular month and year.
    Args:
        year: Year
        month: Month

    Returns:
        List of tables associated with that forecast type for that period
    """
    table_regex = ".*/PUBLIC_DVD_([A-Z_0-9]*)_[0-9]*.zip"
    names = _get_table_names(year, month, table_regex)
    return sorted(names)


def get_table_names_and_sizes(year: int, month: int) -> Dict:
    """Returns table names and sizes from MMSDM Historical Data Archive page

    For a year and month in the MMSDM Historical Data Archive, returns a list of
    tuples each consisting of:
    - A table name (obtained via captured regex group)
    - The size of the associated zip file

    Args:
        year: Year
        month: Month
        regex: Regular expression pattern, with one group capture
    Returns:
        Tuple of table names and file sizes
    """
    regex = ".*/PUBLIC_DVD_([A-Z_0-9]*)_[0-9]*.zip"
    names_and_sizes = []
    links = _get_all_links_from_soup(year, month)
    for link in links:
        if mo := match(regex, link):
            name = mo.group(1).lstrip("_")
            table_url = _construct_table_url(year, month, name)
            size = _get_filesize(table_url)
            names_and_sizes.append((name, size))
    names_and_size = list(set(names_and_sizes))
    name_size_dict = {}
    for name, size in names_and_size:
        name_size_dict[name] = size
    return name_size_dict


def get_and_unzip_table_csv(year: int, month: int, table: str, cache: Path) -> None:
    """Unzipped (single) csv file downloaded from `url` to `cache`

    This function:

    1. Downloads zip file in chunks to limit memory use and enable progress bar
    2. Validates that the zip contains a single file that has the same name as the zip

    Args:
        year: Year
        month: Month
        table: Table name
        cache: Path to save zip.
    Returns:
        None. Extracts csv to `cache`
    """
    available_tables = get_available_tables(year, month)
    if table not in available_tables:
        raise ValueError(f"Table not in available tables for {month}/{year}")
    if not (cache_path := Path(cache)).exists():
        cache_path.mkdir(parents=True)
    header = _build_nemweb_get_header(generate_user_agent())
    url = _construct_table_url(year, month, table)
    file_name = Path(url).name
    file_path = cache / Path(file_name)
    with requests.get(url, headers=header, stream=True) as resp:
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
