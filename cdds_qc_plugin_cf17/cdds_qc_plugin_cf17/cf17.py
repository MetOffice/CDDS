# (C) British Crown Copyright 2017-2022, Met Office.
# Please see LICENSE.rst for license details.

import numpy as np
import re
import os
from compliance_checker.base import Result, BaseCheck, TestCtx
from compliance_checker.cf.cf import CF1_7Check
from compliance_checker.cf.util import StandardNameTable
from netCDF4 import Dataset


class CF17Check(CF1_7Check):
    """
    The CF1.7 checker class
    """
    _cc_spec_version = "1.7"
    _cc_spec = "cf17"
    register_checker = True
    name = "cf17"
    supported_ds = [Dataset]

    def __init__(self, **kwargs):
        """
        CFBaseCheck uses a global attribute to determine version of the
        standard names table, and if it does not find it, uses a packaged
        version (v46 at the moment). Here we provide the location explicitly,
        which also allows us to add some not-yet-standardised names to the
        xml file.
        """
        super(CF17Check, self).__init__()
        try:
            standard_names_dir = kwargs["config"]["standard_names_dir"]
        except KeyError:
            raise ValueError(
                "You must provide the location for the standard"
                " names directory in the config parameter"
            )
        try:
            if kwargs["config"]["standard_names_version"] != "latest":
                table_file = "cf-standard-name-table.v{}.xml".format(
                    kwargs["config"]["standard_names_version"])
            else:
                table_file = "cf-standard-name-table.xml"
        except KeyError:
            table_file = "cf-standard-name-table.xml"
        self._std_names = StandardNameTable(
            os.path.join(standard_names_dir, table_file))

    def check_conventions_version(self, ds):
        """
        Check the global attribute conventions to contain CF-1.7
        CF 2.6.1 the NUG defined global attribute Conventions to the string
        value "CF-1.7" or "CMIP 6.2"

        Parameters
        ----------
        ds : netCDF4.Dataset
            An open netCDF dataset

        Returns
        -------
        : compliance_checker.base.Result
            Result of the version validation
        """

        valid_conventions = ["CF-1.7", "CMIP-6.2"]
        if hasattr(ds, "Conventions"):
            conventions = re.split(",|\s+", getattr(ds, "Conventions", ""))
            if any((c.strip() in valid_conventions for c in conventions)):
                valid = True
                reasoning = []
            else:
                valid = False
                reasoning = ["Conventions global attribute does not contain "
                             "'CF-1.7'. The CF Checker only supports "
                             "CF-1.7-ish at this time."]
        else:
            valid = False
            reasoning = ["Conventions field is not present"]
        return Result(
            BaseCheck.MEDIUM, valid,
            "2.6.1 Global Attribute Conventions includes CF-1.7",
            msgs=reasoning
        )

    def check_cell_measures(self, ds):
        """
        7.2 To indicate extra information about the spatial properties of a
        variable's grid cells, a cell_measures attribute may be defined for a
        variable. This is a string attribute comprising a list of
        blank-separated pairs of words of the form "measure: name". "area" and
        "volume" are the only defined measures.
        The "name" is the name of the variable containing the measure values,
        which we refer to as a "measure variable". The dimensions of the
        measure variable should be the same as or a subset of the dimensions
        of the variable to which they are related, but their order is not
        restricted.
        The variable must have a units attribute and may have other attributes
        such as a standard_name.

        Parameters
        ----------
        ds : netCDF4.Dataset
            An open netCDF dataset

        Returns
        -------
        : compliance_checker.base.Result
            Result of the version validation
        """
        ret_val = []
        reasoning = []
        variables = ds.get_variables_by_attributes(cell_measures=lambda c:
                                                   c is not None)
        cell_measures_regex = "(?:area|volume): (\w+)"
        for var in variables:
            # in rare cases cell measures contain both area and volume, and
            # they need to be captured separately
            double_regex = "^{}\s?{}$".format(cell_measures_regex,
                                              cell_measures_regex)
            search_result = re.search(double_regex, var.cell_measures)
            if search_result:
                # we have captured both area and volume
                cell_meas_var_names = search_result.groups()
            else:
                # try again, this time with just one regex
                search_regex = "^{}$".format(cell_measures_regex)
                search_result = re.search(search_regex, var.cell_measures)
                if search_result:
                    cell_meas_var_names = [search_result.groups()[0]]
            if not search_result:
                valid = False
                reasoning.append(
                    "The cell_measures attribute for variable {} "
                    "is formatted incorrectly. It should take the "
                    "form of either 'area: cell_var' and/or "
                    "'volume: cell_var' where cell_var is the "
                    "variable describing the cell measures".format(var.name)
                )
            else:
                valid = True
                for cell_meas_var_name in cell_meas_var_names:
                    if cell_meas_var_name not in ds.variables:
                        valid = False
                        reasoning.append(
                            "Cell measure variable {} referred to by "
                            "{} is not present in dataset variables".format(
                                var.name, cell_meas_var_name)
                        )
                    else:
                        cell_meas_var = ds.variables[cell_meas_var_name]
                        if not hasattr(cell_meas_var, 'units'):
                            valid = False
                            reasoning.append(
                                "Cell measure variable {} is required "
                                "to have units attribute defined.".format(
                                    cell_meas_var_name)
                            )
                        if not set(cell_meas_var.dimensions).issubset(
                                var.dimensions):
                            valid = False
                            reasoning.append(
                                "Cell measure variable {} must have "
                                "dimensions which are a subset of "
                                "those defined in variable {}.".format(
                                    cell_meas_var_name, var.name)
                            )

            result = Result(
                BaseCheck.MEDIUM, valid, (
                    "7.2 Cell measures", var.name, "cell_measures"),
                reasoning)
            ret_val.append(result)

        return ret_val

    def check_geographic_region(self, ds):
        """
        6.1.1 When data is representative of geographic regions which can be identified by names but which have complex
        boundaries that cannot practically be specified using longitude and latitude boundary coordinates, a labeled
        axis should be used to identify the regions.
        Recommend that the names be chosen from the list of standardized region names whenever possible. To indicate
        that the label values are standardized the variable that contains the labels must be given the standard_name
        attribute with the value region.
        :param netCDF4.Dataset ds: An open netCDF dataset
        :rtype: list
        :return: List of results
        """
        ret_val = []
        region_list = [
            'africa',
            'antarctica',
            'arabian_sea',
            'aral_sea',
            'arctic_ocean',
            'asia',
            'atlantic_arctic_ocean',
            'atlantic_ocean',
            'australia',
            'baltic_sea',
            'barents_opening',
            'barents_sea',
            'beaufort_sea',
            'bellingshausen_sea',
            'bering_sea',
            'bering_strait',
            'black_sea',
            'canadian_archipelago',
            'caribbean_sea',
            'caspian_sea',
            'central_america',
            'chukchi_sea',
            'contiguous_united_states',
            'davis_strait',
            'denmark_strait',
            'drake_passage',
            'east_china_sea',
            'english_channel',
            'eurasia',
            'europe',
            'faroe_scotland_channel',
            'florida_bahamas_strait',
            'fram_strait',
            'gibraltar_strait',
            'global',
            'global_land',
            'global_ocean',
            'great_lakes',
            'greenland',
            'gulf_of_alaska',
            'gulf_of_mexico',
            'hudson_bay',
            'iceland_faroe_channel',
            'indian_pacific_ocean',
            'indian_ocean',
            'indonesian_throughflow',
            'indo_pacific_ocean',
            'irish_sea',
            'lake_baykal',
            'lake_chad',
            'lake_malawi',
            'lake_tanganyika',
            'lake_victoria',
            'mediterranean_sea',
            'mozambique_channel',
            'north_america',
            'north_sea',
            'norwegian_sea',
            'pacific_equatorial_undercurrent',
            'pacific_ocean',
            'persian_gulf',
            'red_sea',
            'ross_sea',
            'sea_of_japan',
            'sea_of_okhotsk',
            'south_america',
            'south_china_sea',
            'southern_ocean',
            'taiwan_luzon_straits',
            'weddell_sea',
            'windward_passage',
            'yellow_sea'
        ]

        for var in ds.get_variables_by_attributes(standard_name='region'):
            regions = var[:]
            # if `regions` is a masked array, convert it to a list
            if np.ma.isMA(regions):
                regions = regions.data.tolist()
            # now we want to process a list of strings in a consistent way

            # if the first element of `regions` is not a list
            # (which means that `regions` is a string), put the variable into a list
            if type(regions[0]) is not list:
                regions = [regions]
            # now `regions` contains a list of strings
            for region in regions:
                # convert from a byte list to a string list
                region = [character.decode('utf8') for character in region]
                # validate each region
                valid_region = TestCtx(BaseCheck.MEDIUM,
                                       "§6.1.1 Geographic region specified by {} is valid"
                                       "".format(var.name))
                valid_region.assert_true(''.join(region).lower() in region_list,
                                         "{} is not a valid region"
                                         "".format(''.join(region)))
                ret_val.append(valid_region.to_result())
        return ret_val
