# (C) British Crown Copyright 2026, Met Office.
# Please see LICENSE.md for license details.
import io
import json
import shutil
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import mkdtemp
from unittest.mock import patch

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
        "timestamp": "v20200828",
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


class TestParseMassFilePath(unittest.TestCase):
    def test_cmip6_available(self):
        dataset_id, status, version, filename = parse_mass_file_path(_CMIP6_FILE_PATH, _MASS_ROOT)
        self.assertEqual(dataset_id, _CMIP6_BASE_ID)
        self.assertEqual(status, "available")
        self.assertEqual(version, "v20200828")
        self.assertEqual(filename, "tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_185001-194912.nc")

    def test_embargoed_status(self):
        embargoed_path = _CMIP6_FILE_PATH.replace("available", "embargoed")
        _, status, _, _ = parse_mass_file_path(embargoed_path, _MASS_ROOT)
        self.assertEqual(status, "embargoed")

    def test_mass_root_trailing_slash_stripped(self):
        dataset_id, _, _, _ = parse_mass_file_path(_CMIP6_FILE_PATH, _MASS_ROOT.rstrip("/"))
        self.assertEqual(dataset_id, _CMIP6_BASE_ID)

    def test_cmip7_path(self):
        cmip7_path = (
            "moose:/adhoc/projects/cdds/production/"
            "MIP-DRS7/CMIP7/CMIP/UKNCSP/UKESM1-3-LL/esm-piControl/r1i1p1f1/glb/mon/vo/"
            "tavg-ol-hxy-sea/g124/available/v20260818/vo_mon.nc"
        )
        dataset_id, status, version, filename = parse_mass_file_path(cmip7_path, _MASS_ROOT)
        self.assertEqual(
            dataset_id,
            "MIP-DRS7.CMIP7.CMIP.UKNCSP.UKESM1-3-LL.esm-piControl.r1i1p1f1.glb.mon.vo.tavg-ol-hxy-sea.g124",
        )
        self.assertEqual(status, "available")
        self.assertEqual(version, "v20260818")
        self.assertEqual(filename, "vo_mon.nc")


class TestListMassFilesWithChecksums(unittest.TestCase):
    def test_dry_run_returns_empty_dict(self):
        result = list_mass_files_with_checksums("moose:/some/path", _MASS_ROOT, dry_run=True)
        self.assertEqual(result, {})

    @patch(f"{_MODULE}.run_mass_command", return_value=_SAMPLE_XML)
    def test_parses_file_nodes(self, _mock):
        result = list_mass_files_with_checksums(
            "moose:/adhoc/projects/cdds/production/CMIP6/CMIP/MOHC/UKESM1-0-LL/piControl/r1i1p1f2/Amon/tas/gn",
            _MASS_ROOT,
            dry_run=False,
        )
        self.assertIn(_CMIP6_BASE_ID, result)
        files = result[_CMIP6_BASE_ID]["files"]
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0]["checksum"], "md5:abc123")
        self.assertEqual(files[0]["filesize"], "123456")

    @patch(f"{_MODULE}.run_mass_command", return_value=_SAMPLE_XML)
    def test_directory_nodes_are_skipped(self, _mock):
        result = list_mass_files_with_checksums(
            "moose:/adhoc/projects/cdds/production/CMIP6/CMIP/MOHC/UKESM1-0-LL/piControl/r1i1p1f2/Amon/tas/gn",
            _MASS_ROOT,
            dry_run=False,
        )
        self.assertEqual(len(result[_CMIP6_BASE_ID]["files"]), 1)

    @patch(f"{_MODULE}.run_mass_command", return_value="")
    def test_empty_output_returns_empty_dict(self, _mock):
        result = list_mass_files_with_checksums("moose:/some/path", _MASS_ROOT, dry_run=False)
        self.assertEqual(result, {})


class TestParseArgs(unittest.TestCase):
    def test_ls_action(self):
        with patch("sys.argv", ["prog", "ls", _CMIP6_FULL_ID]):
            args = parse_args()
        self.assertEqual(args.action, "ls")
        self.assertEqual(args.dataset_id, _CMIP6_FULL_ID)

    def test_get_action_with_destination(self):
        with patch("sys.argv", ["prog", "get", _CMIP6_FULL_ID, "/some/dest"]):
            args = parse_args()
        self.assertEqual(args.action, "get")
        self.assertEqual(args.destination, "/some/dest")

    def test_dry_run_flag(self):
        with patch("sys.argv", ["prog", "ls", _CMIP6_FULL_ID, "--dry-run"]):
            args = parse_args()
        self.assertTrue(args.dry_run)

    def test_mass_root_default(self):
        with patch("sys.argv", ["prog", "ls", _CMIP6_FULL_ID]):
            args = parse_args()
        self.assertEqual(args.mass_root, _MASS_ROOT)

    def test_create_directories_false_flag(self):
        with patch("sys.argv", ["prog", "ls", _CMIP6_FULL_ID, "--create-directories-false"]):
            args = parse_args()
        self.assertFalse(args.create_directories)


class TestGroupFilesByFolder(unittest.TestCase):
    def test_groups_by_parent_folder(self):
        files = [
            {"mass_path": "moose:/path/available/v20200828/file1.nc"},
            {"mass_path": "moose:/path/available/v20200828/file2.nc"},
        ]
        result = group_files_by_folder(files)
        self.assertEqual(len(result), 1)
        self.assertIn("moose:/path/available/v20200828", result)
        self.assertEqual(len(result["moose:/path/available/v20200828"]), 2)

    def test_splits_across_multiple_folders(self):
        files = [
            {"mass_path": "moose:/path/available/v20200828/file1.nc"},
            {"mass_path": "moose:/path/embargoed/v20200829/file2.nc"},
        ]
        result = group_files_by_folder(files)
        self.assertEqual(len(result), 2)

    def test_raises_if_no_available_or_embargoed(self):
        files = [{"mass_path": "moose:/path/other/v20200828/file.nc"}]
        with self.assertRaises(ValueError):
            group_files_by_folder(files)


class TestChunkFiles(unittest.TestCase):
    def _make_file(self, size_bytes, name="file.nc"):
        return {"filesize": str(size_bytes), "mass_path": f"moose:/path/available/v20200828/{name}"}

    def test_all_files_fit_in_one_chunk(self):
        files = [self._make_file(100), self._make_file(200)]
        result = chunk_files(files, 1000)
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[0]), 2)

    def test_splits_into_multiple_chunks(self):
        files = [self._make_file(600, "a.nc"), self._make_file(600, "b.nc")]
        result = chunk_files(files, 1000)
        self.assertEqual(len(result), 2)

    def test_raises_if_file_exceeds_chunk_size(self):
        files = [self._make_file(2000)]
        with self.assertRaises(ValueError):
            chunk_files(files, 1000)

    def test_empty_input_returns_empty_list(self):
        result = chunk_files([], 1000)
        self.assertEqual(result, [])


class TestTransferFiles(unittest.TestCase):
    def setUp(self):
        self.output_dir = Path(mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.output_dir)

    def _make_chunk(self, filename="tas.nc"):
        return [{"mass_path": f"moose:/path/available/v20200828/{filename}", "filesize": "100", "checksum": "abc"}]

    @patch(f"{_MODULE}.transfer_files_to_final_dir")
    @patch(f"{_MODULE}.run_mass_command", return_value="")
    def test_dry_run_passes_n_flag_to_moo_get(self, mock_run, _mock_transfer):
        transfer_files([self._make_chunk()], self.output_dir, dry_run=True)
        cmd = mock_run.call_args[0][0]
        self.assertIn("-n", cmd)

    @patch(f"{_MODULE}.transfer_files_to_final_dir")
    @patch(f"{_MODULE}.run_mass_command", return_value="")
    def test_non_dry_run_omits_n_flag_from_moo_get(self, mock_run, _mock_transfer):
        transfer_files([self._make_chunk()], self.output_dir, dry_run=False)
        cmd = mock_run.call_args[0][0]
        self.assertNotIn("-n", cmd)

    @patch(f"{_MODULE}.transfer_files_to_final_dir")
    @patch(f"{_MODULE}.run_mass_command", return_value="")
    def test_calls_transfer_to_final_dir_once_per_chunk(self, _mock_run, mock_transfer):
        chunks = [self._make_chunk("a.nc"), self._make_chunk("b.nc")]
        transfer_files(chunks, self.output_dir, dry_run=False)
        self.assertEqual(mock_transfer.call_count, 2)


class TestTransferFilesToFinalDir(unittest.TestCase):
    def setUp(self):
        self.tmpdir = mkdtemp()
        self.output_dir = Path(mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        shutil.rmtree(self.output_dir, ignore_errors=True)

    def test_dry_run_does_not_move_files(self):
        src = Path(self.tmpdir) / "tas.nc"
        src.touch()
        chunk = [{"mass_path": "moose:/path/available/v20200828/tas.nc"}]
        with patch(f"{_MODULE}.TMPDIR", self.tmpdir):
            transfer_files_to_final_dir(chunk, self.output_dir, dry_run=True)
        self.assertTrue(src.exists())
        self.assertFalse((self.output_dir / "tas.nc").exists())

    def test_moves_file_to_output_dir(self):
        src = Path(self.tmpdir) / "tas.nc"
        src.touch()
        chunk = [{"mass_path": "moose:/path/available/v20200828/tas.nc"}]
        with patch(f"{_MODULE}.TMPDIR", self.tmpdir):
            transfer_files_to_final_dir(chunk, self.output_dir, dry_run=False)
        self.assertFalse(src.exists())
        self.assertTrue((self.output_dir / "tas.nc").exists())


class TestParseDatasetId(unittest.TestCase):
    def test_cmip6_dataset_id(self):
        base, version = parse_dataset_id(_CMIP6_FULL_ID)
        self.assertEqual(base, _CMIP6_BASE_ID)
        self.assertEqual(version, _CMIP6_VERSION)

    def test_cmip7_dataset_id(self):
        cmip7_id = (
            "MIP-DRS7.CMIP7.CMIP.UKNCSP.UKESM1-3-LL.esm-piControl"
            ".r1i1p1f1.glb.mon.vo.tavg-ol-hxy-sea.g124.v20260818"
        )
        base, version = parse_dataset_id(cmip7_id)
        self.assertEqual(
            base,
            "MIP-DRS7.CMIP7.CMIP.UKNCSP.UKESM1-3-LL.esm-piControl.r1i1p1f1.glb.mon.vo.tavg-ol-hxy-sea.g124",
        )
        self.assertEqual(version, "v20260818")


class TestMassErrorExitCode(unittest.TestCase):
    def _make_error(self, failure):
        return MassError(failure, ["moo", "ls"])

    def test_user_error_returns_2(self):
        self.assertEqual(mass_error_exit_code(self._make_error(MassFailure.USER_ERROR)), 2)

    def test_access_error_returns_2(self):
        self.assertEqual(mass_error_exit_code(self._make_error(MassFailure.ACCESS_ERROR)), 2)

    def test_system_error_returns_3(self):
        self.assertEqual(mass_error_exit_code(self._make_error(MassFailure.SYSTEM_ERROR)), 3)

    def test_client_error_returns_3(self):
        self.assertEqual(mass_error_exit_code(self._make_error(MassFailure.CLIENT_ERROR)), 3)


class TestFetchVersionedFiles(unittest.TestCase):
    @patch(f"{_MODULE}.list_mass_files_with_checksums", return_value=_CMIP6_FILE_LIST)
    def test_success_returns_files_and_mass_path(self, _mock):
        result = fetch_versioned_files(_CMIP6_FULL_ID, _MASS_ROOT)
        self.assertIsInstance(result, tuple)
        files, mass_path = result
        self.assertEqual(len(files), 1)
        self.assertIn(_CMIP6_BASE_ID.replace(".", "/"), mass_path)

    @patch(f"{_MODULE}.list_mass_files_with_checksums", side_effect=FileNotExistMassError(["moo", "ls"]))
    def test_file_not_exist_error_returns_1(self, _mock):
        self.assertEqual(fetch_versioned_files(_CMIP6_FULL_ID, _MASS_ROOT), 1)

    @patch(f"{_MODULE}.list_mass_files_with_checksums", return_value={})
    def test_dataset_absent_from_listing_returns_1(self, _mock):
        self.assertEqual(fetch_versioned_files(_CMIP6_FULL_ID, _MASS_ROOT), 1)

    @patch(f"{_MODULE}.list_mass_files_with_checksums", return_value={
        _CMIP6_BASE_ID: {
            "status": "available",
            "timestamp": "v20190101",
            "files": [{"mass_path": "moose:/path/available/v20190101/tas.nc", "filesize": "1"}],
        }
    })
    def test_wrong_version_returns_1(self, _mock):
        self.assertEqual(fetch_versioned_files(_CMIP6_FULL_ID, _MASS_ROOT), 1)

    @patch(f"{_MODULE}.list_mass_files_with_checksums",
           side_effect=MassError(MassFailure.USER_ERROR, ["moo", "ls"]))
    def test_user_error_returns_2(self, _mock):
        self.assertEqual(fetch_versioned_files(_CMIP6_FULL_ID, _MASS_ROOT), 2)

    @patch(f"{_MODULE}.list_mass_files_with_checksums",
           side_effect=MassError(MassFailure.SYSTEM_ERROR, ["moo", "ls"]))
    def test_system_error_returns_3(self, _mock):
        self.assertEqual(fetch_versioned_files(_CMIP6_FULL_ID, _MASS_ROOT), 3)


class TestRunLsAction(unittest.TestCase):
    @patch(f"{_MODULE}.list_mass_files_with_checksums", return_value=_CMIP6_FILE_LIST)
    def test_success_returns_0_and_prints_json(self, _mock):
        buf = io.StringIO()
        with redirect_stdout(buf):
            result = run_ls_action(_CMIP6_FULL_ID, _MASS_ROOT)
        self.assertEqual(result, 0)
        payload = json.loads(buf.getvalue())
        self.assertEqual(payload["dataset_id"], _CMIP6_FULL_ID)
        self.assertEqual(len(payload["files"]), 1)

    @patch(f"{_MODULE}.list_mass_files_with_checksums", side_effect=FileNotExistMassError(["moo", "ls"]))
    def test_file_not_exist_error_returns_1(self, _mock):
        self.assertEqual(run_ls_action(_CMIP6_FULL_ID, _MASS_ROOT), 1)

    @patch(f"{_MODULE}.list_mass_files_with_checksums", return_value={})
    def test_dataset_absent_from_listing_returns_1(self, _mock):
        self.assertEqual(run_ls_action(_CMIP6_FULL_ID, _MASS_ROOT), 1)

    @patch(f"{_MODULE}.list_mass_files_with_checksums", return_value={
        _CMIP6_BASE_ID: {
            "status": "available",
            "timestamp": "v20190101",
            "files": [{"mass_path": "moose:/path/available/v20190101/tas.nc", "filesize": "1"}],
        }
    })
    def test_wrong_version_in_listing_returns_1(self, _mock):
        self.assertEqual(run_ls_action(_CMIP6_FULL_ID, _MASS_ROOT), 1)

    @patch(f"{_MODULE}.list_mass_files_with_checksums",
           side_effect=MassError(MassFailure.USER_ERROR, ["moo", "ls"]))
    def test_user_error_returns_2(self, _mock):
        self.assertEqual(run_ls_action(_CMIP6_FULL_ID, _MASS_ROOT), 2)

    @patch(f"{_MODULE}.list_mass_files_with_checksums",
           side_effect=MassError(MassFailure.SYSTEM_ERROR, ["moo", "ls"]))
    def test_system_error_returns_3(self, _mock):
        self.assertEqual(run_ls_action(_CMIP6_FULL_ID, _MASS_ROOT), 3)


class TestRunGetAction(unittest.TestCase):
    def setUp(self):
        self.destination = mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.destination)

    @patch(f"{_MODULE}.transfer_files")
    @patch(f"{_MODULE}.create_output_dir")
    @patch(f"{_MODULE}.list_mass_files_with_checksums", return_value=_CMIP6_FILE_LIST)
    def test_success_returns_0(self, _mock_list, mock_create_dir, _mock_transfer):
        mock_create_dir.return_value = Path(self.destination)
        result = run_get_action(_CMIP6_FULL_ID, _MASS_ROOT, self.destination, True, 100, False)
        self.assertEqual(result, 0)

    @patch(f"{_MODULE}.list_mass_files_with_checksums", side_effect=FileNotExistMassError(["moo", "ls"]))
    def test_file_not_exist_error_returns_1(self, _mock):
        result = run_get_action(_CMIP6_FULL_ID, _MASS_ROOT, self.destination, True, 100, False)
        self.assertEqual(result, 1)

    @patch(f"{_MODULE}.list_mass_files_with_checksums", return_value={})
    def test_dataset_absent_from_listing_returns_1(self, _mock):
        result = run_get_action(_CMIP6_FULL_ID, _MASS_ROOT, self.destination, True, 100, False)
        self.assertEqual(result, 1)

    @patch(f"{_MODULE}.list_mass_files_with_checksums",
           side_effect=MassError(MassFailure.USER_ERROR, ["moo", "ls"]))
    def test_user_error_returns_2(self, _mock):
        result = run_get_action(_CMIP6_FULL_ID, _MASS_ROOT, self.destination, True, 100, False)
        self.assertEqual(result, 2)

    @patch(f"{_MODULE}.list_mass_files_with_checksums",
           side_effect=MassError(MassFailure.SYSTEM_ERROR, ["moo", "ls"]))
    def test_system_error_returns_3(self, _mock):
        result = run_get_action(_CMIP6_FULL_ID, _MASS_ROOT, self.destination, True, 100, False)
        self.assertEqual(result, 3)

    @patch(f"{_MODULE}.transfer_files", side_effect=RuntimeError("unexpected"))
    @patch(f"{_MODULE}.create_output_dir")
    @patch(f"{_MODULE}.list_mass_files_with_checksums", return_value=_CMIP6_FILE_LIST)
    def test_generic_exception_returns_3(self, _mock_list, mock_create_dir, _mock_transfer):
        mock_create_dir.return_value = Path(self.destination)
        result = run_get_action(_CMIP6_FULL_ID, _MASS_ROOT, self.destination, True, 100, False)
        self.assertEqual(result, 3)


if __name__ == "__main__":
    unittest.main()
