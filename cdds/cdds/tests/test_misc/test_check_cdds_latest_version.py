# (C) British Crown Copyright 2026, Met Office.
# Please see LICENSE.md for license details.

from pathlib import Path

from cdds.misc.check_cdds_latest_version import main_check_latest_version, retrieve_latest_version


def test_retrieve_latest_version_uses_numeric_order_and_ignores_other_naming(tmp_path: Path) -> None:
    for environment in ("cdds-4.0.2", "cdds-4.0.10", "cdds-4.1.0rc1", "cdds-4.2_dev-1"):
        (tmp_path / environment).mkdir()

    assert retrieve_latest_version(tmp_path) == (4, 0, 10)


def test_main_prints_latest_version_activated(tmp_path: Path, capsys) -> None:
    (tmp_path / "cdds-4.0.2").mkdir()
    (tmp_path / "cdds-4.0.10").mkdir()

    assert main_check_latest_version("4.0.10", tmp_path) == 0
    assert capsys.readouterr().out == "Latest version of CDDS activated.\n"


def test_main_recommends_upgrade_for_older_version(tmp_path: Path, capsys) -> None:
    (tmp_path / "cdds-4.0.5").mkdir()
    (tmp_path / "cdds-4.0.10").mkdir()

    assert main_check_latest_version("4.0.5", tmp_path) == 0
    assert "upgrading is recommended" in capsys.readouterr().out


def test_main_is_silent_when_requested_version_is_newer_than_latest(tmp_path: Path, capsys) -> None:
    # If the requested version is newer than the latest available version,
    # a conda error will show, which i think is descriptive enough.
    (tmp_path / "cdds-4.0.10").mkdir()

    assert main_check_latest_version("5.0.0", tmp_path) == 0
    assert capsys.readouterr().out == ""


def test_main_warns_for_non_release_version(tmp_path: Path, capsys) -> None:
    (tmp_path / "cdds-4.0.10").mkdir()

    assert main_check_latest_version("3.0.5rc1", tmp_path) == 0
    assert capsys.readouterr().out == (
        "Unexpected version selected. Double check 3.0.5rc1 was the version you meant to activate.\n"
    )
