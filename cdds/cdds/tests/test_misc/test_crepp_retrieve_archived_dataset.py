# (C) British Crown Copyright 2026, Met Office.
# Please see LICENSE.md for license details.
import io
import json
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import pytest

from cdds.common.mass_exception import FileNotExistMassError, MassError, MassFailure
from cdds.misc.crepp_retrieve_archived_dataset import (
    chunk_files,
    fetch_versioned_files,
    group_files_by_folder,
    list_mass_files_with_checksums,
    mass_error_exit_code,
    parse_args,
    parse_dataset_id,
    parse_mass_file_path,
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
_CMIP6_FILE_LIST = {
    _CMIP6_BASE_ID: {
        "status": "available",
        "version": "v20200828",
        "files": [
            {
                "filesize": "123456",
                "filename": "tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_185001-194912.nc",
                "mass_path": _CMIP6_FILE_PATH,
                "checksum": "abc123",
            }
        ],
    }
}

_SAMPLE_XML = """\
<nodes>
  <node kind="F" url="moose:/adhoc/projects/cdds/production/CMIP6/CMIP/MOHC/UKESM1-0-LL/piControl/r1i1p1f2/Amon/tas/gn/available/v20200828/tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_185001-194912.nc">
    <size>123456</size>
    <checksum><value>abc123</value></checksum>
  </node>
  <node kind="D" url="moose:/adhoc/projects/cdds/production/CMIP6/CMIP/MOHC/UKESM1-0-LL/piControl/r1i1p1f2/Amon/tas/gn/available/v20200828">
  </node>
</nodes>"""

_MODULE = "cdds.misc.crepp_retrieve_archived_dataset"


class TestParseMassFilePath:
    def test_cmip6_available(self):
        dataset_id, status, version, filename = parse_mass_file_path(_CMIP6_FILE_PATH, _MASS_ROOT)
        assert dataset_id == _CMIP6_BASE_ID
        assert status == "available"
        assert version == "v20200828"
        assert filename == "tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_185001-194912.nc"

    def test_embargoed_status(self):
        embargoed_path = _CMIP6_FILE_PATH.replace("available", "embargoed")
        _, status, _, _ = parse_mass_file_path(embargoed_path, _MASS_ROOT)
        assert status == "embargoed"

    def test_cmip7_path_has_different_facet_count(self):
        cmip7_path = (
            "moose:/adhoc/projects/cdds/production/"
            "MIP-DRS7/CMIP7/CMIP/UKNCSP/UKESM1-3-LL/esm-piControl/r1i1p1f1/glb/mon/vo/"
            "tavg-ol-hxy-sea/g124/available/v20260818/vo_mon.nc"
        )
        dataset_id, status, version, filename = parse_mass_file_path(cmip7_path, _MASS_ROOT)
        assert dataset_id == (
            "MIP-DRS7.CMIP7.CMIP.UKNCSP.UKESM1-3-LL.esm-piControl.r1i1p1f1.glb.mon.vo.tavg-ol-hxy-sea.g124"
        )
        assert status == "available"
        assert version == "v20260818"
        assert filename == "vo_mon.nc"


class TestListMassFilesWithChecksums:
    def test_dry_run_returns_empty_dict(self):
        result = list_mass_files_with_checksums("moose:/some/path", _MASS_ROOT, dry_run=True)
        assert result == {}

    @patch(f"{_MODULE}.run_mass_command", return_value=_SAMPLE_XML)
    def test_parses_file_nodes(self, _mock):
        result = list_mass_files_with_checksums(
            "moose:/adhoc/projects/cdds/production/CMIP6/CMIP/MOHC/UKESM1-0-LL/piControl/r1i1p1f2/Amon/tas/gn",
            _MASS_ROOT,
            dry_run=False,
        )
        assert _CMIP6_BASE_ID in result
        files = result[_CMIP6_BASE_ID]["files"]
        assert len(files) == 1
        assert files[0]["checksum"] == "md5:abc123"
        assert files[0]["filesize"] == "123456"

    @patch(f"{_MODULE}.run_mass_command", return_value="")
    def test_empty_output_returns_empty_dict(self, _mock):
        result = list_mass_files_with_checksums("moose:/some/path", _MASS_ROOT, dry_run=False)
        assert result == {}


class TestParseArgs:
    @pytest.mark.parametrize(
        "argv,expected",
        [
            (["prog", "ls", _CMIP6_FULL_ID], {"action": "ls", "dataset_id": _CMIP6_FULL_ID}),
            (
                ["prog", "get", _CMIP6_FULL_ID, "/some/dest"],
                {"action": "get", "dataset_id": _CMIP6_FULL_ID, "destination": "/some/dest"},
            ),
        ],
    )
    def test_action_and_dataset_id(self, argv, expected):
        with patch("sys.argv", argv):
            args = parse_args()
        for key, value in expected.items():
            assert getattr(args, key) == value

    def test_defaults_and_flags(self):
        with patch("sys.argv", ["prog", "ls", _CMIP6_FULL_ID, "--dry-run", "--create-directories-false"]):
            args = parse_args()
        assert args.dry_run
        assert not args.create_directories
        assert args.mass_root == _MASS_ROOT


class TestGroupFilesByFolder:
    @pytest.mark.parametrize(
        "mass_paths,expected_folder_count",
        [
            (
                [
                    "moose:/path/available/v20200828/file1.nc",
                    "moose:/path/available/v20200828/file2.nc",
                ],
                1,
            ),
            (
                [
                    "moose:/path/available/v20200828/file1.nc",
                    "moose:/path/embargoed/v20200829/file2.nc",
                ],
                2,
            ),
        ],
    )
    def test_groups_by_parent_folder(self, mass_paths, expected_folder_count):
        files = [{"mass_path": path} for path in mass_paths]
        result = group_files_by_folder(files)
        assert len(result) == expected_folder_count

    def test_raises_if_no_available_or_embargoed(self):
        files = [{"mass_path": "moose:/path/other/v20200828/file.nc"}]
        with pytest.raises(ValueError):
            group_files_by_folder(files)


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

    @patch(f"{_MODULE}.transfer_files_to_final_dir")
    @patch(f"{_MODULE}.run_mass_command", return_value="")
    def test_calls_transfer_to_final_dir_once_per_chunk(self, _mock_run, mock_transfer, tmp_path: Path):
        chunks = [_make_chunk("a.nc"), _make_chunk("b.nc")]
        transfer_files(chunks, tmp_path, dry_run=False)
        assert mock_transfer.call_count == 2


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
    def test_cmip6_dataset_id(self):
        base, version = parse_dataset_id(_CMIP6_FULL_ID)
        assert base == _CMIP6_BASE_ID
        assert version == _CMIP6_VERSION

    def test_cmip7_dataset_id_has_different_facet_count(self):
        cmip7_id = (
            "MIP-DRS7.CMIP7.CMIP.UKNCSP.UKESM1-3-LL.esm-piControl"
            ".r1i1p1f1.glb.mon.vo.tavg-ol-hxy-sea.g124.v20260818"
        )
        base, version = parse_dataset_id(cmip7_id)
        assert base == "MIP-DRS7.CMIP7.CMIP.UKNCSP.UKESM1-3-LL.esm-piControl.r1i1p1f1.glb.mon.vo.tavg-ol-hxy-sea.g124"
        assert version == "v20260818"


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


class TestFetchVersionedFiles:
    @patch(f"{_MODULE}.list_mass_files_with_checksums", return_value=_CMIP6_FILE_LIST)
    def test_success_returns_files_and_mass_path(self, _mock):
        result = fetch_versioned_files(_CMIP6_FULL_ID, _MASS_ROOT)
        assert isinstance(result, tuple)
        files, mass_path = result
        assert len(files) == 1
        assert _CMIP6_BASE_ID.replace(".", "/") in mass_path

    @patch(f"{_MODULE}.list_mass_files_with_checksums", side_effect=FileNotExistMassError(["moo", "ls"]))
    def test_file_not_exist_error_returns_1(self, _mock):
        assert fetch_versioned_files(_CMIP6_FULL_ID, _MASS_ROOT) == 1

    @patch(f"{_MODULE}.list_mass_files_with_checksums", return_value={})
    def test_dataset_absent_from_listing_returns_1(self, _mock):
        assert fetch_versioned_files(_CMIP6_FULL_ID, _MASS_ROOT) == 1

    @patch(f"{_MODULE}.list_mass_files_with_checksums", return_value={
        _CMIP6_BASE_ID: {
            "status": "available",
            "version": "v20190101",
            "files": [{"mass_path": "moose:/path/available/v20190101/tas.nc", "filesize": "1"}],
        }
    })
    def test_wrong_version_returns_1(self, _mock):
        assert fetch_versioned_files(_CMIP6_FULL_ID, _MASS_ROOT) == 1

    @pytest.mark.parametrize(
        "failure,expected_code",
        [
            (MassFailure.USER_ERROR, 2),
            (MassFailure.SYSTEM_ERROR, 3),
        ],
    )
    def test_mass_error_returns_mapped_exit_code(self, failure, expected_code):
        with patch(
            f"{_MODULE}.list_mass_files_with_checksums",
            side_effect=MassError(failure, ["moo", "ls"]),
        ):
            assert fetch_versioned_files(_CMIP6_FULL_ID, _MASS_ROOT) == expected_code


class TestRunLsAction:
    @patch(f"{_MODULE}.fetch_versioned_files", return_value=(_CMIP6_FILE_LIST[_CMIP6_BASE_ID]["files"], _MASS_ROOT))
    def test_success_returns_0_and_prints_json(self, _mock):
        buf = io.StringIO()
        with redirect_stdout(buf):
            result = run_ls_action(_CMIP6_FULL_ID, _MASS_ROOT)
        assert result == 0
        payload = json.loads(buf.getvalue())
        assert payload["dataset_id"] == _CMIP6_FULL_ID
        assert len(payload["files"]) == 1

    @patch(f"{_MODULE}.fetch_versioned_files", return_value=2)
    def test_error_code_passthrough(self, _mock):
        assert run_ls_action(_CMIP6_FULL_ID, _MASS_ROOT) == 2


class TestRunGetAction:
    @patch(f"{_MODULE}.transfer_files")
    @patch(f"{_MODULE}.create_output_dir")
    @patch(f"{_MODULE}.fetch_versioned_files")
    def test_success_returns_0(self, mock_fetch, mock_create_dir, _mock_transfer, tmp_path: Path):
        mock_fetch.return_value = (_CMIP6_FILE_LIST[_CMIP6_BASE_ID]["files"], _MASS_ROOT)
        mock_create_dir.return_value = tmp_path
        result = run_get_action(_CMIP6_FULL_ID, _MASS_ROOT, str(tmp_path), True, 100, False)
        assert result == 0

    @patch(f"{_MODULE}.fetch_versioned_files", return_value=2)
    def test_error_code_passthrough(self, _mock, tmp_path: Path):
        result = run_get_action(_CMIP6_FULL_ID, _MASS_ROOT, str(tmp_path), True, 100, False)
        assert result == 2

    @patch(f"{_MODULE}.transfer_files", side_effect=RuntimeError("unexpected"))
    @patch(f"{_MODULE}.create_output_dir")
    @patch(f"{_MODULE}.fetch_versioned_files")
    def test_generic_exception_returns_3(self, mock_fetch, mock_create_dir, _mock_transfer, tmp_path: Path):
        mock_fetch.return_value = (_CMIP6_FILE_LIST[_CMIP6_BASE_ID]["files"], _MASS_ROOT)
        mock_create_dir.return_value = tmp_path
        result = run_get_action(_CMIP6_FULL_ID, _MASS_ROOT, str(tmp_path), True, 100, False)
        assert result == 3
