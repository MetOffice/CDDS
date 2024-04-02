# (C) British Crown Copyright 2023-2024, Met Office.
# Please see LICENSE.rst for license details.
"""
Module to handle the conversion section in the request configuration
"""
from configparser import ConfigParser
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Any

from cdds.common.platforms import Facility, whereami
from cdds.common.request.request_section import Section, load_types, expand_paths
from cdds.common.request.rose_suite.suite_info import RoseSuiteInfo, RoseSuiteArguments


def conversion_defaults() -> Dict[str, Any]:
    """
    Calculates the defaults for the conversion section of
    the request configuration.

    :return: The defaults for the conversion section
    :rtype: Dict[str, Any]
    """
    facility = whereami()
    if facility == Facility.JASMIN:
        skip_extract = True
        skip_extract_validation = False
        skip_configure = False
        skip_qc = False
        skip_archive = True
        cdds_workflow_branch = 'cdds_jasmin_2.3'
    else:
        skip_extract = False
        skip_extract_validation = False
        skip_configure = False
        skip_qc = False
        skip_archive = False
        cdds_workflow_branch = 'trunk'

    return {
        'cdds_workflow_branch': cdds_workflow_branch,
        'cylc_args': '-v',
        'no_email_notifications': True,
        'skip_extract': skip_extract,
        'skip_extract_validation': skip_extract_validation,
        'skip_configure': skip_configure,
        'skip_qc': skip_qc,
        'skip_archive': skip_archive,
    }


@dataclass
class ConversionSection(Section):
    """
    Represents the conversion section in the request configuration
    """
    skip_extract: bool = False
    skip_extract_validation: bool = False
    skip_configure: bool = False
    skip_qc: bool = False
    skip_archive: bool = False
    cdds_workflow_branch: str = ''
    cylc_args: List[str] = field(default_factory=list)
    no_email_notifications: bool = True
    scale_memory_limits: float = None
    override_cycling_frequency: List[str] = field(default_factory=list)  # ['stream=frequency']
    model_params_dir: str = ''

    @property
    def items(self) -> Dict[str, Any]:
        """
        Returns all items of the conversion section as a dictionary.

        :return: Items as dictionary
        :rtype: Dict[str, Any]
        """
        return asdict(self)

    @staticmethod
    def from_config(config: ConfigParser) -> 'ConversionSection':
        """
        Loads the conversion section of a request configuration.

        :param config: Parser for the request configuration
        :type config: ConfigParser
        :return: New conversion section
        :rtype: ConversionSection
        """
        values = conversion_defaults()
        if config.has_section('conversion'):
            config_items = load_types(dict(config.items('conversion')), ['override_cycling_frequency', 'cylc_args'])
            expand_paths(config_items, ['model_params_dir'])
            new_cylc_args = load_cylc_args(config_items['cylc_args'])
            config_items['cylc_args'] = new_cylc_args
            values.update(config_items)
        else:
            values['cylc_args'] = values['cylc_args'].split(' ')
        return ConversionSection(**values)

    @staticmethod
    def from_rose_suite_info(suite_info: RoseSuiteInfo, arguments: RoseSuiteArguments) -> 'ConversionSection':
        """
        Loads the conversion section of a rose-suite.info.

        :param suite_info: The rose-suite.info to be loaded
        :type suite_info: RoseSuiteInfo
        :param arguments: Additional arguments to be considered
        :type arguments: RoseSuiteArguments
        :return: New conversion section
        :rtype: ConversionSection
        """
        defaults = conversion_defaults()
        return ConversionSection(**defaults)

    def add_to_config(self, config: ConfigParser) -> None:
        """
        Adds values defined by the conversion section to given configuration.

        :param config: Configuration where values should add to
        :type config: ConfigParser
        """
        defaults = conversion_defaults()
        self._add_to_config_section(config, 'conversion', defaults)


def load_cylc_args(cylc_args: List[str]) -> List[str]:
    """
    Load and update the cylc arguments for the CDDS processing suite. Therefore, it checks of
    the -v option is always given and that a workflow-name (default: cdds_{request_id}_{stream})
    is provided.

    :param cylc_args: Cylc arguments to load and updated
    :type cylc_args: List[str]
    :return: Cylc arguments for CDDS processing suite
    :rtype: List[str]
    """
    if '-v' not in cylc_args:
        cylc_args += ['-v']

    # If user does not specify a run name for the rose suite, use cdds_{request_id}
    if '--workflow-name' in cylc_args:
        name_indices = [index for index, element in enumerate(cylc_args) if '--workflow-name' in element]
        for index in name_indices:
            if '=' in cylc_args[index]:
                index_to_change = index
            else:
                index_to_change = index + 1
            cylc_args[index_to_change] = cylc_args[index_to_change] + '_{stream}'
    else:
        cylc_args += ['--workflow-name=cdds_{request_id}_{stream}']
    return cylc_args
