from pathlib import Path

import pytest

from mms_monthly_cli.mms_monthly import _construct_filename, get_and_unzip_table_csv


def test_get_random_data_table(random_DATA_table, tmp_path_factory):
    cache = tmp_path_factory.mktemp("temp")
    year, month, table, _ = random_DATA_table
    get_and_unzip_table_csv(year, month, "DATA", table, cache)
    filename = Path(_construct_filename(year, month, table)).stem
    assert Path(cache, filename + ".CSV").exists()


def test_get_random_predisp_table(random_PREDISP_ALL_DATA_table, tmp_path_factory):
    cache = tmp_path_factory.mktemp("temp")
    year, month, table, _ = random_PREDISP_ALL_DATA_table
    get_and_unzip_table_csv(year, month, "PREDISP_ALL_DATA", table, cache)
    filename = Path(_construct_filename(year, month, table)).stem
    assert Path(cache, filename + ".CSV").exists()


def test_get_random_p5min_table(random_P5MIN_ALL_DATA_table, tmp_path_factory):
    cache = tmp_path_factory.mktemp("temp")
    year, month, table, _ = random_P5MIN_ALL_DATA_table
    get_and_unzip_table_csv(year, month, "P5MIN_ALL_DATA", table, cache)
    filename = Path(_construct_filename(year, month, table)).stem
    assert Path(cache, filename + ".CSV").exists()


def test_catch_invalid_year(tmp_path_factory):
    cache = tmp_path_factory.mktemp("temp")
    with pytest.raises(ValueError):
        get_and_unzip_table_csv(1999, 1, "DATA", "DISPATCHREGIONSUM", cache)


def test_catch_invalid_datadir(tmp_path_factory):
    cache = tmp_path_factory.mktemp("temp")
    with pytest.raises(ValueError):
        get_and_unzip_table_csv(2022, 1, "FAKE_DATA", "DISPATCHREGIONSUM", cache)


def test_catch_invalid_table(tmp_path_factory):
    cache = tmp_path_factory.mktemp("temp")
    with pytest.raises(ValueError):
        get_and_unzip_table_csv(2022, 1, "DATA", "SILLY_TABLE", cache)
