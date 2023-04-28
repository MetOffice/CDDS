# (C) British Crown Copyright 2017-2022, Met Office.
# Please see LICENSE.rst for license details.

import re
import os
from cdds.qc.constants import EXCLUDE_DIRECTORIES_REGEXP, MAX_FILESIZE
from cdds.qc.plugins.cmip6.validators import parse_date_range, ValidationError


class StructuredDataset(object):
    """
    A representation of a directory containing a netcdf dataset
    Can be sliced by a MIP table and time period.
    """

    def __init__(self, root, request, mip_tables, mip_table=None, start=None,
                 end=None, logger=None, stream=None, relaxed_cmor=False):
        """
        Initializes the dataset.

        Parameters
        ----------
        root: string
            Path to the root directory of the dataset.
        request: cdds.common.request.Request
            The |Request| json file.
        mip_table: cdds_qc_plugin_cmip6.MipTables
            An object containing information about mip tables associated with the processed request.
        start: string
            A string representation of a date being the start of a date
            range.
        end: string
            A string representation of a date being the end of a date
            range.
        logger: logging.Logger
            A logger instance
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
        self._relaxed_cmor = relaxed_cmor

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

    def load_dataset(self, loader_class):
        """
        A utility method necessary to make this class testable.
        Walks the root directory and gathers ncdf files.

        Parameters
        ----------
        loader_class : type
            A type of dataset loader (e.g. netCDF4.Dataset)
        """
        self._loader_class = loader_class
        self._dataset = self.walk_directory()
        aggregated, var_names = self._aggregate_files()
        self._aggregated = aggregated
        self._var_names = var_names

    def check_filenames_and_sizes(self):
        """
        Tests all filenames and file sizes in this dataset

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
                if file_size > MAX_FILESIZE:
                    messages.append(
                        "The size of the file {} ({} bytes) "
                        "exceeds the limit of {} bytes".format(
                            fp, file_size, MAX_FILESIZE))
                if messages:
                    errors[fp] = messages
                ds.close()
            except IOError:
                self._logger.error("Unable to load file {}".format(fp))
        return errors

    def check_filename(self, ds, filename):
        """
        Tests filename's facets against a CV, e.g.
        <variable_id>   tas
        <table_id>      Amon
        <source_id>     hadgem3-es
        <experiment_id> piCtrl
        <member_id>     r1i1p1f1
        <grid_label>    gn
        [<time_range>]  201601-210012
        .nc

        Parameters
        ----------
        ds : netCDF4.Dataset
            an open ncdf file
        filename : str
            netcdf filename
        Returns
        -------
        bool, list
            check's results (valid or not) and error messages
        """
        filename_parts = filename.split('.')[0].split('_')
        template_dict = {
            "table_id": 1,
            "source_id": 2,
            "experiment_id": 3,
            "grid_label": 5
        }

        messages = []
        valid_filename = True

        for cv in template_dict:
            try:
                # test it against stored global attribute
                attr = ds.getncattr(cv)
                if attr != filename_parts[template_dict[cv]]:
                    valid_filename = False
                    messages.append(
                        "{}'s value '{}' doesn't match filename {}".format(
                            cv, attr, filename))

            except AttributeError:
                # raised if something's wrong with global attributes
                # it should be validated again by the global attributes checker
                messages.append("Attribute '{}' missing from the ncdf "
                                "file".format(cv))

        # member_id might be just a variant_label or contain a subexperiment_id
        member_id = filename_parts[4].split('-')

        if len(member_id) > 1:
            # subexperiment_id is present
            try:
                if ds.getncattr("sub_experiment_id") == "none":
                    messages.append(
                        "sub_experiment_id present in the filename but "
                        "missing in file's global attributes")
                    valid_filename = False

            except AttributeError:
                # raised if something's wrong with global attributes
                # it should be validated again by the global attributes checker
                messages.append("Attribute 'sub_experiment_id' missing from "
                                "the ncdf file".format(cv))
            label_candidate = member_id[1]

        else:
            # member_id should only contain variant_label
            if (hasattr(ds, "sub_experiment_id") and
                    ds.getncattr("sub_experiment_id") != "none"):
                messages.append(
                    "sub_experiment_id present in file's global attributes "
                    "but missing in the filename")
                valid_filename = False
            label_candidate = member_id[0]
        if re.match(r"^r\d+i\d+p\d+f\d+$", label_candidate) is None:
            valid_filename = False
            messages.append("Invalid variant_label {}".format(label_candidate))
        else:
            variant_label = ds.getncattr("variant_label")
            if variant_label != label_candidate:
                valid_filename = False
                messages.append(
                    "Variant label {} is not consistent with file "
                    "contents ({})".format(label_candidate, variant_label))

        if filename_parts[1] in self._mip_tables.tables:
            if filename_parts[0] not in (
                    self._mip_tables.get_variables(filename_parts[1])):
                valid_filename = False
                messages.append(
                    "Invalid variable {} in the filename {}".format(
                        filename_parts[0], filename))
        else:
            valid_filename = False
            messages.append(
                "Invalid MIP table {} in the filename {}".format(
                    filename_parts[1], filename))
        if len(filename_parts) == 7:
            try:
                _, _ = parse_date_range(filename_parts[6],
                                        ds.getncattr("frequency"))
            except AttributeError:
                messages.append(
                    "Unable to validate filename (frequency not "
                    "present in global attributes)")
            except ValidationError as e:
                valid_filename = False
                messages.append(str(e))
        return valid_filename, messages

    def get_aggregated_files(self, chunked_only=True):
        """
        Returns a dictionary of file aggregated by a key.

        Parameters
        ----------
        chunked_only: bool
            if True, single chunk files won't be returned.

        Returns
        -------
        : dict
            A facet-indexed dictionary.
        """

        if chunked_only:
            ret = {}
            for key in self._aggregated:
                if len(self._aggregated[key]) > 1:
                    ret[key] = self._aggregated[key]
            return ret
        else:
            return self._aggregated

    def _aggregate_files(self):
        """
        Aggregate files in the dataset directory by different facets,
        and corresponding |MIP requested variable name|.

        Returns
        -------
        : (dict, dict)
            Facet-indexed dictionaries
        """

        aggregated_dataset = {}
        variable_names = {}
        self._logger.info("Aggregating files")
        for filepath in self._dataset:
            with self._loader_class(filepath) as ds:
                attrs = [
                    'mip_era',
                    'source_id',
                    'experiment_id',
                    'sub_experiment_id',
                    'table_id',
                    'variant_label',
                    'variable_id',
                    'grid_label',
                ]
                try:
                    file_index = '_'.join([ds.getncattr(x) for x in attrs])
                    try:
                        var_name = ds.getncattr('variable_name')
                    except AttributeError:
                        # Following changes introduced #1052,
                        # the `variable_name` attribute is expected
                        # to be present in all output files.
                        # To make the code backward compatible
                        # with datasets generated pre-1052,
                        # we try to replace it with `variable_id`
                        # when it's not present.
                        # Note that this mean some variables will not pass QC.
                        var_name = ds.getncattr('variable_id')
                    if file_index not in variable_names:
                        variable_names[file_index] = var_name

                    if file_index in aggregated_dataset:
                        aggregated_dataset[file_index].append(filepath)
                    else:
                        aggregated_dataset[file_index] = [filepath]
                except AttributeError as e:
                    self._logger.error(
                        "Error when parsing dataset {}: {}".format(
                            filepath, str(e)))
        return aggregated_dataset, variable_names

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
