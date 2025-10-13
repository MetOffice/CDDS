# (C) British Crown Copyright 2025, Met Office.
# Please see LICENSE.md for license details.
import shutil
import unittest
from pathlib import Path
from tempfile import mkdtemp
from unittest.mock import patch

from cdds.misc.retrieve_mass_data import transfer_files


class TestTransferFiles(unittest.TestCase):
    MASS_COMMAND_OUTPUT = "#### get, command-id=2059286267, estimated-cost=60722658byte(s), files=1, media=0"

    def setUp(self):
        self.dummy_chunks = [["file1.nc", "file2.nc"], ["file3.nc"]]
        self.tmp_dir = Path(mkdtemp(prefix="test_output_dir_"))
        self.output_dir = self.tmp_dir / "output"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

    @patch("cdds.misc.retrieve_mass_data.run_mass_command")
    @patch("logging.getLogger")
    def test_transfer_files_dry_run(self, mock_get_logger, mock_run_mass_command):
        mock_logger = mock_get_logger.return_value
        mock_run_mass_command.return_value = (self.MASS_COMMAND_OUTPUT,)
        transfer_files(self.dummy_chunks, self.output_dir, dry_run=True)
        self.assertEqual(mock_run_mass_command.call_count, len(self.dummy_chunks))
        for call in mock_logger.info.call_args_list:
            self.assertIn(
                self.MASS_COMMAND_OUTPUT,
                call[0][0],
            )

    @patch(
        "cdds.misc.retrieve_mass_data.run_mass_command",
        side_effect=RuntimeError("fail"),
    )
    @patch("logging.getLogger")
    def test_transfer_files_runtime_error(self, mock_get_logger, mock_run_mass_command):
        mock_logger = mock_get_logger.return_value
        with self.assertRaises(RuntimeError):
            transfer_files(self.dummy_chunks, self.output_dir, dry_run=True)
        self.assertTrue(mock_logger.critical.called)


if __name__ == "__main__":
    unittest.main()
