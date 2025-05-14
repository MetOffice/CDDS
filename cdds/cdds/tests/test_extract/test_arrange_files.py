from pathlib import Path

import pytest

from cdds.extract.command_line import identify_files, symlink_files


@pytest.fixture
def dummy_files(tmp_path: Path):
    filenames = [
        "dn300a.p52015apr.pp",
        "dn300a.p42015apr.pp",
        "medusa_dn300o_1m_20150101-20150201_diad-T.nc",
    ]

    for filename in filenames:
        full_path = tmp_path / filename
        full_path.touch()
    return tmp_path


class TestIdentifyFiles:
    def test_identify_files(self, dummy_files: Path):
        expected = [
            ("dn300", "ap5", str(dummy_files), "dn300a.p52015apr.pp"),
            ("dn300", "ap4", str(dummy_files), "dn300a.p42015apr.pp"),
            ("dn300", "onm", str(dummy_files), "medusa_dn300o_1m_20150101-20150201_diad-T.nc"),
        ]

        assert expected == identify_files(dummy_files, "dn300")

    def test_symlink_files(self, dummy_files, tmp_path_factory):
        file_paths = identify_files(dummy_files, "dn300")
        input_dir = tmp_path_factory.mktemp("dir1")
        symlink_files(file_paths, input_dir)

        assert Path(input_dir, "ap5", "dn300a.p52015apr.pp").is_symlink()
        assert Path(input_dir, "ap4", "dn300a.p42015apr.pp").is_symlink()
        assert Path(input_dir, "onm", "medusa_dn300o_1m_20150101-20150201_diad-T.nc").is_symlink()
