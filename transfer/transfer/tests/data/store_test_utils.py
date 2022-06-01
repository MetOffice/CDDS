# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
import os

from dataclasses import dataclass
from enum import Enum
from typing import List

from transfer.command_line import parse_args_store
from hadsdk.config import FullPaths
from hadsdk.request import read_request


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
        arguments = parse_args_store(test_args, 'cdds_store')
        request = read_request(arguments.request)
        full_paths = FullPaths(arguments, request)
        log_dir = full_paths.log_directory('archive')
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
        return self._simulation_cmds('moo_mkdir')

    def moo_mv_cmds(self) -> List[str]:
        return self._simulation_cmds('moo_mv')

    def moo_mv_files(self) -> List[List[str]]:
        moo_mv_cmds = self.moo_mv_cmds()
        result = []
        for cmd in moo_mv_cmds:
            result.append(sorted(cmd.split()[9:-1]))
        return result

    def moo_put_cmds(self, state: FileState = None) -> List[str]:
        moo_put_cmds = self._simulation_cmds('moo_put')
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
