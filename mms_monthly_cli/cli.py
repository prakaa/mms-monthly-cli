import argparse
import sys
from pprint import pprint
from typing import Union

from mms_monthly import (
    get_and_unzip_table_csv,
    get_available_tables,
    get_years_and_months,
)


def cli_parser() -> Union[argparse.Namespace, None]:
    description = (
        "A CLI utility to find and obtain data made available through "
        + "AEMO's MMS Monthly Data Archive: "
        + "http://www.nemweb.com.au/Data_Archive/Wholesale_Electricity/MMSDM/"
    )
    # create the top-level parser
    parser = argparse.ArgumentParser(description=description)
    subparsers = parser.add_subparsers(
        title="subcommands",
        description="valid subcommands",
        help="additional help",
        dest="subparser_name",
    )

    # create the parser for the "available-periods" command
    subparsers.add_parser(
        "available-periods",
        help="Displays months and years for which data is available",
    )

    # create the parser for the "available-tables" command
    parser_at = subparsers.add_parser(
        "available-tables",
        help="Displays available tables fora period (i.e. supplied month and year)",
    )
    parser_at.add_argument("-year", type=int, required=True, help="Data year")
    parser_at.add_argument("-month", type=int, required=True, help="Data month")

    # create the parser for the "get-table" command
    parser_gt = subparsers.add_parser(
        "get-table",
        help=(
            "Download and unzip monthly data zip file to get data table CSV in cache. "
            + "To see available periods, use `available-periods`, "
            + "To see available tables for a given period, use `available-tables`"
        ),
    )
    parser_gt.add_argument("-year", type=int, required=True, help="Data year")
    parser_gt.add_argument("-month", type=int, required=True, help="Data month")
    parser_gt.add_argument("-table", type=str, required=True, help="Table name")
    parser_gt.add_argument(
        "-cache",
        type=str,
        required=True,
        help=(
            "Path to save data to. The directory will be"
            + "created if it does not exist"
        ),
    )
    if len(sys.argv) < 2:
        parser.print_usage()
        sys.exit(1)
    else:
        return parser.parse_args()


def main():
    args = cli_parser()
    subcommand = args.subparser_name
    if subcommand == "available-periods":
        pprint(get_years_and_months())
    elif subcommand == "available-tables":
        pprint(get_available_tables(args.year, args.month))
    elif subcommand == "get-table":
        get_and_unzip_table_csv(args.year, args.month, args.table, args.cache)
