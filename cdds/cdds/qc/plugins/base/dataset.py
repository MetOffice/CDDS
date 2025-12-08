# (C) British Crown Copyright 2017-2025, Met Office.
# Please see LICENSE.md for license details.

import re
import os

from abc import ABCMeta, abstractmethod
from collections import OrderedDict
from cdds.qc.constants import DIURNAL_CLIMATOLOGY, EXCLUDE_DIRECTORIES_REGEXP, FREQ_DICT, SECONDS_IN_DAY
from cdds.qc.common import GlobalAttributesCache


class StructuredDataset(object, metaclass=ABCMeta):
    """A representation of a directory containing a netcdf dataset
    Can be sliced by a MIP table and time period.
    """

    def __init__(self, root, request, mip_tables, mip_table=None, start=None,
                 end=None, logger=None, stream=None):
        """Initializes the dataset.

        Parameters
        ----------
        root: string
            Path to the root directory of the dataset.
        request: cdds.common.request.request.Request
            The |Request| cfg file.
        mip_tables: cdds_qc_plugin_cmip6.MipTables
            An object containing information about mip tables associated with the processed request.
        mip_table: str
            The MIP table to consider if not given all will consider.
        start: string
            A string representation of a date being the start of a date
            range.
        end: string
            A string representation of a date being the end of a date
            range.
        logger: logging.Logger
            A logger instance
        stream: str
            The stream to consider.
        """
        if not os.path.isdir(root):
            raise Exception("{} is not a directory".format(root))
        self._root = os.path.join(root, '')
        self._request = request
        self._file_count = 0
        self._mip_table = mip_table
        self._start = start
        self._end = end
        self._loader_class = None
        self._mip_tables = mip_tables
        self._stream = stream
        self._logger = logger
        self._dataset = []
        self._aggregated = {}
        self._var_names = {}
        self.global_attributes_cache = GlobalAttributesCache()

    @classmethod
    @abstractmethod
    def is_responsible(cls, project):
        pass

    @property
    def stream(self):
        return self._stream

    @property
    def mip_table(self):
        return self._mip_table if self._mip_table is not None else "all"

    @property
    def request(self):
        return self._request

    @property
    def root(self):
        return self._root

    @property
    def filepaths(self):
        return self._dataset

    @property
    def file_count(self):
        return self._file_count

    @property
    def var_names(self):
        return self._var_names

    @abstractmethod
    def load_dataset(self, loader_class):
        pass

    def check_filenames_and_sizes(self):
        """Tests all filenames and file sizes in this dataset

        Returns
        -------
        dict :
            A dictionary of error messages corresponding to each file
        """

        errors = {}
        for fp in self._dataset:
            try:
                ds = self._loader_class(fp)
                _, messages = self.check_filename(ds, os.path.basename(fp))
                file_size = os.path.getsize(fp)
                if file_size > self._request.data.max_file_size:
                    messages.append(
                        "The size of the file {} ({} bytes) exceeds the limit of {} bytes"
                        "".format(fp, file_size, self._request.data.max_file_size)
                    )
                if messages:
                    errors[fp] = messages
                ds.close()
            except IOError:
                self._logger.error("Unable to load file {}".format(fp))
        return errors

    @abstractmethod
    def check_filename(self, ds, filename):
        pass

    def get_aggregated_files(self, chunked_only=True):
        if chunked_only:
            ret = {}
            for key in self._aggregated:
                if len(self._aggregated[key]) > 1:
                    ret[key] = self._aggregated[key]
            return ret
        else:
            return self._aggregated

    def variable_time_axis(self, var_key, atmos_timestep):
        """Extracts time axis and bounds (if they exist) from a netcdf file, along with corresponding frequency code.
        Axes and bounds are ordered dictionaries indexed with names of the files from which they have been extracted,
        the assumption is that for CMIP6-like output standard filename ordering will correspond to time ordering.

        Parameters
        ==========
        var_key: str
            Variable id
        atmos_timestep: int
            Atmospheric time step in seconds

        Returns
        =======
        : tuple
            Time axis dict, time bounds dict, frequency code
        """
        filepaths = sorted(self._aggregated[var_key])
        # we make assumption that filenames are sortable and their order should correspond to concatenated time axis
        # order. This is generally true for CMIP-like filenames with YYYYMMDD-type dates in filenames.
        time_axis = OrderedDict()
        time_bnds = OrderedDict()
        frequency = None
        for filepath in filepaths:
            with self._loader_class(filepath) as nc_file:
                time_axis[filepath] = nc_file.variables["time"][:].data
                if "time_bnds" in nc_file.variables:
                    time_bnds[filepath] = nc_file.variables["time_bnds"][:].data
                frequency_code = self.global_attributes_cache.getncattr("frequency", nc_file)
                if frequency_code == 'subhrPt':
                    if variable_id.startswith("rs") or variable_id.startswith("rl"):
                        # despite the frequency code, radiation variables are on hourly timepoints
                        frequency = 'PT1H'
                    else:
                        # the rest are reported once per timestep
                        frequency = 'PT{}S'.format(atmos_timestep)
                elif frequency_code == DIURNAL_CLIMATOLOGY:
                    frequency = DIURNAL_CLIMATOLOGY
                    time_bnds[filepath] = nc_file.variables["climatology_bnds"][:].data
                else:
                    frequency = FREQ_DICT[self.global_attributes_cache.getncattr("frequency", nc_file)]
        if len(time_bnds.keys()) == 0:
            time_bnds = None
        return (time_axis, time_bnds, frequency)

    @abstractmethod
    def _aggregate_files(self):
        pass

    def walk_directory(self):
        """Traverses a base directory and adds netcdf files to the dataset

        Parameters
        ----------
        basedir: str
            Dataset root directory
        mip_table: str
            If set, only files belonging to this |MIP Table| will be
            included
        start: str
            Date in YYYMM[DD] format, if set only files in this daterange
            will be included.
        end: str
            Date in YYYMM[DD] format, if set only files in this daterange
            will be included.

        Returns
        -------
        : list
            List of filepaths to the dataset.
        """
        dataset = []
        for root, _, files in os.walk(self._root):
            if re.search(EXCLUDE_DIRECTORIES_REGEXP, root):
                continue
            for filename in files:
                if filename.endswith(".nc") and \
                        ((self._mip_table is None or
                          "_{}_".format(self._mip_table) in filename) and
                         (self._stream is None or
                          "/output/{}/".format(self._stream) in root)):
                    m = re.match(r"^.+_(\d{6,8})-(\d{6,8})\.nc$", filename)
                    # it does not have to match if start and end are None
                    if (self._start is None and self._end is None) or\
                            (m and int(m.group(1)) >= int(self._start) and
                             int(m.group(2)) <= int(self._end)):
                        dataset.append(os.path.join(root, filename))
                        self._file_count += 1
                        # Log version.
        self._logger.info('Added {} files to the dataset'.format(
            self._file_count))
        return dataset
