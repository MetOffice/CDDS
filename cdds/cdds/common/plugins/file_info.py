# (C) British Crown Copyright 2023-2025, Met Office.
# Please see LICENSE.md for license details.
# mypy: ignore-errors
# Ignore errors because code is old and will be updated soon
import os.path
import re
from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, List, Tuple, Dict

from metomi.isodatetime.data import TimePoint, Duration
from metomi.isodatetime.parsers import TimePointParser

from cdds.archive.constants import OUTPUT_FILE_DT_STR

# Only used for type hints: There would be a package cycle otherwise
if TYPE_CHECKING:
    from cdds.common.request.request import Request


class ModelFileInfo(object, metaclass=ABCMeta):
    """
    Provides methods to manage and check netCDF files from simulation models
    """

    @abstractmethod
    def mass_location_suffix(
            self, request: 'Request', mip_table: str, variable: str, grid_label: str, frequency: str) -> str:
        """
        Returns the suffix to the MASS location for the simulation model files of a variable

        :param request: The information about the request being processed
        :type request: Request
        :param mip_table: MIP table
        :type mip_table: str
        :param variable: Variable
        :type variable: str
        :param grid_label: Grid label
        :type grid_label: str
        :param frequency: Frequency of the variable
        :type: str
        :return: The suffix to the MASS location for the simulation model files of a variable
        :rtype: str
        """
        pass

    @abstractmethod
    def mass_root_location_suffix(self, request: 'Request') -> str:
        """
        Returns the suffix to the MASS root location that contains all simulation model files

        :param request: The information about the request being processed
        :type request: Request
        :return: The suffix to the MASS root location containing all simulation model files
        :rtype: str
        """
        pass

    @property
    @abstractmethod
    def _nc_files_to_archive_regex(self) -> str:
        pass

    @property
    @abstractmethod
    def output_file_template(self) -> str:
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
    def is_relevant_for_archiving(
            self, request: 'Request', variable_dict: Dict[str, str], nc_file: str) -> bool:
        """
        Checks if the given |Output netCDF file| is ready for archiving by checking if it matches the expected
        file pattern by using the given information of the request and variable information.

        :param request: The information about the request being processed
        :type request: old_request.Request
        :param variable_dict: Information about the MIP approved variable
        :type variable_dict: Dict[str, str]
        :param nc_file: Path to the netCDF file to archive
        :type nc_file: str
        :return: True if the netCDF file can be archived otherwise False
        :rtype: bool
        """
        pass

    def get_date_range(self, nc_files: List[str], frequency: str) -> Tuple[TimePoint, TimePoint]:
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
        :rtype: Tuple[TimePoint, TimePoint]
        """
        filename_pattern = re.compile(self._nc_files_to_archive_regex)
        file_match = filename_pattern.search(nc_files[0])
        file_start = TimePointParser().strptime(file_match.group('start_date'),
                                                strptime_format_string=OUTPUT_FILE_DT_STR[frequency]['str'])
        start_date = TimePoint(year=file_start.year, month_of_year=file_start.month_of_year,
                               day_of_month=file_start.day_of_month)

        file_end = TimePointParser().strptime(file_match.group('end_date'),
                                              strptime_format_string=OUTPUT_FILE_DT_STR[frequency]['str'])

        # For subhrPt frequency the seconds can be either the model time step or the radiation time step (1hr)
        seconds_for_delta = OUTPUT_FILE_DT_STR[frequency]['delta'][1]
        if seconds_for_delta is None:
            last_file_end = re.search(self._nc_files_to_archive_regex, nc_files[-1]).group('end_date')
            # Assuming all time steps are an integer number of minutes
            seconds_for_delta = 60 * (60 - int(last_file_end[10:12]))

        # for the end date, we want the start of the next day for easier processing.
        # So if the range is 20100101-20191230, use 20200101 as the end date.
        delta_to_add = Duration(days=OUTPUT_FILE_DT_STR[frequency]['delta'][0], seconds=seconds_for_delta)
        file_end_date = TimePoint(year=file_end.year, month_of_year=file_end.month_of_year,
                                  day_of_month=file_end.day_of_month)
        end_date = file_end_date + delta_to_add
        valid_files = [data_file for data_file in nc_files if filename_pattern.search(data_file)]

        for current_file in valid_files:
            current_match = filename_pattern.search(current_file)
            file_start = TimePointParser().strptime(current_match.group('start_date'),
                                                    strptime_format_string=OUTPUT_FILE_DT_STR[frequency]['str'])
            current_start_date = TimePoint(year=file_start.year,
                                           month_of_year=file_start.month_of_year,
                                           day_of_month=file_start.day_of_month,
                                           hour_of_day=file_start.hour_of_day,
                                           minute_of_hour=file_start.minute_of_hour,
                                           )
            if current_start_date < start_date:
                start_date = current_start_date
            file_end = TimePointParser().strptime(current_match.group('end_date'),
                                                  strptime_format_string=OUTPUT_FILE_DT_STR[frequency]['str'])
            current_end_date = file_end + delta_to_add
            if current_end_date > end_date:
                end_date = current_end_date
        return start_date, end_date


class GlobalModelFileInfo(ModelFileInfo):
    """
    Provides methods to manage and check netCDF files from global simulation models
    """

    _CMOR_FILENAME_PATTERN = (r'([a-zA-Z0-9]+)_([a-zA-Z0-9]+)_([a-zA-Z0-9-]+)_'
                              r'([a-zA-Z0-9-]+)_([a-zA-Z0-9]+-)?(r\d+i\d+p\d+f\d+)_g([a-zA-Z0-9]+)'
                              r'_((\d+)-(\d+))(-clim)?.nc')

    _NC_FILES_TO_ARCHIVE_REGEX = (
        '(?P<out_var_name>[a-zA-Z0-9-]+)_(?P<mip_table_id>[a-zA-Z0-9-]+)_'
        '(?P<model_id>[a-zA-Z0-9-]+)_(?P<experiment_id>[a-zA-Z0-9-]+)_'
        '(?P<variant_label>[a-zA-Z0-9-]+)_(?P<grid>[a-zA-Z0-9]+)_'
        '(?P<start_date>[0-9]+)-(?P<end_date>[0-9]+)(?P<climatology>-clim)?.nc')

    _MASS_ROOT_LOCATION_FACET = 'mip_era|mip|institution_id|model_id|experiment_id|variant_label'
    _MASS_SUFFIX_LOCATION_FACET = '|mip_table_id|out_var_name|grid_label'

    def __init__(self):
        super(GlobalModelFileInfo, self).__init__()

    def mass_location_suffix(
            self, request: 'Request', mip_table: str, variable: str, grid_label: str, frequency: str) -> str:
        """
        Returns the suffix to the MASS location for the simulation model files of a variable

        :param request: The information about the request being processed
        :type request: Request
        :param mip_table: MIP table
        :type mip_table: str
        :param variable: Variable
        :type variable: str
        :param grid_label: Grid label
        :type grid_label: str
        :param frequency: Frequency of the variable
        :type: str
        :return: The suffix to the MASS location for the simulation model files of a variable
        :rtype: str
        """
        mass_root_location = self.mass_root_location_suffix(request)
        return os.path.join(mass_root_location, mip_table, variable, grid_label)

    def mass_root_location_suffix(self, request: 'Request') -> str:
        """
        Returns the suffix to the MASS root location that contains all simulation model files

        :param request: The information about the request being processed
        :type request: Request
        :return: The suffix to the MASS root location containing all simulation model files
        :rtype: str
        """
        return os.path.join(
            request.metadata.mip_era,
            request.metadata.mip,
            request.metadata.institution_id,
            request.metadata.model_id,
            request.metadata.experiment_id,
            request.metadata.variant_label
        )

    @property
    def _nc_files_to_archive_regex(self) -> str:
        return self._NC_FILES_TO_ARCHIVE_REGEX

    @property
    def output_file_template(self) -> str:
        return ''

    def is_cmor_file(self, filename) -> bool:
        """
        Checks if the given file name matches the expected cmor file name pattern.

        :param filename: File name to check
        :type filename: str
        :return: True if the file name matches the expected cmor file name pattern, otherwise False
        :rtype: bool
        """
        return re.match(self._CMOR_FILENAME_PATTERN, filename)

    def is_relevant_for_archiving(
            self, request: 'Request', variable_dict: Dict[str, str], nc_file: str) -> bool:
        """
        Checks if the given |Output netCDF file| is ready for archiving by checking if it matches the expected
        file pattern by using the given information of the request and variable information.

        :param request: The information about the request being processed
        :type request: Request
        :param variable_dict: Information about the MIP approved variable
        :type variable_dict: Dict[str, str]
        :param nc_file: Path to the netCDF file to archive
        :type nc_file: str
        :return: True if the netCDF file can be archived otherwise False
        :rtype: bool
        """
        pattern = re.compile(self._NC_FILES_TO_ARCHIVE_REGEX)
        match = pattern.search(nc_file)
        if not match:
            return False
        if request.metadata.experiment_id != match.group('experiment_id'):
            return False
        if (request.metadata.sub_experiment_id == 'none' and
                request.metadata.variant_label != match.group('variant_label')):
            return False
        if (request.metadata.sub_experiment_id != 'none' and
                match.group('variant_label') !=
                '{}-{}'.format(request.metadata.sub_experiment_id, request.metadata.variant_label)):
            return False
        if request.metadata.model_id != match.group('model_id'):
            return False
        if variable_dict['out_var_name'] != match.group('out_var_name'):
            return False
        if variable_dict['mip_table_id'] != match.group('mip_table_id'):
            return False
        return True


class RegionalModelFileInfo(ModelFileInfo):
    """
    Provides methods to manage and check netCDF files from regional simulation models
    """

    _CMOR_FILENAME_PATTERN = (r'([a-zA-Z0-9]+)_([a-zA-Z0-9-]+)_([a-zA-Z0-9-]+)_([a-zA-Z0-9-]+)_'
                              r'(r\d+i\d+p\d+f\d+)_([a-zA-Z0-9-]+)_([a-zA-Z0-9-]+)_([a-zA-Z0-9-]+)_'
                              r'([a-zA-Z0-9-]+)_((\d+)-(\d+)).nc')

    _NC_FILES_TO_ARCHIVE_REGEX = ('(?P<out_var_name>[a-zA-Z0-9-]+)_'
                                  '(?P<domain_id>[a-zA-Z0-9-]+)_'
                                  '(?P<driving_model_id>[a-zA-Z0-9-]+)_'
                                  '(?P<driving_experiment>[a-zA-Z0-9-]+)_'
                                  '(?P<driving_variant_label>[a-zA-Z0-9-]+)_'
                                  '(?P<institution_id>[a-zA-Z0-9-]+)_'
                                  '(?P<model_id>[a-zA-Z0-9-]+)_'
                                  '(?P<version>[a-zA-Z0-9-]+)_'
                                  '(?P<frequency>[a-zA-Z0-9-]+)_'
                                  '(?P<start_date>[0-9]+)-(?P<end_date>[0-9]+).nc')

    _OUTPUT_FILE_TEMPLATE = ('<variable_id><domain_id><driving_source_id><driving_experiment_id><driving_variant_label>'
                             '<institution_id><source_id><version_realization><frequency>')

    def __init__(self):
        super(RegionalModelFileInfo, self).__init__()

    def mass_location_suffix(
            self, request: 'Request', mip_table: str, variable: str, grid_label: str, frequency: str) -> str:
        """
        Returns the suffix to the MASS location for the simulation model files of a variable

        :param request: The information about the request being processed
        :type request: Request
        :param mip_table: MIP table
        :type mip_table: str
        :param variable: Variable
        :type variable: str
        :param grid_label: Grid label
        :type grid_label: str
        :param frequency: Frequency of the variable
        :type: str
        :return: The suffix to the MASS location for the simulation model files of a variable
        :rtype: str
        """
        mass_root_location = self.mass_root_location_suffix(request)
        return os.path.join(
            mass_root_location,
            frequency,
            variable
        )

    def mass_root_location_suffix(self, request: 'Request') -> str:
        """
        Returns the suffix to the MASS root location that contains all simulation model files

        :param request: The information about the request being processed
        :type request: Request
        :return: The suffix to the MASS root location containing all simulation model files
        :rtype: str
        """

        return os.path.join(
            request.netcdf_global_attributes.attributes['project_id'],
            request.metadata.mip_era,
            request.metadata.mip,
            request.netcdf_global_attributes.attributes['domain'],
            request.metadata.institution_id,
            request.netcdf_global_attributes.attributes['driving_source_id'],
            request.netcdf_global_attributes.attributes['driving_experiment'],
            request.netcdf_global_attributes.attributes['driving_variant_label'],
            request.metadata.model_id,
            request.netcdf_global_attributes.attributes['version_realization']
        )

    @property
    def _nc_files_to_archive_regex(self) -> str:
        return self._NC_FILES_TO_ARCHIVE_REGEX

    @property
    def output_file_template(self) -> str:
        return self._OUTPUT_FILE_TEMPLATE

    def is_cmor_file(self, filename) -> bool:
        """
        Checks if the given file name matches the expected cmor file name pattern.

        :param filename: File name to check
        :type filename: str
        :return: True if the file name matches the expected cmor file name pattern, otherwise False
        :rtype: bool
        """
        return re.match(self._CMOR_FILENAME_PATTERN, filename)

    def is_relevant_for_archiving(
            self, request: 'Request', variable_dict: Dict[str, str], nc_file: str) -> bool:
        """
        Checks if the given |Output netCDF file| is ready for archiving by checking if it matches the expected
        file pattern by using the given information of the request and variable information.

        :param request: The information about the request being processed
        :type request: Request
        :param variable_dict: Information about the MIP approved variable
        :type variable_dict: Dict[str, str]
        :param nc_file: Path to the netCDF file to archive
        :type nc_file: str
        :return: True if the netCDF file can be archived otherwise False
        :rtype: bool
        """
        global_attributes = request.items_global_attributes
        pattern = re.compile(self._NC_FILES_TO_ARCHIVE_REGEX)
        match = pattern.search(nc_file)
        if not match:
            return False
        if request.metadata.model_id != match.group('model_id'):
            return False
        if variable_dict['out_var_name'] != match.group('out_var_name'):
            return False
        if global_attributes['driving_experiment'] != match.group('driving_experiment'):
            return False
        return True
