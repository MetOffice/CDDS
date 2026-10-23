# (C) British Crown Copyright 2026, Met Office.
# Please see LICENSE.md for license details.

import os
import subprocess
import sys
from pathlib import Path

from cdds.misc.check_cdds_latest_version import check_latest_version, retrieve_latest_version


def test_retrieve_latest_version_uses_numeric_order_and_ignores_other_naming(tmp_path: Path) -> None:
    for environment in ("cdds-4.0.2", "cdds-4.0.10", "cdds-4.1.0rc1", "cdds-4.2_dev-1"):
        (tmp_path / environment).mkdir()

    assert retrieve_latest_version(tmp_path) == (4, 0, 10)


def test_main_prints_latest_version_activated(tmp_path: Path, capsys) -> None:
    (tmp_path / "cdds-4.0.2").mkdir()
    (tmp_path / "cdds-4.0.10").mkdir()

    assert check_latest_version("4.0.10", tmp_path) == 0
    assert capsys.readouterr().out == "Latest version of CDDS activated (v4.0.10).\n"


def test_main_recommends_upgrade_for_older_version(tmp_path: Path, capsys) -> None:
    (tmp_path / "cdds-4.0.5").mkdir()
    (tmp_path / "cdds-4.0.10").mkdir()

    assert check_latest_version("4.0.5", tmp_path) == 0
    assert "upgrading is recommended" in capsys.readouterr().out


def test_main_is_silent_when_requested_version_is_newer_than_latest(tmp_path: Path, capsys) -> None:
    # If the requested version is newer than the latest available version,
    # a conda error will show, which i think is descriptive enough.
    (tmp_path / "cdds-4.0.10").mkdir()

    assert check_latest_version("5.0.0", tmp_path) == 0
    assert capsys.readouterr().out == ""


def test_main_warns_for_non_release_version(tmp_path: Path, capsys) -> None:
    (tmp_path / "cdds-4.0.10").mkdir()

    assert check_latest_version("3.0.5rc1", tmp_path) == 0
    assert capsys.readouterr().out == (
        "Unexpected version selected. Double check 3.0.5rc1 was the version you meant to activate.\n"
    )


def test_command_launcher_uses_active_environment_without_arguments(tmp_path: Path) -> None:
    environments_directory = tmp_path / "conda_environments"
    active_environment = environments_directory / "cdds-4.0.2"
    active_environment.mkdir(parents=True)
    (environments_directory / "cdds-4.0.10").mkdir()

    package_root = Path(__file__).parents[3]
    launcher = package_root / "bin" / "cdds_check_latest_version"
    environment = os.environ.copy()
    environment["CONDA_PREFIX"] = str(active_environment)
    environment["PYTHONPATH"] = str(package_root)

    result = subprocess.run(
        [sys.executable, str(launcher)],
        capture_output=True,
        check=False,
        env=environment,
        text=True,
    )

    assert result.returncode == 0
    assert "The latest version of CDDS is 4.0.10." in result.stdout
    assert "using version 4.0.2" in result.stdout


def test_command_launcher_displays_help() -> None:
    package_root = Path(__file__).parents[3]
    launcher = package_root / "bin" / "cdds_check_latest_version"
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(package_root)

    result = subprocess.run(
        [sys.executable, str(launcher), "--help"],
        capture_output=True,
        check=False,
        env=environment,
        text=True,
    )

    assert result.returncode == 0
    assert "usage: cdds_check_latest_version" in result.stdout
    assert "Check whether the active CDDS environment is the latest version" in result.stdout
