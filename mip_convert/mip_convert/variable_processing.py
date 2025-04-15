# (C) British Crown Copyright 2021, Met Office.
# Please see LICENSE.md for license details.
import iris.cube
import copy
import logging
import metomi.isodatetime.parsers as parse
import regex as re

import cf_units
import cftime
import iris
from iris.time import PartialDateTime
from iris.analysis.cartography import rotate_pole, get_xy_grids, get_xy_contiguous_bounded_grids
from iris.coord_systems import RotatedGeogCS, GeogCS
from iris.util import guess_coord_axis
import numpy as np

from cdds.common import DATE_TIME_REGEX
from mip_convert.common import (
    DEFAULT_FILL_VALUE, Longitudes, validate_latitudes, format_date,
    MIP_to_model_axis_name_mapping, apply_time_constraint, raw_to_value,
    parse_to_loadables)
from mip_convert.variable import make_masked
from dataclasses import dataclass
from typing import Dict
from mip_convert.new_variable import VariableMetadata


class Preparator:

    def __init__(self, input_variables: Dict[str, iris.cube.Cube]):
        self.input_variables = input_variables

    def prepare(self, input_variables: Dict[str, iris.cube.Cube]) -> Dict[str, iris.cube.Cube]:
        self._remove_units_from_input_variables_as_necessary()
        self._remove_forecast_period()
        self._ensure_masked_arrays()
        return self.input_variables

    def _remove_units_from_input_variables_as_necessary(self, input_variables: Dict[str, iris.cube.Cube]):
        # To prevent the Iris error "Cannot use <operator> with
        # differing units" when applying expressions containing
        # multiple 'input variables', remove the units from the
        # 'input variables' prior to applying the expression.
        if len(input_variables) > 1:
            for cube in list(input_variables.values()):
                cube.units = cf_units.Unit('unknown')

    def _remove_forecast_period(self):
        # Avoid issues in inconsistent forecast_period (LBFT) values by blanket removal of the coord.
        logger = logging.getLogger(__name__)
        for cube in self.input_variables.values():
            try:
                cube.remove_coord("forecast_period")
                logger.debug(f'Removed coordinate "forecast_period" from {cube} variable ')
            except iris.exceptions.CoordinateNotFoundError:
                pass

    def _ensure_masked_arrays(self):
        # This method realises the data.
        for cube in list(self.input_variables.values()):
            if 'fill_value' not in cube.attributes:  # Iris v1
                if hasattr(cube.data, 'fill_value'):  # Iris v2
                    cube.attributes['fill_value'] = cube.data.fill_value
                else:
                    cube.attributes['fill_value'] = DEFAULT_FILL_VALUE
            if not np.ma.isMaskedArray(cube.data):
                cube.data = make_masked(cube.data, cube.shape, cube.attributes['fill_value'], cube.data.dtype)
