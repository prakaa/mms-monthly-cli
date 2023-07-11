# AEMO Monthly Data Archive Tool

A CLI utility to find and obtain data made available through AEMO's [MMS Monthly Data Archive](http://www.nemweb.com.au/Data_Archive/Wholesale_Electricity/MMSDM/").

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

### CLI tool

The CLI tool uses [Typer](https://typer.tiangolo.com/).

Usage is documented within the tool:
```bash
mms-monthly-cli --help
```
...which produces
```bash
Usage: mms-monthly-cli [OPTIONS] COMMAND [ARGS]...                             
                                                                                
 A CLI utility to find and obtain data made available through AEMO's MMS        
 Monthly Data Archive:                                                          
 http://www.nemweb.com.au/Data_Archive/Wholesale_Electricity/MMSDM/             
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.      │
│ --show-completion             Show completion for the current shell, to copy │
│                               it or customize the installation.              │
│ --help                        Show this message and exit.                    │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────╮
│ available-periods  Displays years and the months within them for which data  │
│                    is available                                              │
│ available-tables   Displays available tables for a period (i.e. supplied     │
│                    month and year)                                           │
│ get-table          Download and unzip monthly data zip file to get data      │
│                    table CSV in cache. To see available periods, use the     │
│                    `available_periods` command To see available tables for a │
│                    given period, use the `available_tables` command          │
╰──────────────────────────────────────────────────────────────────────────────╯
```

## License

This tool and associated source code (reused from [`nemseer`](https://github.com/UNSW-CEEM/NEMSEER), which is licensed under GNU GPL-3.0-or-later) was created by Abhijith Prakash.

This tool and its source code is licensed under the terms of [GNU GPL-3.0-or-later licences](./LICENSE).
