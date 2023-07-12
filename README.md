# AEMO Monthly Data Archive Tool

A CLI utility to find and obtain data made available through AEMO's [MMS Monthly Data Archive](http://www.nemweb.com.au/Data_Archive/Wholesale_Electricity/MMSDM/).

> **Note**
> Most users will prefer to use  to access NEMWeb data.
> This package and its CLI have some overlap with [NEMOSIS](https://github.com/UNSW-CEEM/NEMOSIS)
> and [NEMSEER](https://github.com/UNSW-CEEM/NEMSEER).
> However:
> - NEMOSIS does not provide access to the monthly data archive, and does not allow a user to download certain
 >   tables such as bid data tables (`BIDPEROFFER`).
> - NEMSEER is specifically designed to handle PASA and pre-dispatch tables available in the monthly data archive

## Installation

Recommended that you use [`pipx`](https://github.com/pypa/pipx) to install the CLI as it [prevents dependency conflicts](https://github.com/pypa/pipx#overview-what-is-pipx).

```bash
pipx install mms-monthly-cli
```

However, you can still install via `pip` if you wish to:
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

This will expose the following functions (accessed using `mms_monthly.<func_name>`):

```python
get_years_and_months() -> Dict[int, List[int]]
```
```md
Years and months with data on NEMWeb MMSDM Historical Data Archive
Returns:
    Months mapped to each year. Data is available for each of these months.
```

```python
get_available_tables(year: int, month: int) -> List[str]
```
```md
Tables that can be requested from MMSDM Historical Data Archive for a
   particular month and year.
Args:
    year: Year
    month: Month

Returns:
    List of tables associated with that forecast type for that period
```

```python
get_table_names_and_sizes(year: int, month: int) -> Dict
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
    regex: Regular expression pattern, with one group capture
Returns:
    Tuple of table names and file sizes
```

```python
get_and_unzip_table_csv(year: int, month: int, table: str, cache: pathlib.Path) -> None
```
```md
Unzipped (single) csv file downloaded from `url` to `cache`

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
```

### CLI tool

The CLI tool uses [Typer](https://typer.tiangolo.com/).

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
