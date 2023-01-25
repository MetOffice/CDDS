# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.
# mypy: ignore-errors
# Ignore errors because code is old and will be updated soon
import re
from abc import ABCMeta, abstractmethod
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, List, Tuple

from cftime import Datetime360Day

from cdds.archive.constants import OUTPUT_FILE_DT_STR

if TYPE_CHECKING:
    from cdds.common.request import Request


class ModelFileInfo(object, metaclass=ABCMeta):
    """
    Provides methods to manage and check netCDF files from simulation models
    """

    @property
    @abstractmethod
    def mass_location_facet(self) -> str:
        pass

    @property
    @abstractmethod
    def mass_root_location_facet(self) -> str:
        pass

    @property
    @abstractmethod
    def _nc_files_to_archive_regex(self) -> str:
        pass

    @abstractmethod
    def is_cmor_file(self, filename: str) -> bool:
        """
        Checks if the given file name matches the expected cmor file name pattern.

        :param filename: File name to check
        :type filename: str
        :return: True if the file name matches the expected cmor file name pattern, otherwise False
        :rtype: bool
        """
        pass

    @abstractmethod
    def is_relevant_for_archiving(self, request: 'Request', out_var_name: str, mip_table_id: str, nc_file: str) -> bool:
        """
        Checks if the given |Output netCDF file| is ready for archiving by checking if it matches
        the expected file pattern by using the given information of the request, MIP table ID and
        output variable name.

        :param request: The information about the request being processed
        :type request: Request
        :param out_var_name: Expected output variable name
        :type out_var_name: str
        :param mip_table_id: Expected MIP table ID
        :type mip_table_id: str
        :param nc_file: Path to the netCDF file to archive
        :type nc_file: str
        :return: True if the netCDF file can be archived otherwise False
        :rtype: bool
        """
        pass

    def get_date_range(self, nc_files: List[str], frequency: str) -> Tuple[Datetime360Day, Datetime360Day]:
        """
        Calculates the date range for the given |Output netCDF files|. It is assumed this set of files
        has been through the CDDS quality control process and represents a contiguous dataset, so this
        is not checked.

        :param nc_files: A list of filenames that have been checked for valid formatting.
        :type nc_files: List[str]
        :param frequency: A string describing the output frequency for the variables, which is used
                          to determine the expected datestamp format used in the filename.
        :type frequency: str
        :return: A tuple of cftime objects representing the start and end of the date range.
        :rtype: Tuple[Datetime360Day, Datetime360Day]
        """
        filename_pattern = re.compile(self._nc_files_to_archive_regex)
        file_match = filename_pattern.search(nc_files[0])
        file_start = datetime.strptime(file_match.group('start_date'), OUTPUT_FILE_DT_STR[frequency]['str'])
        start_date = Datetime360Day(file_start.year, file_start.month, file_start.day)

        file_end = datetime.strptime(file_match.group('end_date'), OUTPUT_FILE_DT_STR[frequency]['str'])

        # For subhrPt frequency the seconds can be either the model time step or the radiation time step (1hr)
        seconds_for_delta = OUTPUT_FILE_DT_STR[frequency]['delta'][1]
        if seconds_for_delta is None:
            last_file_end = re.search(self._nc_files_to_archive_regex, nc_files[-1]).group('end_date')
            # Assuming all time steps are an integer number of minutes
            seconds_for_delta = 60 * (60 - int(last_file_end[10:12]))

        # for the end date, we want the start of the next day for easier processing.
        # So if the range is 20100101-20191230, use 20200101 as the end date.
        delta_to_add = timedelta(days=OUTPUT_FILE_DT_STR[frequency]['delta'][0], seconds=seconds_for_delta)
        end_date = (Datetime360Day(file_end.year, file_end.month, file_end.day) + delta_to_add)
        valid_files = [data_file for data_file in nc_files if filename_pattern.search(data_file)]

        for current_file in valid_files:
            current_match = filename_pattern.search(current_file)
            file_start = datetime.strptime(current_match.group('start_date'), OUTPUT_FILE_DT_STR[frequency]['str'])
            current_start_date = Datetime360Day(file_start.year,
                                                file_start.month,
                                                file_start.day,
                                                file_start.hour,
                                                file_start.minute,
                                                )
            if current_start_date < start_date:
                start_date = current_start_date
            file_end = datetime.strptime(current_match.group('end_date'), OUTPUT_FILE_DT_STR[frequency]['str'])
            current_end_date = (
                Datetime360Day(file_end.year,
                               file_end.month,
                               file_end.day,
                               file_end.hour,
                               file_end.minute)
                + delta_to_add)
            if current_end_date > end_date:
                end_date = current_end_date
        return start_date, end_date


class GlobalModelFileInfo(ModelFileInfo):
    """
    Provides methods to manage and check netCDF files from global simulation models
    """

    _CMOR_FILENAME_PATTERN = (r'([a-zA-Z0-9]+)_([a-zA-Z0-9]+)_([a-zA-Z0-9-]+)_'
                              r'([a-zA-Z0-9-]+)_(r\d+i\d+p\d+f\d+)_g([a-zA-Z0-9]+)'
                              r'_((\d+)-(\d+))(-clim)?.nc')

    _NC_FILES_TO_ARCHIVE_REGEX = (
        '(?P<out_var_name>[a-zA-Z0-9-]+)_(?P<mip_table_id>[a-zA-Z0-9-]+)_'
        '(?P<model_id>[a-zA-Z0-9-]+)_(?P<experiment_id>[a-zA-Z0-9-]+)_'
        '(?P<variant_label>[a-zA-Z0-9]+)_(?P<grid>[a-zA-Z0-9]+)_'
        '(?P<start_date>[0-9]+)-(?P<end_date>[0-9]+)(?P<climatology>-clim)?.nc')

    _MASS_ROOT_LOCATION_FACET = 'mip_era|mip|institution_id|model_id|experiment_id|variant_label'
    _MASS_SUFFIX_LOCATION_FACET = '|mip_table_id|out_var_name|grid_label'

    def __init__(self):
        super(GlobalModelFileInfo, self).__init__()

    @property
    def mass_location_facet(self) -> str:
        return self._MASS_ROOT_LOCATION_FACET + self._MASS_SUFFIX_LOCATION_FACET

    @property
    def mass_root_location_facet(self) -> str:
        return self._MASS_ROOT_LOCATION_FACET

    @property
    def _nc_files_to_archive_regex(self) -> str:
        return self._NC_FILES_TO_ARCHIVE_REGEX

    def is_cmor_file(self, filename) -> bool:
        """
        Checks if the given file name matches the expected cmor file name pattern.

        :param filename: File name to check
        :type filename: str
        :return: True if the file name matches the expected cmor file name pattern, otherwise False
        :rtype: bool
        """
        return re.match(self._CMOR_FILENAME_PATTERN, filename)

    def is_relevant_for_archiving(self, request: 'Request', out_var_name: str, mip_table_id: str, nc_file: str) -> bool:
        """
        Checks if the given |Output netCDF file| is ready for archiving by checking if it matches
        the expected file pattern by using the given information of the request, MIP table ID and
        output variable name.

        :param request: The information about the request being processed
        :type request: Request
        :param out_var_name: Expected output variable name
        :type out_var_name: str
        :param mip_table_id: Expected MIP table ID
        :type mip_table_id: str
        :param nc_file: Path to the netCDF file to archive
        :type nc_file: str
        :return: True if the netCDF file can be archived otherwise False
        :rtype: bool
        """
        pattern = re.compile(self._NC_FILES_TO_ARCHIVE_REGEX)
        match = pattern.search(nc_file)
        if not match:
            return False
        if request.experiment_id != match.group('experiment_id'):
            return False
        if request.variant_label != match.group('variant_label'):
            return False
        if request.model_id != match.group('model_id'):
            return False
        if out_var_name != match.group('out_var_name'):
            return False
        if mip_table_id != match.group('mip_table_id'):
            return False
        return True


class RegionalModelFileInfo(ModelFileInfo):
    """
    Provides methods to manage and check netCDF files from regional simulation models
    """
    _CMOR_FILENAME_PATTERN = (r'([a-zA-Z0-9]+)_([a-zA-Z0-9-]+)_([a-zA-Z0-9-]+)_([a-zA-Z0-9-]+)_'
                              r'(r\d+i\d+p\d+)_([a-zA-Z0-9-]+)_v([a-zA-Z0-9]+)_([a-zA-Z0-9-]+)'
                              r'_((\d+)-(\d+)).nc')

    _NC_FILES_TO_ARCHIVE_REGEX = (
        '(?P<out_var_name>[a-zA-Z0-9-]+)_(?P<domain>[a-zA-Z0-9-]+)_'
        '(?P<driving_model_id>[a-zA-Z0-9-]+)_(?P<experiment_id>[a-zA-Z0-9-]+)_'
        '(?P<driving_ensemble_member>[a-zA-Z0-9-]+)_(?P<model_id>[a-zA-Z0-9-]+)_'
        '(?P<rcm_version_id>[a-zA-Z0-9]+)_(?P<frequency>[a-zA-Z0-9]+)_'
        '(?P<start_date>[0-9]+)-(?P<end_date>[0-9]+).nc')

    _MASS_ROOT_LOCATION_FACET = ('domain|institution_id|driving_model_id|experiment_id|driving_model_ensemble_member|'
                                 'model_id|rcm_version_id')
    _MASS_SUFFIX_LOCATION_FACET = '|frequency|out_var_name'

    def __init__(self):
        super(RegionalModelFileInfo, self).__init__()

    @property
    def mass_location_facet(self) -> str:
        return self._MASS_ROOT_LOCATION_FACET + self._MASS_SUFFIX_LOCATION_FACET

    @property
    def mass_root_location_facet(self) -> str:
        return self._MASS_ROOT_LOCATION_FACET

    @property
    def _nc_files_to_archive_regex(self) -> str:
        return self._NC_FILES_TO_ARCHIVE_REGEX

    def is_cmor_file(self, filename) -> bool:
        return re.match(self._CMOR_FILENAME_PATTERN, filename)

    def is_relevant_for_archiving(self, request: 'Request', out_var_name: str, mip_table_id: str, nc_file: str) -> bool:
        pattern = re.compile(self._NC_FILES_TO_ARCHIVE_REGEX)
        match = pattern.search(nc_file)
        if not match:
            return False
        if request.experiment_id != match.group('experiment_id'):
            return False
        if request.model_id != match.group('model_id'):
            return False
        if out_var_name != match.group('out_var_name'):
            return False
        return True
