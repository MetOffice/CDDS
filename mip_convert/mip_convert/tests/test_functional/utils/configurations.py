# (C) British Crown Copyright 2022-2023, Met Office.
# Please see LICENSE.rst for license details.
"""
Module to specify the classes that are needed for storing the information of the test data for
functional tests in MIP convert
"""
from abc import ABC
from dataclasses import dataclass, asdict, field
from typing import Dict, Any, List

from mip_convert.tests.test_functional.utils.constants import (ARISE_LICENSE, CMIP6_LICENSE, CORDEX_LICENSE,
                                                               GCMODELDEV_LICENSE)
from mip_convert.tests.test_functional.utils.directories import (CMIP6_MIP_TABLE_DIR, CORDEX_MIP_TABLE_DIR,
                                                                 ARISE_MIP_TABLE_DIR, SEASONAL_MIP_TABLE_DIR,
                                                                 NAHOSMIP_MIP_TABLE_DIR,
                                                                 ROOT_REFERENCE_DATA_DIR, ROOT_ANCIL_DIR)


@dataclass
class CommonInfo:
    """
    Stores common test data information that is necessary and equal for all projects
    It stores values (in the corresponding directory) to the chapters of the MIP configuration:
        * cmor_setup
        * cmor_dataset
    Other values will be stored in the common directory
    """
    common: Dict[str, Any] = None
    cmor_setup: Dict[str, Any] = None
    cmor_dataset: Dict[str, Any] = None

    def as_dict(self) -> Dict[str, Dict[str, Any]]:
        """
        Returns the information as a directory using the MIP configuration structure as template, e.g.:
        {
            'COMMON': {
                'root_test_dir': '/path/to/root/test/dir'
            },
            'cmor_setup': {
                'create_subdirectories': '0'
            },
            'cmor_data_set': {
                'calendar': '360_day',
                'grid': 'not checked'
            }
        }

        :return: Values as directory (like Mip configuration)
        :rtype: Dict[str, Any]
        """
        excludes = ['common']
        items = {
            k: v for k, v in asdict(self).items() if v and k not in excludes
        }
        items['COMMON'] = self.common
        return items

    @classmethod
    def default_common_info(cls) -> 'CommonInfo':
        """
        Returns the default common values for the projects CMIP6, CORDEX and ARISE.

        :return: Default common values
        :rtype: CommonInfo
        """
        return CommonInfo(
            common={
                'root_test_location': ROOT_REFERENCE_DATA_DIR,
                'root_ancil_dir': ROOT_ANCIL_DIR
            },
            cmor_setup={
                # 'cmor_log_file': '${COMMON:test_location}/cmor.log',  # Kerstin move to specific info?
                'create_subdirectories': '0'
            },
            cmor_dataset={
                'calendar': '360_day',
                'grid_label': 'gn',
                'institution_id': 'MOHC',
            }
        )


@dataclass
class ProjectInfo:
    """
    Stores values that are common for a specific project. The values are stored in following
    dictionaries following the structure of the MIP configuration:
        * cmor_setup
        * cmor_dataset
        * request
        * global_attributes
    """
    project_id: Dict[str, Any] = None
    cmor_setup: Dict[str, Any] = None
    cmor_dataset: Dict[str, Any] = None
    request: Dict[str, Any] = None
    global_attributes: Dict[str, Any] = None

    def as_dict(self) -> Dict[str, Dict[str, Any]]:
        """
        Returns the information as a directory using the MIP configuration structure as template, e.g.:
        {
            'cmor_setup': {
                'netcdf_file_action': 'CMOR_REPLACE_4'
            },
            'cmor_data_set': {
                'branch_method': 'no parent'
            },
             'request': {
                'base_date': '2000-01-01T00:00:00'
            },
             'global_attributes': {
                'further_info_url': 'https://furtherinfo.es-doc.org/CMIP6.MOHC.UKESM1-0-LL.amip.none.r1i1p1f1'
            }
        }

        :return: Values as directory (like Mip configuration)
        :rtype: Dict[str, Any]
        """
        excludes = ['project_id']
        items = {
            k: v for k, v in asdict(self).items() if v and k not in excludes
        }
        return items

    @classmethod
    def cmip6_project_info(cls) -> 'ProjectInfo':
        """
        Returns all common values that are specific for CMIP6 projects.

        :return: Values that are specific for CMIP6 projects
        :rtype: ProjectInfo
        """
        return ProjectInfo(
            project_id='CMIP6',
            cmor_setup={
                'mip_table_dir': CMIP6_MIP_TABLE_DIR,
                'netcdf_file_action': 'CMOR_REPLACE_4',
            },
            cmor_dataset={
                'grid': 'not checked',
                'branch_method': 'no parent',
                'experiment_id': 'amip',
                'license': CMIP6_LICENSE,
                'mip': 'CMIP',
                'mip_era': 'CMIP6',
                'model_id': 'UKESM1-0-LL',
                'model_type': 'AGCM',
                'nominal_resolution': '5 km',
                'sub_experiment_id': 'none',
                'variant_label': 'r1i1p1f1'
            },
            request={
                'base_date': '2000-01-01T00:00:00'
            },
            global_attributes={
                'further_info_url': 'https://furtherinfo.es-doc.org/CMIP6.MOHC.UKESM1-0-LL.amip.none.r1i1p1f1'
            }
        )

    @classmethod
    def hires_project_info(cls) -> 'ProjectInfo':
        """
        Returns all common values that are specific for high resolution model runs.

        :return: Values that are specific for high resolution runs
        :rtype: ProjectInfo
        """
        return ProjectInfo(
            project_id='HIRES',
            cmor_setup={
                'mip_table_dir': CMIP6_MIP_TABLE_DIR,
                'netcdf_file_action': 'CMOR_REPLACE_4',
            },
            cmor_dataset={
                'grid': 'not checked',
                'license': CMIP6_LICENSE,
                'branch_date_in_child': '1950-01-01T00:00:00',
                'branch_date_in_parent': '1980-01-01T00:00:00',
                'branch_method': 'standard',
                'experiment_id': 'hist-1950',
                'mip': 'HighResMIP',
                'mip_era': 'CMIP6',
                'model_id': 'HadGEM3-GC31-HH',
                'model_type': 'AOGCM',
                'nominal_resolution': '10 km',
                'parent_base_date': '1950-01-01T00:00:00',
                'parent_experiment_id': 'spinup-1950',
                'parent_mip_era': 'CMIP6',
                'parent_model_id': 'HadGEM3-GC31-MH',
                'parent_time_units': 'days since 1950-01-01',
                'parent_variant_label': 'r1i1p1f1',
                'sub_experiment_id': 'none',
                'variant_label': 'r1i1p1f1'
            },
            request={
                'base_date': '1950-01-01T00:00:00'
            },
            global_attributes={
                'further_info_url': 'https://furtherinfo.es-doc.org/CMIP6.MOHC.UKESM1-0-LL.amip.none.r1i1p1f1'
            }
        )

    @classmethod
    def arise_project_info(cls) -> 'ProjectInfo':
        """
        Returns all common values that are specific for ARISE projects.

        :return: Values that are specific for ARISE projects
        :rtype: ProjectInfo
        """
        return ProjectInfo(
            project_id='ARISE',
            cmor_setup={
                'mip_table_dir': ARISE_MIP_TABLE_DIR,
                'netcdf_file_action': 'CMOR_REPLACE_4',
            },
            cmor_dataset={
                'grid': 'not checked',
                'branch_method': 'standard',
                'branch_date_in_child': '1850-01-01T00:00:00',
                'branch_date_in_parent': '2250-01-01T00:00:00',
                'experiment_id': 'arise-sai-1p5',
                'license': ARISE_LICENSE,
                'mip': 'ARISE',
                'mip_era': 'ARISE',
                'model_id': 'UKESM1-0-LL',
                'model_type': 'AOGCM',
                'nominal_resolution': '250 km',
                'sub_experiment_id': 'none',
                'variant_label': 'r1i1p1f2',
                'parent_base_date': '1850-01-01T00:00:00',
                'parent_experiment_id': 'ssp245',
                'parent_mip_era': 'CMIP6',
                'parent_model_id': 'UKESM1-0-LL',
                'parent_time_units': 'days since 1850-01-01',
                'parent_variant_label': 'r1i1p1f2',
            },
            request={
                'base_date': '2000-01-01T00:00:00'
            },
            global_attributes={
                'further_info_url': 'https://furtherinfo.es-doc.org/CMIP6.MOHC.UKESM1-0-LL.historical.none.r1i1p1f2'
            }
        )

    @classmethod
    def cordex_project_info(cls) -> 'ProjectInfo':
        """
        Returns all common values that are specific for CORDEX projects.

        :return: Values that are specific for CORDEX projects
        :rtype: ProjectInfo
        """
        return ProjectInfo(
            project_id='CORDEX-CMIP6',
            cmor_setup={
                'mip_table_dir': CORDEX_MIP_TABLE_DIR,
                'netcdf_file_action': 'CMOR_REPLACE_4',
            },
            cmor_dataset={
                'branch_method': 'no parent',
                'grid': 'Native ; None x None longitude/latitude',
                'institution_id': 'MOHC',
                'license': CORDEX_LICENSE,
                'mip_era': 'CMIP6',
                'mip': 'DD',
                'model_id': 'HadREM3-GA7-05',
                'model_type': 'ARCM',
                'nominal_resolution': '25 km',
                'output_file_template': (
                    '<variable_id><domain_id><driving_source_id><driving_experiment_id><driving_variant_label>'
                    '<institution_id><source_id><version_realization><frequency>'),
                'variant_label': 'r1i1p1f3'
            },
            request={
                'base_date': '1850-01-01T00:00:00'
            },
            global_attributes={
                'contact': 'a.b.c',
                'domain': 'Europe',
                'domain_id': 'EUR-11',
                'driving_experiment': 'evaluation',
                'driving_experiment_id': 'evaluation',
                'driving_experiment_name': 'evaluation',
                'driving_institution_id': 'MOHC',
                'driving_source_id': 'HadGEM3-GC31-LL',
                'driving_variant_label': 'r1i1p1f3',
                'further_info_url': 'None',
                'project_id': 'CORDEX-CMIP6',
                'source_configuration_id': 'v1.0',
                'version_realization': 'v1-r1'
            }
        )

    @classmethod
    def seasonal_project_info(cls) -> 'ProjectInfo':
        """
        Returns all common values that are specific for CMIP6 projects.

        :return: Values that are specific for CMIP6 projects
        :rtype: ProjectInfo
        """
        return ProjectInfo(
            project_id='SEASONAL',
            cmor_setup={
                'mip_table_dir': SEASONAL_MIP_TABLE_DIR,
                'netcdf_file_action': 'CMOR_REPLACE_4',
            },
            cmor_dataset={
                'grid': 'not checked',
                'branch_method': 'no parent',
                'experiment_id': 'amip',
                'license': CMIP6_LICENSE,
                'mip': 'CMIP',
                'mip_era': 'SEASONAL',
                'model_id': 'UKESM1-0-LL',
                'model_type': 'AGCM',
                'nominal_resolution': '5 km',
                'sub_experiment_id': 'none',
                'variant_label': 'r1i1p1f1'
            },
            request={
                'base_date': '2000-01-01T00:00:00'
            },
            global_attributes={
                'further_info_url': 'https://furtherinfo.es-doc.org/CMIP6.MOHC.UKESM1-0-LL.amip.none.r1i1p1f1'
            }
        )

    @classmethod
    def nahosmip_project_info(cls) -> 'ProjectInfo':
        """
        Returns all common values that are specific for CMIP6 projects.

        :return: Values that are specific for CMIP6 projects
        :rtype: ProjectInfo
        """
        return ProjectInfo(
            project_id='NAHosMIP',
            cmor_setup={
                'mip_table_dir': NAHOSMIP_MIP_TABLE_DIR,
                'netcdf_file_action': 'CMOR_REPLACE_4',
            },
            cmor_dataset={
                'grid': 'not checked',
                'branch_method': 'no parent',
                'experiment_id': 'amip',
                'license': GCMODELDEV_LICENSE,
                'mip': 'NAHosMIP',
                'mip_era': 'GCModelDev',
                'model_id': 'UKESM1-0-LL',
                'model_type': 'AGCM',
                'nominal_resolution': '5 km',
                'sub_experiment_id': 'none',
                'variant_label': 'r1i1p1f1'
            },
            request={
                'base_date': '1850-01-01T00:00:00'
            },
            global_attributes={
                'further_info_url': 'https://furtherinfo.es-doc.org/CMIP6.MOHC.UKESM1-0-LL.amip.none.r1i1p1f1'
            }
        )


@dataclass
class SpecificInfo:
    common: Dict[str, Any] = field(default_factory=dict)
    cmor_setup: Dict[str, Any] = field(default_factory=dict)
    cmor_dataset: Dict[str, Any] = field(default_factory=dict)
    request: Dict[str, Any] = field(default_factory=dict)
    streams: Dict[str, Dict[str, str]] = field(default_factory=dict)
    other: Dict[str, Any] = field(default_factory=dict)
    global_attributes: Dict[str, Any] = field(default_factory=dict)
    masking: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    halo_removal: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Dict[str, Any]]:
        """
        Returns the information as a directory using the MIP configuration structure as template, e.g.:
        {
            'common': {
                'test_location': '/path/to/specific/test/location'
            }
            'cmor_setup': {
                'netcdf_file_action': 'CMOR_REPLACE_3'
            },
            'cmor_data_set': {
                'branch_method': 'standard'
            },
            'request': {
                'base_date': '2000-01-01T00:00:00'
            },
            'streams_ap4': {
                'CMIP6_Emon': 'taxmas'
            }
            'global_attributes': {
                'further_info_url': 'https://furtherinfo.es-doc.org/CMIP6.MOHC.UKESM1-0-LL.amip.none.r1i1p1f1'
            },
            masking: {

            },
            halo_removal: {
            },
            'other': {
            }
        }

        :return: Values as directory (like Mip configuration)
        :rtype: Dict[str, Any]
        """
        excludes = ['common', 'project_id', 'streams', 'masking', 'halo_removal']
        items = {
            k: v for k, v in asdict(self).items() if v and k not in excludes
        }
        items['COMMON'] = self.common

        stream_key = 'stream_{}'
        stream_items = {
            stream_key.format(k): v for k, v in self.streams.items()
        }
        items.update(stream_items)

        if len(self.masking) > 0:
            items['masking'] = self.masking_as_dict()

        if len(self.halo_removal) > 0:
            items['halo_removal'] = self.removal_as_dict()

        return items

    def masking_as_dict(self):
        items = {}
        masking_key = 'stream_{}_{}'
        for stream, grid_masking in self.masking.items():
            for grid, value in grid_masking.items():
                key = masking_key.format(stream, grid)
                items[key] = value
        return items

    def removal_as_dict(self):
        items = {}
        removal_key = 'stream_{}'
        for stream, value in self.halo_removal.items():
            key = removal_key.format(stream)
            items[key] = value
        return items


@dataclass
class AbstractTestData(ABC):
    """
    Abstract class for storing test data
    """
    project_id: str = ''
    mip_table: str = ''
    variables: List[str] = field(default_factory=list)
    common_info: CommonInfo = field(default_factory=lambda: CommonInfo())
    project_info: ProjectInfo = None
    specific_info: SpecificInfo = None

    def as_list_dicts(self) -> List[Dict[str, Dict[str, Any]]]:
        """
        Returns a list containing the dictionaries of the common information, the project specific information
        and the specific information of the current test data.

        :return: List of dictionaries containing common information, project specific information and specific
                 information of the test data
        :rtype: List[Dict[str, Dict[str, Any]]]
        """
        return [self.common_info.as_dict(), self.project_info.as_dict(), self.specific_info.as_dict()]


@dataclass
class Cmip6TestData(AbstractTestData):
    """
    Stores test data for CMIP6 projects
    """
    project_id: str = field(init=False, default_factory=lambda: 'CMIP6')
    common_info: CommonInfo = field(init=False, default_factory=lambda: CommonInfo.default_common_info())
    project_info: ProjectInfo = field(init=False, default_factory=lambda: ProjectInfo.cmip6_project_info())
    specific_info: SpecificInfo = None


@dataclass
class HiResTestData(AbstractTestData):
    """
    Stores test data for CMIP6 projects
    """
    project_id: str = field(init=False, default_factory=lambda: 'HIRES')
    common_info: CommonInfo = field(init=False, default_factory=lambda: CommonInfo.default_common_info())
    project_info: ProjectInfo = field(init=False, default_factory=lambda: ProjectInfo.hires_project_info())
    specific_info: SpecificInfo = None


@dataclass
class SeasonalTestData(AbstractTestData):
    """
    Stores test data for CMIP6 projects
    """
    project_id: str = field(init=False, default_factory=lambda: 'SEASONAL')
    common_info: CommonInfo = field(init=False, default_factory=lambda: CommonInfo.default_common_info())
    project_info: ProjectInfo = field(init=False, default_factory=lambda: ProjectInfo.seasonal_project_info())
    specific_info: SpecificInfo = None


@dataclass
class AriseTestData(AbstractTestData):
    """
    Stores test data for CMIP6 projects
    """
    project_id: str = field(init=False, default_factory=lambda: 'ARISE')
    common_info: CommonInfo = field(init=False, default_factory=lambda: CommonInfo.default_common_info())
    project_info: ProjectInfo = field(init=False, default_factory=lambda: ProjectInfo.arise_project_info())
    specific_info: SpecificInfo = None


@dataclass
class CordexTestData(AbstractTestData):
    """
    Stores test data for CMIP6 projects
    """
    project_id: str = field(init=False, default_factory=lambda: 'CORDEX-CMIP6')
    common_info: CommonInfo = field(init=False, default_factory=lambda: CommonInfo.default_common_info())
    project_info: ProjectInfo = field(init=False, default_factory=lambda: ProjectInfo.cordex_project_info())
    specific_info: SpecificInfo = None


@dataclass
class NAHosMIPTestData(AbstractTestData):
    """
    Stores test data for CMIP6 projects
    """
    project_id: str = field(init=False, default_factory=lambda: 'NAHosMIP')
    common_info: CommonInfo = field(init=False, default_factory=lambda: CommonInfo.default_common_info())
    project_info: ProjectInfo = field(init=False, default_factory=lambda: ProjectInfo.nahosmip_project_info())
    specific_info: SpecificInfo = None
