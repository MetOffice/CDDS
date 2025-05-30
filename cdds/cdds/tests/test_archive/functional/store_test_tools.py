# (C) British Crown Copyright 2022-2025, Met Office.
# Please see LICENSE.md for license details.
import os
import tempfile
import shutil

from dataclasses import dataclass
from enum import Enum
from typing import List

from cdds.archive.command_line import parse_args_store
from cdds.common.request.request import read_request
from cdds.common.cdds_files.cdds_directories import log_directory


DEFAULT_LOG_DATESTAMP = '2019-11-23T1432Z'


@dataclass
class TestData:

    __test__ = False

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
    variables_file: str = ''

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
    def request_cfg_path(self):
        return os.path.join(self.test_dir_root, self.request_filename)

    def update_request_cfg(self):
        path = self.request_cfg_path
        with open(path, 'r') as f:
            print(f.readlines())

        request = read_request(self.request_cfg_path)
        request.misc.use_proc_dir = True
        request.common.root_proc_dir = self.root_proc_dir
        request.common.root_data_dir = self.root_data_dir
        request.data.output_mass_root = self.mass_root
        request.data.output_mass_suffix = self.mass_suffix
        request.data.variable_list_file = self.variables_file
        request.data.data_version = self.data_version
        request.common.simulation = True
        request.write(self.request_cfg_path)

    def get_arguments(self):
        self.update_request_cfg()

        base_arguments = [
            self.request_cfg_path,
            '--log_name', self.log_name,
        ]
        if self.stream:
            base_arguments += ['--stream', self.stream]
        return base_arguments


class ArchiveMode(Enum):
    PREPEND_IN_TIME = 'prepend (in time)'
    APPEND_IN_TIME = 'append (in time)'
    CONTINUE_ABORTED = 'continue aborted'
    FIRST_PUBLICATION = 'first publication'
    PREVIOUSLY_WITHDRAWN = 'previously withdrawn'


class FileState(Enum):
    SUPERSEDED = 'superseded'
    EMBARGOED = 'embargoed'


@dataclass
class LogFile:

    log_txt: List[str]

    @classmethod
    def load(cls, test_args: List[str], log_name: str, log_datestamp: str) -> "LogFile":
        arguments = parse_args_store(test_args, log_name)
        request = read_request(arguments.request)

        log_dir = log_directory(request, 'archive')
        if arguments.stream:
            log_file_name = '{0}_{1}_{2}.log'.format(log_name, arguments.stream, log_datestamp)
        else:
            log_file_name = '{0}_{1}.log'.format(log_name, log_datestamp)
        log_path = os.path.join(log_dir, log_file_name)
        with open(log_path) as log_file:
            log_txt = log_file.readlines()
        return LogFile(log_txt)

    def critical(self) -> List[str]:
        return [l1 for l1 in self.log_txt if 'CRITICAL' in l1]

    def archive_cmds(self, archive_mode: ArchiveMode) -> List[str]:
        archive_cmds = [msg for msg in self.log_txt if 'archiving mode' in msg.lower()]
        return [cmd for cmd in archive_cmds if archive_mode.value in cmd.lower()]

    def moo_test_cmds(self) -> List[str]:
        return self._simulation_cmds('moo test')

    def moo_mkdir_cmds(self) -> List[str]:
        return self._simulation_cmds('moo mkdir')

    def moo_mv_cmds(self) -> List[str]:
        return self._simulation_cmds('moo mv')

    def moo_mv_files(self) -> List[List[str]]:
        moo_mv_cmds = self.moo_mv_cmds()
        result = []
        for cmd in moo_mv_cmds:
            result.append(sorted(cmd.split()[9:-1]))
        return result

    def moo_put_cmds(self, state: FileState = None) -> List[str]:
        moo_put_cmds = self._simulation_cmds('moo put')
        if state:
            return [cmd for cmd in moo_put_cmds if state.value in cmd]
        return moo_put_cmds

    def moo_put_files(self, state: FileState = None) -> List[List[str]]:
        moo_put_cmds = self.moo_put_cmds(state)
        result = []
        for cmd in moo_put_cmds:
            result.append(sorted(cmd.split()[9:-1]))
        return result

    def _simulation_cmds(self, command_name: str) -> List[str]:
        sim_cmds = [l1 for l1 in self.log_txt if 'simulating mass command' in l1.lower()]
        return [cmd for cmd in sim_cmds if command_name in cmd.lower()]
