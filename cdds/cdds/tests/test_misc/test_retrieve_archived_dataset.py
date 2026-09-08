# (C) British Crown Copyright 2026, Met Office.
# Please see LICENSE.md for license details.
import io
import json
from contextlib import redirect_stdout
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
_CMIP6_FULL_ID = f"{_CMIP6_BASE_ID}.{_CMIP6_VERSION}"
_CMIP6_FILE_PATH = (
    "moose:/adhoc/projects/cdds/production/"
    "CMIP6/CMIP/MOHC/UKESM1-0-LL/piControl/r1i1p1f2/Amon/tas/gn/"
    "available/v20200828/tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_185001-194912.nc"
)
_CMIP6_FILES = [
    {
        "filesize": "123456",
        "filename": "tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_185001-194912.nc",
        "mass_path": _CMIP6_FILE_PATH,
        "checksum": "abc123",
    }
]

_SAMPLE_XML = """\
<nodes>
  <node kind="F" url="moose:/adhoc/projects/cdds/production/CMIP6/CMIP/MOHC/UKESM1-0-LL/piControl/r1i1p1f2/Amon/tas/gn/available/v20200828/tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_185001-194912.nc">
    <size>123456</size>
    <checksum><value>abc123</value></checksum>
  </node>
  <node kind="D" url="moose:/adhoc/projects/cdds/production/CMIP6/CMIP/MOHC/UKESM1-0-LL/piControl/r1i1p1f2/Amon/tas/gn/available/v20200828">
  </node>
</nodes>"""

_MODULE = "cdds.misc.retrieve_archived_dataset"


class TestListMassFilesWithChecksums:
    @patch(f"{_MODULE}.run_mass_command", return_value=_SAMPLE_XML)
    def test_parses_file_nodes(self, _mock):
        result = list_mass_files_with_checksums(
            "moose:/adhoc/projects/cdds/production/CMIP6/CMIP/MOHC/UKESM1-0-LL/piControl/r1i1p1f2/Amon/tas/gn",
            _MASS_ROOT,
        )
        assert len(result) == 1
        assert result[0]["checksum"] == "md5:abc123"
        assert result[0]["filesize"] == "123456"
        assert result[0]["filename"] == "tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_185001-194912.nc"


def _make_file(size_bytes, name="file.nc"):
    return {"filesize": str(size_bytes), "mass_path": f"moose:/path/available/v20200828/{name}"}


class TestChunkFiles:
    @pytest.mark.parametrize(
        "sizes,chunk_size,expected_chunk_count",
        [
            ([100, 200], 1000, 1),
            ([600, 600], 1000, 2),
        ],
    )
    def test_chunking_by_size(self, sizes, chunk_size, expected_chunk_count):
        files = [_make_file(size, f"file{i}.nc") for i, size in enumerate(sizes)]
        result = chunk_files(files, chunk_size)
        assert len(result) == expected_chunk_count

    def test_raises_if_file_exceeds_chunk_size(self):
        files = [_make_file(2000)]
        with pytest.raises(ValueError):
            chunk_files(files, 1000)


def _make_chunk(filename="tas.nc"):
    return [{"mass_path": f"moose:/path/available/v20200828/{filename}", "filesize": "100", "checksum": "abc"}]


class TestTransferFiles:
    @pytest.mark.parametrize("dry_run,expect_n_flag", [(True, True), (False, False)])
    @patch(f"{_MODULE}.transfer_files_to_final_dir")
    @patch(f"{_MODULE}.run_mass_command", return_value="")
    def test_moo_get_n_flag_matches_dry_run(self, mock_run, _mock_transfer, tmp_path: Path, dry_run, expect_n_flag):
        transfer_files([_make_chunk()], tmp_path, dry_run=dry_run)
        cmd = mock_run.call_args[0][0]
        assert ("-n" in cmd) == expect_n_flag


class TestTransferFilesToFinalDir:
    def test_dry_run_does_not_move_files(self, tmp_path: Path):
        tmpdir = tmp_path / "tmp"
        output_dir = tmp_path / "output"
        tmpdir.mkdir()
        output_dir.mkdir()
        src = tmpdir / "tas.nc"
        src.touch()
        chunk = [{"mass_path": "moose:/path/available/v20200828/tas.nc"}]
        with patch(f"{_MODULE}.TMPDIR", str(tmpdir)):
            transfer_files_to_final_dir(chunk, output_dir, dry_run=True)
        assert src.exists()
        assert not (output_dir / "tas.nc").exists()

    def test_moves_file_to_output_dir(self, tmp_path: Path):
        tmpdir = tmp_path / "tmp"
        output_dir = tmp_path / "output"
        tmpdir.mkdir()
        output_dir.mkdir()
        src = tmpdir / "tas.nc"
        src.touch()
        chunk = [{"mass_path": "moose:/path/available/v20200828/tas.nc"}]
        with patch(f"{_MODULE}.TMPDIR", str(tmpdir)):
            transfer_files_to_final_dir(chunk, output_dir, dry_run=False)
        assert not src.exists()
        assert (output_dir / "tas.nc").exists()


class TestParseDatasetId:
    @pytest.mark.parametrize(
        "dataset_id,expected_base,expected_version",
        [
            (_CMIP6_FULL_ID, _CMIP6_BASE_ID, _CMIP6_VERSION),
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

    @pytest.mark.parametrize(
        "failure,expected_exit_code",
        [
            (MassFailure.USER_ERROR, 2),
            (MassFailure.SYSTEM_ERROR, 3),
        ],
    )
    def test_exit_code_for_failure(self, failure, expected_exit_code):
        assert mass_error_exit_code(self._make_error(failure)) == expected_exit_code


class TestQueryFilesByVersion:
    @patch(f"{_MODULE}.list_mass_files_with_checksums", return_value=_CMIP6_FILES)
    def test_success_returns_files_and_mass_path(self, _mock):
        result = query_files_by_version(_CMIP6_FULL_ID, _MASS_ROOT)
        assert isinstance(result, tuple)
        files, mass_path = result
        assert len(files) == 1
        assert _CMIP6_BASE_ID.replace(".", "/") in mass_path

    @patch(f"{_MODULE}.list_mass_files_with_checksums", side_effect=FileNotExistMassError(["moo", "ls"]))
    def test_file_not_exist_error_returns_1(self, _mock):
        assert query_files_by_version(_CMIP6_FULL_ID, _MASS_ROOT) == 1

    @patch(f"{_MODULE}.list_mass_files_with_checksums", return_value=[
        {"mass_path": "moose:/path/available/v20190101/tas.nc", "filesize": "1"}
    ])
    def test_wrong_version_returns_1(self, _mock, caplog):
        assert query_files_by_version(_CMIP6_FULL_ID, _MASS_ROOT) == 1
        assert "No versioned files found in MASS" in caplog.text


class TestRunLsAction:
    @patch(f"{_MODULE}.query_files_by_version", return_value=(_CMIP6_FILES, _MASS_ROOT))
    def test_success_returns_0_and_prints_json(self, _mock):
        buf = io.StringIO()  # Captures stdout so the printed JSON can be inspected.
        with redirect_stdout(buf):
            result = run_ls_action(_CMIP6_FULL_ID, _MASS_ROOT)
        assert result == 0
        payload = json.loads(buf.getvalue())
        assert payload["dataset_id"] == _CMIP6_FULL_ID
        assert len(payload["files"]) == 1


class TestRunGetAction:
    @patch(f"{_MODULE}.transfer_files")
    @patch(f"{_MODULE}.create_output_dir")
    @patch(f"{_MODULE}.query_files_by_version")
    def test_success_returns_0(self, mock_fetch, mock_create_dir, _mock_transfer, tmp_path: Path):
        mock_fetch.return_value = (_CMIP6_FILES, _MASS_ROOT)
        mock_create_dir.return_value = tmp_path
        result = run_get_action(_CMIP6_FULL_ID, _MASS_ROOT, str(tmp_path), True, 100, False)
        assert result == 0

    @patch(f"{_MODULE}.query_files_by_version")
    def test_invalid_source_filepath_missing_status_returns_3(self, mock_fetch, tmp_path: Path, caplog):
        invalid_files = [{"mass_path": "moose:/adhoc/projects/cdds/production/bad/path/file.nc"}]
        mock_fetch.return_value = (invalid_files, _MASS_ROOT)
        result = run_get_action(_CMIP6_FULL_ID, _MASS_ROOT, str(tmp_path), True, 100, False)
        assert result == 3
        assert "'available' or 'embargoed' not found in source filepath" in caplog.text
