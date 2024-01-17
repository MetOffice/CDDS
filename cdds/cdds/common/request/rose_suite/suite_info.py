# (C) British Crown Copyright 2023-2024, Met Office.
# Please see LICENSE.rst for license details.
"""
Module to manage the loading of the rose-suite.info into a request object
"""
import os

from argparse import Namespace
from dataclasses import dataclass, field
from metomi.isodatetime.data import TimePoint
from metomi.isodatetime.parsers import TimePointParser
from typing import Dict, List

from cdds.common.plugins.plugin_loader import load_plugin
from cdds.common import run_command, rose_config
from cdds.common.io import delete_file, write_into_temp_file
from cdds.common.plugins.plugins import PluginStore


NO_PARENT = 'no parent'
STANDARD = 'standard'


@dataclass
class RoseSuiteInfo:
    """
    Represents a rose-suite.info with its values
    """
    data: Dict[str, str] = field(default_factory=dict)

    def license(self) -> str:
        """
        Returns the license. First it checks if the license is defined in the
        rose-suite.info if not returns the license defined in the plugins.

        :return: License
        :rtype: str
        """
        if 'license' in self.data.keys() and self.data['license']:
            return self.data['license']
        else:
            plugin = PluginStore.instance().get_plugin()
            return plugin.license()

    def branch_method(self) -> str:
        """
        Returns the branch method.

        :return: The branch method
        :rtype: str
        """
        return STANDARD if self.has_parent() else NO_PARENT

    def branch_date_in_child(self) -> TimePoint:
        """
        Returns the branch date in child in isodate format

        :return: Branch date in child
        :rtype: TimePoint
        """
        return TimePointParser().parse('{start-date}T00:00:00'.format(**self.data))

    def branch_date_in_parent(self) -> TimePoint:
        """
        Returns the branch date in parent in isodate format

        :return: Branch date in parent
        :rtype: TimePoint
        """
        return TimePointParser().parse('{branch-date}T00:00:00'.format(**self.data))

    def mip_table_dir(self) -> str:
        """
        Returns the path to the MIP table directory by getting it from the plugin.

        :return: Path to the MIP table directory
        :rtype: str
        """
        plugin = PluginStore.instance().get_plugin()
        return plugin.cdds_paths().mip_table_dir()

    def end_date(self) -> TimePoint:
        """
        Returns the end date of the experiment in isodate time.

        :return: End date of the experiment
        :rtype: TimePoint
        """
        date = '{}T00:00:00'.format(self.data['end-date'])
        return TimePointParser().parse(date)

    def start_date(self) -> TimePoint:
        """
        Returns the start date of the experiment in isodate time.

        :return: Start date of the experiment
        :rtype: TimePoint
        """
        date = '{}T00:00:00'.format(self.data['start-date'])
        return TimePointParser().parse(date)

    def has_parent(self) -> bool:
        """
        Checks if a parent experiment is defined.

        :return: Is a parent experiment defined?
        :rtype: bool
        """
        key = 'parent-experiment-id'
        # Allowed values of parent-experiment-id other than valid experiment id's
        return key in self.data and self.data[key] not in [NO_PARENT, '', 'None', None]


@dataclass
class RoseSuiteArguments:
    """
    Stores all arguments that are used to write a request from a rose suite
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
    def from_user_args(command_line_args: Namespace) -> 'RoseSuiteArguments':
        """
        Returns the rose suite arguments from the command line arguments.

        :param command_line_args: Arguments defined by the command
        :type command_line_args: Namespace
        :return: Rose suite arguments
        :rtype: RoseSuiteArguments
        """
        arguments = RoseSuiteArguments()
        arguments.external_plugin = command_line_args.external_plugin
        arguments.external_plugin_location = command_line_args.external_plugin_location
        arguments.suite = command_line_args.suite
        arguments.branch = command_line_args.branch
        arguments.revision = command_line_args.revision
        arguments.package = command_line_args.package
        arguments.streams = command_line_args.streams
        arguments.mass_data_class = command_line_args.mass_data_class
        arguments.mass_ensemble_member = command_line_args.mass_ensemble_member

        if command_line_args.output_dir:
            arguments.output_dir = expand_path(command_line_args.output_dir)

        if command_line_args.output_file_name:
            arguments.output_file_name = command_line_args.output_file_name

        if command_line_args.start_date:
            iso_start_date = '{}T00:00:00'.format(command_line_args.start_date)
            arguments.start_date = TimePointParser().parse(iso_start_date)

        if command_line_args.end_date:
            iso_end_date = '{}T00:00:00'.format(command_line_args.end_date)
            arguments.end_date = TimePointParser().parse(iso_end_date)

        if command_line_args.root_proc_dir:
            arguments.root_proc_dir = expand_path(command_line_args.root_proc_dir)

        if command_line_args.root_data_dir:
            arguments.root_data_dir = expand_path(command_line_args.root_data_dir)

        return arguments

    @property
    def request_file(self) -> str:
        """
        Returns the path to the request configuration file.

        :return: Path to the request configuration file
        :rtype: str
        """
        return os.path.join(self.output_dir, self.output_file_name)


def load_rose_suite_info(svn_url: str, arguments: RoseSuiteArguments) -> RoseSuiteInfo:
    """
    Load rose suite info by given Subversion URL, convert it into a dictionary containing
    the key and the actual value and store it into a RoseSuiteInfo object.

    :param svn_url: The Subversion URL where the rose suite info is found
    :type svn_url: str
    :param arguments: Additional arguments that should be considered
    :type arguments: RoseSuiteArguments
    :return: the rose suite info as a RoseSuiteInfo object
    :rtype: RoseSuiteInfo
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
    """
    Expand the given path.

    :param path: Path to expand
    :type path: str
    :return: The absolute expanded path
    :rtype: str
    """
    if path.startswith('~') or '$' in path:
        path = os.path.expanduser(os.path.expandvars(path))
    return os.path.abspath(path)
