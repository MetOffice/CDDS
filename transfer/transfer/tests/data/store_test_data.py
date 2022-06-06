# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
import os
import tempfile
import shutil

from dataclasses import dataclass


DEFAULT_LOG_DATESTAMP = '2019-11-23T1432Z'


@dataclass
class TestData:
    number_variables: int = 0
    data_version: str = 'v20191128'
    test_temp_dir: str = ''
    test_dir_root: str = ''
    proc_dir_name: str = ''
    data_dir_name: str = ''
    request_filename: str = ''
    mass_root: str = ''
    mass_suffix: str = ''
    log_name: str = ''
    stream: str = ''

    @property
    def root_proc_dir(self):
        if not self.test_temp_dir:
            self.test_temp_dir = tempfile.mkdtemp()
            shutil.copytree(os.path.join(self.test_dir_root, self.proc_dir_name),
                            os.path.join(self.test_temp_dir, self.proc_dir_name))
        return os.path.join(self.test_temp_dir, self.proc_dir_name)

    @property
    def root_data_dir(self):
        return os.path.join(self.test_dir_root, self.data_dir_name)

    @property
    def request_json_path(self):
        return os.path.join(self.test_dir_root, self.request_filename)

    def get_arguments(self):
        base_arguments = [
            self.request_json_path,
            '--use_proc_dir',
            '--data_version', self.data_version,
            '--root_proc_dir', self.root_proc_dir,
            '--root_data_dir', self.root_data_dir,
            '--output_mass_root', self.mass_root,
            '--output_mass_suffix', self.mass_suffix,
            '--log_name', self.log_name,
            '--simulate',
        ]
        if self.stream:
            base_arguments += ['--stream', self.stream]
        return base_arguments
