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

from pathlib import Path

import typer
from rich import print
from typing_extensions import Annotated

from .mms_monthly import (
    get_and_unzip_table_csv,
    get_available_tables,
    get_years_and_months,
)

app = typer.Typer(
    no_args_is_help=True,
    help=(
        "A CLI utility to find and obtain data made available through "
        + "AEMO's MMS Monthly Data Archive: "
        + "http://www.nemweb.com.au/Data_Archive/Wholesale_Electricity/MMSDM/"
    ),
)


@app.command()
def available_periods():
    """
    Displays years and the months within them for which data is available
    """
    print(get_years_and_months())


@app.command(no_args_is_help=True)
def available_tables(year: int, month: int):
    """
    Displays available tables for a period (i.e. supplied month and year)
    """
    print(get_available_tables(year, month))


@app.command(no_args_is_help=True)
def get_table(
    year: int,
    month: int,
    table: str,
    cache: Annotated[
        Path,
        typer.Argument(
            help="Directory to save data to. If it does not exist, it will be created"
        ),
    ],
):
    """
    Download and unzip monthly data zip file to get data table CSV in cache.
    To see available periods, use the `available_periods` command
    To see available tables for a given period, use the `available_tables` command
    """
    get_and_unzip_table_csv(year, month, table, cache)
