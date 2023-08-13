import random
from itertools import filterfalse
from typing import Tuple

import pytest

from mms_monthly_cli.mms_monthly import get_table_names_and_sizes, get_years_and_months

SIZE_THRESHOLD = 2 * 10**7


@pytest.fixture(scope="session")
def random_year_month() -> Tuple[int, int]:
    years_months = get_years_and_months()
    random_year = random.choice(list(years_months.keys()))
    random_month = random.choice(years_months[random_year])
    return (random_year, random_month)


@pytest.fixture
def random_DATA_table(random_year_month) -> Tuple[int, int, str, int]:
    year, month = random_year_month
    table_sizes = get_table_names_and_sizes(year, month, "DATA")
    small_tables = filterfalse(lambda x: table_sizes[x] > SIZE_THRESHOLD, table_sizes)
    small_non_enumerated_tables = filterfalse(
        lambda x: "1" in x and "2" in x, small_tables
    )
    table = random.choice(list(small_non_enumerated_tables))
    return year, month, table, table_sizes[table]


@pytest.fixture
def random_PREDISP_ALL_DATA_table(random_year_month) -> Tuple[int, int, str, int]:
    year, month = random_year_month
    table_sizes = get_table_names_and_sizes(year, month, "PREDISP_ALL_DATA")
    small_tables = filterfalse(lambda x: table_sizes[x] > SIZE_THRESHOLD, table_sizes)
    small_non_enumerated_tables = filterfalse(
        lambda x: "1" in x and "2" in x, small_tables
    )
    table = random.choice(list(small_non_enumerated_tables))
    return year, month, table, table_sizes[table]


@pytest.fixture
def random_P5MIN_ALL_DATA_table() -> Tuple[int, int, str, int]:
    month = random.choice(range(1, 13))
    table_sizes = get_table_names_and_sizes(2022, month, "P5MIN_ALL_DATA")
    small_tables = filterfalse(lambda x: table_sizes[x] > SIZE_THRESHOLD, table_sizes)
    small_non_enumerated_tables = filterfalse(
        lambda x: "1" in x and "2" in x, small_tables
    )
    table = random.choice(list(small_non_enumerated_tables))
    return 2022, month, table, table_sizes[table]
