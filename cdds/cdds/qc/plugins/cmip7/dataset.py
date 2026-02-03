# (C) British Crown Copyright 2023-2025, Met Office.
# Please see LICENSE.md for license details.

import re
from cdds.qc.plugins.base.dataset import StructuredDataset
from cdds.qc.plugins.cmip6.validators import parse_date_range, ValidationError


class Cmip7Dataset(StructuredDataset):
    """A representation of a directory containing a netcdf dataset
    Can be sliced by a MIP table and time period.
    """

    def __init__(self, root, request, mip_tables, mip_table=None, start=None, end=None, logger=None, stream=None):
        super(Cmip7Dataset, self).__init__(root, request, mip_tables, mip_table, start, end, logger, stream)

    def load_dataset(self, loader_class):
        """A utility method necessary to make this class testable.
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

    @classmethod
    def is_responsible(cls, project):
        return 'cmip6' == project.lower()

    def check_filename(self, ds, filename):
        """Tests filename's facets against a CV, e.g.
        <variable_id>   tasself._loader_class
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
        # tas_tavg-h2m-hxy-u_day_glb_gn_UKESM1-3-LL_1pctCO2_r1i1p1f3_19560101-19561230
        filename_parts = filename.split('.')[0].split('_')
        template_dict = {
            "variable_id": 0,
            "branding_suffix": 1,
            "frequency": 2,
            "region": 3,
            "grid_label": 4,
            "source_id": 5,
            "experiment_id": 6,
            "variant_label": 7,
        }

        messages = []
        valid_filename = True

        for cv in template_dict:
            try:
                # test it against stored global attribute
                attr = self.global_attributes_cache.getncattr(cv, ds)
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
        member_id = filename_parts[7]

        label_candidate = member_id
        if re.match(r"^r\d+i\d+p\d+f\d+$", label_candidate) is None:
            valid_filename = False
            messages.append("Invalid variant_label {}".format(label_candidate))
        else:
            variant_label = self.global_attributes_cache.getncattr("variant_label", ds)
            if variant_label != label_candidate:
                valid_filename = False
                messages.append(
                    "Variant label {} is not consistent with file "
                    "contents ({})".format(label_candidate, variant_label))
        table = self.global_attributes_cache.getncattr("table_id", ds)

        if table in self._mip_tables.tables:
            if filename_parts[0] + "_" + filename_parts[1] not in (
                    self._mip_tables.get_variables(table)):
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
                                        self.global_attributes_cache.getncattr("frequency", ds),
                                        self._request.metadata.calendar)
            except AttributeError:
                messages.append(
                    "Unable to validate filename (frequency not "
                    "present in global attributes)")
            except ValidationError as e:
                valid_filename = False
                messages.append(str(e))

        return valid_filename, messages

    def _aggregate_files(self):
        """Aggregate files in the dataset directory by different facets,
        and corresponding |MIP requested variable name|.

        Returns
        -------
        (dict, dict)
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
                    file_index = '_'.join([self.global_attributes_cache.getncattr(x, ds) for x in attrs])
                    try:
                        var_name = self.global_attributes_cache.getncattr('variable_name', ds)
                    except AttributeError:
                        # Following changes introduced #1052,
                        # the `variable_name` attribute is expected
                        # to be present in all output files.
                        # To make the code backward compatible
                        # with datasets generated pre-1052,
                        # we try to replace it with `variable_id`
                        # when it's not present.
                        # Note that this mean some variables will not pass QC.
                        var_name = self.global_attributes_cache.getncattr('variable_id', ds)
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
