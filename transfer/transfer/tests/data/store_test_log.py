# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
import os

from dataclasses import dataclass
from enum import Enum
from typing import List

from transfer.command_line import parse_args_store
from hadsdk.config import FullPaths
from hadsdk.request import read_request


class LogKey(Enum):
    CRITICAL = 'CRITICAL'
    FIRST_PUBLICATION = 'first publication'
    MOO_TEST = 'moo test'
    MOO_MKDIR = 'moo mkdir'
    MOO_PUT = 'moo put'
    ARCHIVING_MODE = 'archiving mode'
    SIMULATING_MASS = 'simulating mass command'
    CONTINUE_ABORTED = 'continue aborted'
    APPEND_IN_TIME = 'append (in time)'
    SUPERSEDED = 'superseded'
    EMBARGOED = 'embargoed'
    MOO_MV = 'moo mv'
    PREVIOUSLY_WITHDRAWN = 'previously withdrawn'
    ALREADY_IN_AVAILABLE_STATE = 'already in available state'
    INVALID_MASS_STATE = 'invalid mass state'
    EMBARGOED_STATE_DIFFERENT_DATESTAMP = 'embargoed state with a different datestamp'
    USED_DATESTAMP = 'used datestamp'
    PUBLISH_DATA_USED_DATESTAMP = 'publish data with a previously used datestamp'
    PREPEND_IN_TIME = 'prepend (in time)'
    MOO_COMMAND_FAILED = 'moo command failed'


@dataclass
class LogFile:

    log_txt: List[str]

    @classmethod
    def load(cls, test_args: List[str], log_name: str, log_datestamp: str) -> "LogFile":
        args = parse_args_store(test_args, 'cdds_store')
        request = read_request(args.request)
        full_paths = FullPaths(args, request)
        log_dir = full_paths.log_directory('archive')
        if args.stream:
            log_file_name = '{0}_{1}_{2}.log'.format(log_name, args.stream, log_datestamp)
        else:
            log_file_name = '{0}_{1}.log'.format(log_name, log_datestamp)
        log_path = os.path.join(log_dir, log_file_name)
        with open(log_path) as log_file:
            log_txt = log_file.readlines()
        return LogFile(log_txt)

    def critical(self) -> List[str]:
        return [l1 for l1 in self.log_txt if LogKey.CRITICAL.value in l1]

    def count(self, key_word: LogKey) -> int:
        lines = [l1 for l1 in self.log_txt if key_word.value in l1.lower()]
        return len(lines)

    def archive_cmds(self, archive_mode: LogKey) -> List[str]:
        mode_msgs = [l1 for l1 in self.log_txt if LogKey.ARCHIVING_MODE.value in l1.lower()]
        return [l1 for l1 in mode_msgs if archive_mode.value in l1.lower()]

    def simulation_cmds(self, command_name: LogKey) -> List[str]:
        mode_msgs = [l1 for l1 in self.log_txt if LogKey.SIMULATING_MASS.value in l1.lower()]
        return [l1 for l1 in mode_msgs if command_name.value in l1.lower()]

    def moo_put_cmds(self, state: LogKey = None) -> List[str]:
        moo_put_cmds = self.simulation_cmds(LogKey.MOO_PUT)
        if state:
            return [mc1 for mc1 in moo_put_cmds if state.value in mc1]
        return moo_put_cmds

    def moo_put_files(self, state: LogKey = None) -> List[str]:
        moo_put_cmds = self.moo_put_cmds(state)
        for cmd1 in moo_put_cmds:
            return sorted(cmd1.split()[9:-1])
        return []
