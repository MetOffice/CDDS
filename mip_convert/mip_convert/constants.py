# (C) British Crown Copyright 2021-2025, Met Office.
# Please see LICENSE.md for license details.
import logging

LOG_NAME = 'mip_convert'
LOG_LEVEL = logging.INFO

TIMESTEP = 'ATMOS_TIMESTEP'
PREDEFINED_BOUNDS = {
    'category maximum thickness': [[0, 0.6], [0.6, 1.4], [1.4, 2.4], [2.4, 3.6], [3.6, 1e+08]]
}
OVERRIDE_AXIS_DIRECTION = {
    'effectRadIc': 'Z',
    'effectRadLi': 'Z',
}
JPDFTAUREICEMODIS_POINTS = [5., 15., 25., 35., 50., 75.]
JPDFTAUREICEMODIS_BOUNDS = [[0., 10.], [10., 20.], [20., 30.], [30., 40.], [40., 60.], [60., 90.]]
JPDFTAURELIQMODIS_POINTS = [4., 9., 11.5, 14., 17.5, 25.]
JPDFTAURELIQMODIS_BOUNDS = [[0., 8.], [8., 10.], [10., 13.], [13., 15.], [15., 20.], [20., 30.]]
