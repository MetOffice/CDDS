# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.
import cftime
import datetime
import re

from cdds.archive.constants import OUTPUT_FILE_DT_STR

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, List, Tuple
if TYPE_CHECKING:
    from cdds.common.request import Request


class ModelFileInfo(object, metaclass=ABCMeta):

    @abstractmethod
    def is_cmor_file(self, filename: str) -> bool:
        pass

    @abstractmethod
    def is_relevant_for_archiving(self, request: 'Request', out_var_name: str, mip_table_id: str, path1: str) -> bool:
        pass

    @abstractmethod
    def get_date_range(self, data_files: List[str], frequency: str) -> Tuple[cftime.datetime, cftime.datetime]:
        pass


class GlobalModelFileInfo(ModelFileInfo):
    CMOR_FILENAME_PATTERN = (r'([a-zA-Z0-9]+)_([a-zA-Z0-9]+)_([a-zA-Z0-9-]+)_'
                             r'([a-zA-Z0-9-]+)_(r\d+i\d+p\d+f\d+)_g([a-zA-Z0-9]+)'
                             r'_((\d+)-(\d+))(-clim)?.nc')

    OUTPUT_FILES_REGEX = (
        '(?P<out_var_name>[a-zA-Z0-9-]+)_(?P<mip_table_id>[a-zA-Z0-9-]+)_'
        '(?P<model_id>[a-zA-Z0-9-]+)_(?P<experiment_id>[a-zA-Z0-9-]+)_'
        '(?P<variant_label>[a-zA-Z0-9]+)_(?P<grid>[a-zA-Z0-9]+)_'
        '(?P<start_date>[0-9]+)-(?P<end_date>[0-9]+)(?P<climatology>-clim)?.nc')

    def __init__(self):
        super(GlobalModelFileInfo, self).__init__()

    def is_cmor_file(self, filename) -> bool:
        return re.match(self.CMOR_FILENAME_PATTERN, filename)

    def is_relevant_for_archiving(self, request: 'Request', out_var_name: str, mip_table_id: str, path1: str) -> bool:
        pattern1 = re.compile(self.OUTPUT_FILES_REGEX)
        match1 = pattern1.search(path1)
        if not match1:
            return False
        if request.experiment_id != match1.group('experiment_id'):
            return False
        if request.variant_label != match1.group('variant_label'):
            return False
        if request.model_id != match1.group('model_id'):
            return False
        if out_var_name != match1.group('out_var_name'):
            return False
        if mip_table_id != match1.group('mip_table_id'):
            return False
        return True

    def get_date_range(self, data_files: List[str], frequency: str) -> Tuple[cftime.datetime, cftime.datetime]:
        """
        Calculate the date range for the this set of |Output netCDF files|. It
        is assumed this set of files has been through the CDDS quality control
        process and represents a contiguous dataset, so this is not checked.

        Parameters
        ----------
        data_files: list
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
        fname_pattern = re.compile(self.OUTPUT_FILES_REGEX)
        init_match = fname_pattern.search(data_files[0])
        start_dt = datetime.datetime.strptime(init_match.group('start_date'),
                                              OUTPUT_FILE_DT_STR[frequency]['str'])
        start_cft = cftime.Datetime360Day(start_dt.year, start_dt.month,
                                          start_dt.day)

        end_dt = datetime.datetime.strptime(init_match.group('end_date'),
                                            OUTPUT_FILE_DT_STR[frequency]['str'])

        # For subhrPt frequency the seconds can be either the model timestep or
        # the radiation timestep (1hr)
        seconds_for_delta = OUTPUT_FILE_DT_STR[frequency]['delta'][1]
        if seconds_for_delta is None:
            file_end_date = re.search(self.OUTPUT_FILES_REGEX, data_files[-1]).group('end_date')
            # Assuming all timesteps are an integer number of minutes
            seconds_for_delta = 60 * (60 - int(file_end_date[10:12]))

        # for the end date, we want the start of the next day for easier
        # processing. So if the range is 20100101-20191230, use 20200101 as the
        # end date.
        delta_to_add = datetime.timedelta(
            days=OUTPUT_FILE_DT_STR[frequency]['delta'][0],
            seconds=seconds_for_delta,
        )
        end_cft = (cftime.Datetime360Day(end_dt.year, end_dt.month, end_dt.day) +
                   delta_to_add)
        valid_files = [fn1 for fn1 in data_files if fname_pattern.search(fn1)]

        for current_fname in valid_files:
            current_match = fname_pattern.search(current_fname)
            start_dt = datetime.datetime.strptime(
                current_match.group('start_date'),
                OUTPUT_FILE_DT_STR[frequency]['str'])
            current_start_cft = cftime.Datetime360Day(start_dt.year,
                                                      start_dt.month,
                                                      start_dt.day,
                                                      start_dt.hour,
                                                      start_dt.minute,
                                                      )
            if current_start_cft < start_cft:
                start_cft = current_start_cft
            end_dt = datetime.datetime.strptime(current_match.group('end_date'), OUTPUT_FILE_DT_STR[frequency]['str'])
            current_end_cft = (
                cftime.Datetime360Day(end_dt.year,
                                      end_dt.month,
                                      end_dt.day,
                                      end_dt.hour,
                                      end_dt.minute)
                + delta_to_add)
            if current_end_cft > end_cft:
                end_cft = current_end_cft
        return start_cft, end_cft


class RegionalModelFileInfo(ModelFileInfo):

    def __init__(self):
        super(RegionalModelFileInfo, self).__init__()

    def is_cmor_file(self, filename) -> bool:
        # Not implemented yet
        return None

    def is_relevant_for_archiving(self, request: 'Request', out_var_name: str, mip_table_id: str, path1: str) -> bool:
        # Not implemented yet
        return None

    def get_date_range(self, data_files: List[str], frequency: str) -> Tuple[cftime.datetime, cftime.datetime]:
        # Not implemented yet
        return None, None
