# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.
import re
from abc import ABCMeta, abstractmethod
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, List, Tuple

from cftime import Datetime360Day

from cdds.archive.constants import OUTPUT_FILE_DT_STR

if TYPE_CHECKING:
    from cdds.common.request import Request


class ModelFileInfo(object, metaclass=ABCMeta):

    @abstractmethod
    def is_cmor_file(self, filename: str) -> bool:
        pass

    @abstractmethod
    def is_relevant_for_archiving(self, request: 'Request', out_var_name: str, mip_table_id: str, nc_file: str) -> bool:
        pass

    @abstractmethod
    def get_date_range(self, nc_files: List[str], frequency: str) -> Tuple[Datetime360Day, Datetime360Day]:
        pass


class GlobalModelFileInfo(ModelFileInfo):
    CMOR_FILENAME_PATTERN = (r'([a-zA-Z0-9]+)_([a-zA-Z0-9]+)_([a-zA-Z0-9-]+)_'
                             r'([a-zA-Z0-9-]+)_(r\d+i\d+p\d+f\d+)_g([a-zA-Z0-9]+)'
                             r'_((\d+)-(\d+))(-clim)?.nc')

    NC_FILES_TO_ARCHIVE_REGEX = (
        '(?P<out_var_name>[a-zA-Z0-9-]+)_(?P<mip_table_id>[a-zA-Z0-9-]+)_'
        '(?P<model_id>[a-zA-Z0-9-]+)_(?P<experiment_id>[a-zA-Z0-9-]+)_'
        '(?P<variant_label>[a-zA-Z0-9]+)_(?P<grid>[a-zA-Z0-9]+)_'
        '(?P<start_date>[0-9]+)-(?P<end_date>[0-9]+)(?P<climatology>-clim)?.nc')

    def __init__(self):
        super(GlobalModelFileInfo, self).__init__()

    def is_cmor_file(self, filename) -> bool:
        return re.match(self.CMOR_FILENAME_PATTERN, filename)

    def is_relevant_for_archiving(self, request: 'Request', out_var_name: str, mip_table_id: str, nc_file: str) -> bool:
        pattern = re.compile(self.NC_FILES_TO_ARCHIVE_REGEX)
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

    def get_date_range(self, nc_files: List[str], frequency: str) -> Tuple[Datetime360Day, Datetime360Day]:
        """
        Calculate the date range for the this set of |Output netCDF files|. It
        is assumed this set of files has been through the CDDS quality control
        process and represents a contiguous dataset, so this is not checked.

        Parameters
        ----------
        nc_files: list
            A list of filenames that have been checked for valid formatting.
        frequency: str
            A string describing the output frequency for the variables, which is
            used to determine the expected datestamp format used in the filename.

        Returns
        -------
        : tuple
            A tuple of cftime objects representing the start and end of the date
            range.
        """
        filename_pattern = re.compile(self.NC_FILES_TO_ARCHIVE_REGEX)
        file_match = filename_pattern.search(nc_files[0])
        file_start = datetime.strptime(file_match.group('start_date'), OUTPUT_FILE_DT_STR[frequency]['str'])
        start_date = Datetime360Day(file_start.year, file_start.month, file_start.day)

        file_end = datetime.strptime(file_match.group('end_date'), OUTPUT_FILE_DT_STR[frequency]['str'])

        # For subhrPt frequency the seconds can be either the model time step or the radiation time step (1hr)
        seconds_for_delta = OUTPUT_FILE_DT_STR[frequency]['delta'][1]
        if seconds_for_delta is None:
            last_file_end = re.search(self.NC_FILES_TO_ARCHIVE_REGEX, nc_files[-1]).group('end_date')
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


class RegionalModelFileInfo(ModelFileInfo):

    def __init__(self):
        super(RegionalModelFileInfo, self).__init__()

    def is_cmor_file(self, filename) -> bool:
        # Not implemented yet
        return None

    def is_relevant_for_archiving(self, request: 'Request', out_var_name: str, mip_table_id: str, nc_file: str) -> bool:
        # Not implemented yet
        return None

    def get_date_range(self, nc_files: List[str], frequency: str) -> Tuple[Datetime360Day, Datetime360Day]:
        # Not implemented yet
        return None, None
