# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.
import os

from dataclasses import dataclass, field
from metomi.isodatetime.data import TimePoint
from metomi.isodatetime.parsers import TimePointParser
from typing import Dict, List, Any

from cdds.common.plugins.plugin_loader import load_plugin
from cdds.common import run_command, rose_config
from cdds.common.io import delete_file, write_into_temp_file
from cdds.common.plugins.plugins import PluginStore


NO_PARENT = 'no parent'
STANDARD = 'standard'


@dataclass
class RoseSuiteInfo:
    data: Dict[str, str] = field(default_factory=dict)

    def license(self) -> str:
        if 'license' in self.data.keys() and self.data['license']:
            return self.data['license']
        else:
            plugin = PluginStore.instance().get_plugin()
            return plugin.license()

    def branch_method(self) -> str:
        return STANDARD if self.has_parent() else NO_PARENT

    def branch_date_in_child(self) -> TimePoint:
        return TimePointParser().parse('{start-date}T00:00:00'.format(**self.data))

    def branch_date_in_parent(self) -> TimePoint:
        return TimePointParser().parse('{branch-date}T00:00:00'.format(**self.data))

    def mip_table_dir(self) -> str:
        plugin = PluginStore.instance().get_plugin()
        return plugin.mip_table_dir()

    def end_date(self) -> TimePoint:
        date = '{}T00:00:00'.format(self.data['end-date'])
        return TimePointParser().parse(date)

    def start_date(self) -> TimePoint:
        date = '{}T00:00:00'.format(self.data['start-date'])
        return TimePointParser().parse(date)

    def has_parent(self):
        key = 'parent-experiment-id'
        # Allowed values of parent-experiment-id other than valid experiment id's
        return key in self.data and self.data[key] not in [NO_PARENT, '', 'None', None]


@dataclass
class RoseSuiteArguments:
    """
    Stores all arguments that are used to write a request from a rose suite

    branch - the branch that should be used, for example: cdds
    revision - revision of the rose suite that should be used
    suite - the suite ID
    package - the package of the experiment
    streams - the additional round bound streams that should be considered
    cv_dir - the directory of the controlled vocabularies
    request_file - the path to the output file of the request
    """
    external_plugin: str = ''
    external_plugin_location: str = ''
    suite: str = ''
    branch: str = ''
    revision: str = ''
    package: str = ''
    streams: List[str] = field(default_factory=list)
    root_proc_dir: str = ''
    root_data_dir: str = ''
    mass_data_class: str = ''
    mass_ensemble_member: str = ''
    output_dir: str = os.path.dirname(os.path.realpath(__file__))
    output_file_name: str = 'request.cfg'
    start_date: TimePoint = None
    end_date: TimePoint = None

    @staticmethod
    def from_user_args(user_args: Dict[str, Any]) -> 'RoseSuiteArguments':
        arguments = RoseSuiteArguments()
        arguments.external_plugin = user_args.external_plugin
        arguments.external_plugin_location = user_args.external_plugin_location
        arguments.suite = user_args.suite
        arguments.branch = user_args.branch
        arguments.revision = user_args.revision
        arguments.package = user_args.package
        arguments.streams = user_args.streams
        arguments.mass_data_class = user_args.mass_data_class
        arguments.mass_ensemble_member = user_args.mass_ensemble_member

        if user_args.output_dir:
            arguments.output_dir = expand_path(user_args.output_dir)

        if user_args.output_file_name:
            arguments.output_file_name = user_args.output_file_name

        if user_args.start_date:
            iso_start_date = '{}T00:00:00'.format(user_args.start_date)
            arguments.start_date = TimePointParser().parse(iso_start_date)

        if user_args.end_date:
            iso_end_date = '{}T00:00:00'.format(user_args.end_date)
            arguments.end_date = TimePointParser().parse(iso_end_date)

        if user_args.root_proc_dir:
            arguments.root_proc_dir = expand_path(user_args.root_proc_dir)

        if user_args.root_data_dir:
            arguments.root_data_dir = expand_path(user_args.root_data_dir)

        return arguments

    @property
    def request_file(self):
        return os.path.join(self.output_dir, self.output_file_name)


def load_rose_suite_info(svn_url: str, arguments: RoseSuiteArguments) -> RoseSuiteInfo:
    """
    Load rose suite info by given Subversion URL and convert it
    into a dictionary containing the key and the actual value

    Parameters
    ----------
    svn_url: :class:`string`
        The Subversion URL where the rose suite info is found

    Returns
    -------
    :dict
        the rose suite info as a dictionary of key :string and
        value :string
    """
    command = ['svn', 'cat', svn_url]
    data = run_command(command)
    temp_file = write_into_temp_file(data)
    suite_info = load_suite_info_from_file(temp_file)
    delete_file(temp_file)

    mip_era = suite_info.get('mip-era', 'CMIP6')
    load_plugin(mip_era, arguments.external_plugin, arguments.external_plugin_location)

    return RoseSuiteInfo(suite_info)


def load_suite_info_from_file(file_path: str) -> Dict[str, str]:
    """
    Loads the rose suite info from a file

    :param file_path: Path to the rose suite info file
    :type file_path: str
    :return: The rose suite info as a dictionary of key :string and value :string
    :rtype: dict
    """
    full_suite = rose_config.load(file_path)
    suite_info = {k: v.value for k, v in full_suite.value.items() if v.state == ''}
    return suite_info


def expand_path(path: str) -> str:
    if path.startswith('~') or '$' in path:
        path = os.path.expanduser(os.path.expandvars(path))
    return os.path.abspath(path)
