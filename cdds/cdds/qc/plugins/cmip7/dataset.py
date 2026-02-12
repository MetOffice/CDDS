# (C) British Crown Copyright 2023-2025, Met Office.
# Please see LICENSE.md for license details.

from collections import defaultdict
import re

from cdds.common.constants import CMIP7_VARIANT_LABEL_FORMAT
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
        return 'cmip7' == project.lower()

    def check_filename(self, ds, filename):
        """Checks a filename's consitency with it's global attributes and performs some validation.

        Example
        -------
        An example CMIP7 filename.

        tas_tavg-h2m-hxy-u_day_glb_gn_UKESM1-3-LL_1pctCO2_r1i1p1f3_19560101-19561230.nc

        <variable_id>      tas
        <branding_suffix>  tavg-h2m-hxy-u
        <frequency>        day
        <region>           glb
        <grid_label>       gn
        <source_id>        UKESEM1-3-LL
        <experiment_id>    1pctCO2
        <variant_label>    r1i1p1f3
        [<time_range>]     19560101-19561230
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
        facet_dict = {
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

        for facet, part_index in facet_dict.items():
            try:
                # test it against stored global attribute
                attr = self.global_attributes_cache.getncattr(facet, ds)
                if attr != filename_parts[part_index]:
                    valid_filename = False
                    messages.append(
                        f"{facet}'s value '{attr}' doesn't match filename {filename}")

            except AttributeError:
                # raised if something's wrong with global attributes
                # it should be validated again by the global attributes checker
                messages.append(f"Global Attribute '{facet}' missing from the NetCDF file")

        variant_label = filename_parts[facet_dict["variant_label"]]
        if re.match(CMIP7_VARIANT_LABEL_FORMAT, variant_label) is None:
            valid_filename = False
            messages.append(f"Invalid variant_label {variant_label}")

        table = self.global_attributes_cache.getncattr("table_id", ds)
        variable = filename_parts[0] + "_" + filename_parts[1]
        if table in self._mip_tables.tables:
            if variable not in (self._mip_tables.get_variables(table)):
                valid_filename = False
                messages.append(f"Invalid variable {variable} in the filename {filename}")
        else:
            valid_filename = False
            messages.append(f"Invalid table_id Global Attribute {table} in file {filename}")

        if filename_parts[8]:
            try:
                _, _ = parse_date_range(filename_parts[8],
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

    def _aggregate_files(self) -> tuple[dict, dict]:
        """Aggregate files in the dataset directory by a particular set of facets.

        Returns
        -------
        tuple[dict, dict]
            Facet-indexed dictionaries
        """
        aggregated_dataset = defaultdict(list)
        variable_names = {}
        self._logger.info("Aggregating files")
        for filepath in self._dataset:
            with self._loader_class(filepath) as ds:
                facet_attrs = [
                    'mip_era',
                    'source_id',
                    'experiment_id',
                    'variant_label',
                    'table_id',
                    'frequency',
                    'variable_name',
                    'grid_label',
                    'region',
                ]
                try:
                    file_index = '_'.join([self.global_attributes_cache.getncattr(x, ds) for x in facet_attrs])

                    var_name = self.global_attributes_cache.getncattr('variable_name', ds)
                    if file_index not in variable_names:
                        variable_names[file_index] = var_name

                    aggregated_dataset[file_index].append(filepath)

                except AttributeError as e:
                    self._logger.error("Error when parsing dataset {}: {}".format(filepath, str(e)))
        return aggregated_dataset, variable_names
