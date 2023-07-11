# AEMO Monthly Data Archive Tool

A CLI utility to find and obtain data made available through AEMO's [MMS Monthly Data Archive](http://www.nemweb.com.au/Data_Archive/Wholesale_Electricity/MMSDM/").

## Usage

You can use this package as a module (source code functions within `[mms_monthly.py](./mms_monthly_cli/mms_monthly.py)`) or as a CLI tool to:

1. Inspect what data is available
2. Download and unzip a table CSV for a particular period (i.e. a month within a year)

### CLI tool

The CLI tool uses [Typer](https://typer.tiangolo.com/).

Usage is documented within the tool:
```bash
mms-monthly-cli --help
```
## License

This tool and associated source code (reused from [`nemseer`](https://github.com/UNSW-CEEM/NEMSEER), which is licensed under GNU GPL-3.0-or-later) was created by Abhijith Prakash.

This tool and its source code is licensed under the terms of [GNU GPL-3.0-or-later licences](./LICENSE).
