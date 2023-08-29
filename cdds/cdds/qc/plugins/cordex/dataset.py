# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.

import re
from cdds.qc.plugins.base.dataset import StructuredDataset
from cdds.qc.plugins.cmip6.validators import parse_date_range, ValidationError


class CordexDataset(StructuredDataset):
    """
    A representation of a directory containing a netcdf dataset
    Can be sliced by a MIP table and time period.
    """

    def __init__(self, root, request, mip_tables, mip_table=None, start=None, end=None, logger=None, stream=None):
        super(CordexDataset, self).__init__(root, request, mip_tables, mip_table, start, end, logger, stream)

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

    @classmethod
    def is_responsible(cls, project):
        return 'cordex' == project.lower()

    def check_filename(self, ds, filename):
        """
        Tests filename's facets against a CV, e.g.

        <variable_id>               pr
        <domain>                    ALP-3
        <driving_model_id>          ECMWF-ERAINT
        <experiment_id>             evaluation
        <driving_ensemble_member>   r1i1p1
        <model_id>                  CLMcom-KIT-CCLM5-0-14
        <rcm_version_id>            fpsconv-x2yn2-v1
        <frequency>                 1hr
        [<time_range>]              200001010030-200012312330
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
            "experiment_id": 3,
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

        # member_id should only contain variant_label
        if (hasattr(ds, "sub_experiment_id") and
                ds.getncattr("sub_experiment_id") != "none"):
            messages.append(
                "sub_experiment_id present in file's global attributes "
                "but missing in the filename")
            valid_filename = False

        label_candidate = member_id[0]
        if re.match(r"^r\d+i\d+p\d+$", label_candidate) is None:
            valid_filename = False
            messages.append("Invalid driving ensemble member {}".format(label_candidate))
        else:
            esemble_member = ds.getncattr("driving_ensemble_member")
            if esemble_member != label_candidate:
                valid_filename = False
                messages.append(
                    "Driving ensemble member {} is not consistent with file "
                    "contents ({})".format(label_candidate, esemble_member))

        if len(filename_parts) == 9:
            try:
                _, _ = parse_date_range(filename_parts[8],
                                        ds.getncattr("frequency"),
                                        self._request.calendar)
            except AttributeError:
                messages.append(
                    "Unable to validate filename (frequency not "
                    "present in global attributes)")
            except ValidationError as e:
                valid_filename = False
                messages.append(str(e))
        return valid_filename, messages

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
                    'experiment_id',
                    'sub_experiment_id',
                    'table_id',
                    'variable_id',
                    'domain',
                    'driving_model_id',
                    'driving_ensemble_member',
                    'model_id',
                    'rcm_version_id',
                    'frequency'
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
