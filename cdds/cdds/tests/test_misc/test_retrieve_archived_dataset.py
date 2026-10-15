# (C) British Crown Copyright 2026, Met Office.
# Please see LICENSE.md for license details.
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from cdds.common.mass_exception import FileNotExistMassError, MassError, MassFailure
from cdds.misc.retrieve_archived_dataset import (
    chunk_files,
    query_files_by_version,
    list_mass_files_with_checksums,
    mass_error_exit_code,
    parse_dataset_id,
    run_get_action,
    run_ls_action,
    transfer_files,
    transfer_files_to_final_dir,
)

_MASS_ROOT = "moose:/adhoc/projects/cdds/production/"
_CMIP6_BASE_ID = "CMIP6.CMIP.MOHC.UKESM1-0-LL.piControl.r1i1p1f2.Amon.tas.gn"
_CMIP6_VERSION = "v20200828"
_CMIP6_FULL_DATASET_ID = f"{_CMIP6_BASE_ID}.{_CMIP6_VERSION}"
_CMIP6_FILE_PATH = (
    "moose:/adhoc/projects/cdds/production/"
    "CMIP6/CMIP/MOHC/UKESM1-0-LL/piControl/r1i1p1f2/Amon/tas/gn/"
    "available/v20200828/tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_185001-194912.nc"
)
_CMIP6_FILE_METADATA = [
    {
        "filesize": "123456",
        "filename": "tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_185001-194912.nc",
        "mass_path": _CMIP6_FILE_PATH,
        "checksum": "abc123",
    }
]

_SAMPLE_XML = f"""\
<nodes>
  <node kind="F" url="{_CMIP6_FILE_PATH}">
    <size>123456</size>
    <checksum><value>abc123</value></checksum>
  </node>
  <node kind="D" url="{_MASS_ROOT}CMIP6/CMIP/MOHC/UKESM1-0-LL/piControl/r1i1p1f2/Amon/tas/gn/available/v20200828">
  </node>
</nodes>"""

_MODULE = "cdds.misc.retrieve_archived_dataset"


class TestRunGetAction:
    @patch(f"{_MODULE}.run_mass_command", return_value=_SAMPLE_XML)
    def test_dry_run_success_returns_0(self, mock_run_mass_command, tmp_path):
        result = run_get_action(
            _CMIP6_FULL_DATASET_ID, _MASS_ROOT, tmp_path, create_directories=True, chunk_size=100, dry_run=True
        )
        assert result == 0
        assert mock_run_mass_command.call_count == 2
        # 1st: moo ls -Rlxm, 2nd: moo get -I -n (ls command is used to build paths the get uses for retrieval/dry run).

    @patch(f"{_MODULE}.query_files_by_version")
    def test_invalid_source_filepath_missing_status_returns_3(self, mock_query_files_by_version, tmp_path, caplog):
        invalid_files = [{"mass_path": "moose:/adhoc/projects/cdds/production/bad/path/file.nc"}]
        mock_query_files_by_version.return_value = (invalid_files, _MASS_ROOT)
        result = run_get_action(_CMIP6_FULL_DATASET_ID, _MASS_ROOT, tmp_path, True, 100, False)
        assert result == 3
        assert "'available' or 'embargoed' not found in source filepath" in caplog.text


class TestRunLsAction:
    @patch(f"{_MODULE}.run_mass_command", return_value=_SAMPLE_XML)
    def test_success_returns_0_and_prints_json(self, _mock_run_mass_command, capsys):
        result = run_ls_action(_CMIP6_FULL_DATASET_ID, _MASS_ROOT)
        assert result == 0
        captured = capsys.readouterr()
        payload = json.loads(captured.out)
        assert payload["dataset_id"] == _CMIP6_FULL_DATASET_ID
        assert len(payload["files"]) == 1
        assert payload["files"][0]["checksum"] == "md5:abc123"


class TestQueryFilesByVersion:
    @patch(f"{_MODULE}.list_mass_files_with_checksums", return_value=_CMIP6_FILE_METADATA)
    def test_success_returns_files_and_mass_path(self, _mock_list_mass_files_with_checksums):
        result = query_files_by_version(_CMIP6_FULL_DATASET_ID, _MASS_ROOT)
        assert isinstance(result, tuple)
        files, mass_path = result
        assert len(files) == 1
        expected_path = (
            "moose:/adhoc/projects/cdds/production/"
            "CMIP6/CMIP/MOHC/UKESM1-0-LL/piControl/r1i1p1f2/Amon/tas/gn"
        )
        assert mass_path == expected_path

    @patch(f"{_MODULE}.list_mass_files_with_checksums", side_effect=FileNotExistMassError(["moo", "ls"]))
    def test_file_not_exist_error_returns_1(self, _mock_list_mass_files_with_checksums):
        assert query_files_by_version(_CMIP6_FULL_DATASET_ID, _MASS_ROOT) == 1

    @patch(f"{_MODULE}.list_mass_files_with_checksums", return_value=[
        {"mass_path": "moose:/path/available/v20190101/tas.nc", "filesize": "1"}
    ])
    def test_wrong_version_returns_1(self, _mock_list_mass_files_with_checksums, caplog):
        # Checks version != embargoed or available returns 1 and logs accordingly
        assert query_files_by_version(_CMIP6_FULL_DATASET_ID, _MASS_ROOT) == 1
        assert "No versioned files found in MASS" in caplog.text


class TestTransferFiles:
    @pytest.mark.parametrize("dry_run,expect_n_flag", [(True, True), (False, False)])
    # Mock final transfer to avoid FileNotFoundError when dry_run=False since mocked MASS downloads no files.
    @patch(f"{_MODULE}.transfer_files_to_final_dir")
    @patch(f"{_MODULE}.run_mass_command", return_value="")
    def test_moo_get_n_flag_matches_dry_run(
        self, mock_run_mass_command, _mock_transfer_files_to_final_dir, tmp_path, dry_run, expect_n_flag
    ):
        transfer_files([_CMIP6_FILE_METADATA], tmp_path, dry_run=dry_run)
        cmd = mock_run_mass_command.call_args[0][0]
        assert ("-n" in cmd) == expect_n_flag


class TestTransferFilesToFinalDir:
    # Patches TMPDIR to isolate file operations inside pytest tmp_path as module also initialises $TMPDIR.
    def test_dry_run_does_not_move_files(self, tmp_path):
        tmpdir = tmp_path / "tmp"
        output_dir = tmp_path / "output"
        tmpdir.mkdir()
        output_dir.mkdir()
        staged_file = tmpdir / "tas.nc"
        staged_file.touch()
        chunk = [{"mass_path": "moose:/path/available/v20200828/tas.nc"}]
        with patch(f"{_MODULE}.TMPDIR", tmpdir):
            transfer_files_to_final_dir(chunk, output_dir, dry_run=True)
        assert staged_file.exists()
        assert not (output_dir / "tas.nc").exists()

    def test_moves_file_to_output_dir(self, tmp_path):
        tmpdir = tmp_path / "tmp"
        output_dir = tmp_path / "output"
        tmpdir.mkdir()
        output_dir.mkdir()
        staged_file = tmpdir / "tas.nc"
        staged_file.touch()
        chunk = [{"mass_path": "moose:/path/available/v20200828/tas.nc"}]
        with patch(f"{_MODULE}.TMPDIR", tmpdir):
            transfer_files_to_final_dir(chunk, output_dir, dry_run=False)
        assert not staged_file.exists()
        assert (output_dir / "tas.nc").exists()


class TestListMassFilesWithChecksums:
    def test_parses_file_nodes(self):
        with patch(f"{_MODULE}.run_mass_command", return_value=_SAMPLE_XML):
            result = list_mass_files_with_checksums(
                "moose:/adhoc/projects/cdds/production/CMIP6/CMIP/MOHC/UKESM1-0-LL/piControl/r1i1p1f2/Amon/tas/gn"
            )
        assert len(result) == 1
        assert result[0]["checksum"] == "md5:abc123"
        assert result[0]["filesize"] == "123456"
        assert result[0]["filename"] == "tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_185001-194912.nc"


class TestChunkFiles:
    def test_combines_files_under_chunk_size(self):
        files = [
            {"filesize": "100", "mass_path": "file0.nc"},
            {"filesize": "200", "mass_path": "file1.nc"},
        ]
        result = chunk_files(files, 1000)
        assert len(result) == 1

    def test_splits_files_exceeding_chunk_size(self):
        files = [
            {"filesize": "600", "mass_path": "file0.nc"},
            {"filesize": "600", "mass_path": "file1.nc"},
        ]
        result = chunk_files(files, 1000)
        assert len(result) == 2

    def test_raises_if_file_exceeds_chunk_size(self):
        files = [{"filesize": "2000", "mass_path": "file0.nc"}]
        with pytest.raises(ValueError):
            chunk_files(files, 1000)


class TestParseDatasetId:
    # Tests both CMIP6 and CMIP7 format
    @pytest.mark.parametrize(
        "dataset_id,expected_base,expected_version",
        [
            (
                "CMIP6.CMIP.MOHC.UKESM1-0-LL.piControl.r1i1p1f2.Amon.tas.gn.v20200828",
                "CMIP6.CMIP.MOHC.UKESM1-0-LL.piControl.r1i1p1f2.Amon.tas.gn",
                "v20200828",
            ),
            (
                "MIP-DRS7.CMIP7.CMIP.UKNCSP.UKESM1-3-LL.esm-piControl.r1i1p1f1.glb.mon.vo.tavg-ol-hxy-sea.g124.v20260818",
                "MIP-DRS7.CMIP7.CMIP.UKNCSP.UKESM1-3-LL.esm-piControl.r1i1p1f1.glb.mon.vo.tavg-ol-hxy-sea.g124",
                "v20260818",
            ),
        ],
    )
    def test_parse_dataset_id(self, dataset_id, expected_base, expected_version):
        base, version = parse_dataset_id(dataset_id)
        assert base == expected_base
        assert version == expected_version


class TestMassErrorExitCode:
    def _make_error(self, failure):
        return MassError(failure, ["moo", "ls"])

    # Note: Testing of exit code "1" is in TestQueryFilesByVersion
    @pytest.mark.parametrize(
        "failure,expected_exit_code",
        [
            (MassFailure.USER_ERROR, 2),
            (MassFailure.SYSTEM_ERROR, 3),
        ],
    )
    def test_exit_code_for_failure(self, failure, expected_exit_code):
        assert mass_error_exit_code(self._make_error(failure)) == expected_exit_code
