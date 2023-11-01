# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.
from configparser import ConfigParser
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Any

from cdds.common.platforms import Facility, whereami
from cdds.common.request.request_section import Section, load_types


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
        'no_email_notifications': False,
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
    cylc_args: str = ''
    no_email_notifications: bool = False
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
            config_items = load_types(dict(config.items('conversion')), ['override_cycling_frequency'])
            values.update(config_items)
        return ConversionSection(**values)

    def add_to_config(self, config: ConfigParser) -> None:
        """
        Adds values defined by the conversion section to given configuration.

        :param config: Configuration where values should add to
        :type config: ConfigParser
        """
        defaults = conversion_defaults()
        self._add_to_config_section(config, 'conversion', defaults)
