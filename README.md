# AEMO Monthly Data Archive Tool
[![PyPI version](https://badge.fury.io/py/mms-monthly-cli.svg)](https://badge.fury.io/py/mms-monthly-cli)
[![Continuous Integration and Deployment](https://github.com/prakaa/mms-monthly-cli/actions/workflows/cicd.yml/badge.svg)](https://github.com/prakaa/mms-monthly-cli/actions/workflows/cicd.yml)
[![codecov](https://codecov.io/gh/prakaa/mms-monthly-cli/branch/master/graph/badge.svg?token=WL7DH013Q7)](https://codecov.io/gh/prakaa/mms-monthly-cli)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/prakaa/mms-monthly-cli/master.svg)](https://results.pre-commit.ci/latest/github/prakaa/mms-monthly-cli/master)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A CLI utility to find and obtain data made available through AEMO's [MMS Monthly Data Archive](http://www.nemweb.com.au/Data_Archive/Wholesale_Electricity/MMSDM/).

> **Note**
>
> This package and its CLI have some overlap with [NEMOSIS](https://github.com/UNSW-CEEM/NEMOSIS)
> and [NEMSEER](https://github.com/UNSW-CEEM/NEMSEER).
> However:
> - NEMOSIS does not provide access to the monthly data archive, and does not allow a user to download certain
 >   tables such as bid data tables (`BIDPEROFFER`).
> - NEMSEER only handles PASA and pre-dispatch tables available in the monthly data archive, though it
>   provides a lot of useful utilities for handling these tables

## Installation

Recommended that you use [`pipx`](https://github.com/pypa/pipx) to install the CLI as it [prevents dependency conflicts](https://github.com/pypa/pipx#overview-what-is-pipx).

```bash
pipx install mms-monthly-cli
```

However, you can still install via `pip` if you are only using the Python package:
```bash
pip install mms-monthly-cli
```

## Usage

You can use this package as a module (source code functions within [`mms_monthly.py`](./mms_monthly_cli/mms_monthly.py)) or as a CLI tool to:

1. Inspect what data is available
2. Download and unzip a table CSV for a particular period (i.e. a month within a year)

### Python module

Simply import `mms_monthly_cli` as follows:

```python
import mms_monthly_cli.mms_monthly as mms_monthly
```

This will expose the functions listed below (accessed using `mms_monthly.<func_name>`).

> [!NOTE]
> The `data_dir` argument requires you to specify which folder within `MMSDM_YYYY_MM` you are interested in.
> Most users will be interested in tables within `DATA` (i.e. `data_dir="DATA"`), but you can also access `PREDISP_ALL_DATA` (complete pre-dispatch data)
> and `P5MIN_ALL_DATA` (complete 5-minute pre-dispatch data).
>
> If you are accessing pre-dispatch data, consider using [NEMSEER](https://github.com/UNSW-CEEM/NEMSEER).

---
```python
get_years_and_months() -> Dict[int, List[int]]
```
```md
Years and months with data on NEMWeb MMSDM Historical Data Archive
Returns:
    Months mapped to each year. Data is available for each of these months.
```
---
```python
get_available_tables(year: int, month: int, data_dir: str) -> List[str]
```
```md
Tables that can be requested from MMSDM Historical Data Archive for a
   particular month and year.
Args:
    year: Year
    month: Month
    data_dir: Directory within monthly archives

Returns:
    List of tables associated with that forecast type for that period
```
---
```python
get_table_names_and_sizes(year: int, month: int, data_dir: str) -> Dict
```
```md
Returns table names and sizes from MMSDM Historical Data Archive page

For a year and month in the MMSDM Historical Data Archive, returns a list of
tuples each consisting of:
- A table name (obtained via captured regex group)
- The size of the associated zip file

Args:
    year: Year
    month: Month
    data_dir: Directory within monthly archives
Returns:
    Tuple of table names and file sizes
```
---
```python
get_and_unzip_table_csv(year: int, month: int, data_dir: str, table: str, cache: pathlib.Path) -> None
```
```md
Unzipped (single) csv file downloaded from `url` to `cache`

This function:

1. Downloads zip file in chunks to limit memory use and enable progress bar
2. Validates that the zip contains a single file that has the same name as the zip

Args:
    year: Year
    month: Month
    data_dir: Directory within monthly archives
    table: Table name
    cache: Path to save zip.
Returns:
    None. Extracts csv to `cache`
```
---
### CLI tool

The CLI tool uses [Typer](https://typer.tiangolo.com/).

![CLI usage](./mms-monthly-cli.gif)
<sub><sup>GIF produced using [asciinema](https://github.com/asciinema/asciinema) and [agg](https://github.com/asciinema/agg)</sup></sub>

Usage is documented within the tool:
```bash
mms-monthly-cli --help
```
...which returns:
```bash
Usage: mms-monthly-cli [OPTIONS] COMMAND [ARGS]...

 A CLI utility to find and obtain data made available through AEMO's MMS Monthly Data
 Archive: http://www.nemweb.com.au/Data_Archive/Wholesale_Electricity/MMSDM/

╭─ Options ───────────────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.                 │
│ --show-completion             Show completion for the current shell, to copy it or      │
│                               customize the installation.                               │
│ --help                        Show this message and exit.                               │
╰─────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ──────────────────────────────────────────────────────────────────────────────╮
│ available-periods  Displays years and the months within them for which data is          │
│                    available                                                            │
│ available-tables   Displays available tables for a period (i.e. supplied month and      │
│                    year)                                                                │
│ get-table          Download and unzip monthly data zip file to get data table CSV in    │
│                    cache. To see available periods, use the `available_periods` command │
│                    To see available tables for a given period, use the                  │
│                    `available_tables` command                                           │
╰─────────────────────────────────────────────────────────────────────────────────────────╯
```

## License

This tool and associated source code (reused from [`nemseer`](https://github.com/UNSW-CEEM/NEMSEER), which is licensed under GNU GPL-3.0-or-later) was created by Abhijith Prakash.

This tool and its source code is licensed under the terms of [GNU GPL-3.0-or-later licences](./LICENSE).
