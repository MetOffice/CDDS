# (C) British Crown Copyright 2018-2021, Met Office.
# Please see LICENSE.rst for license details.
"""
Tests of mip_convert_wrapper.config_updater
"""
from datetime import datetime
import unittest

from cdds.convert.mip_convert_wrapper.config_updater import (
    calculate_mip_convert_run_bounds, rose_date)


class TestCalculateBounds(unittest.TestCase):
    """
    Tests of calculate_mip_convert_run_bounds.
    """
    def test_simple(self):
        start_point = '18500101T0000Z'
        cycle_duration = 'P1Y'
        simulation_end = datetime(2001, 1, 1)
        stream_time_overrides = 'None'
        expected_task_bounds = (datetime(1850, 1, 1), datetime(1851, 1, 1))

        task_bounds = calculate_mip_convert_run_bounds(
            start_point, cycle_duration, simulation_end,
            stream_time_overrides)
        self.assertEqual(task_bounds, expected_task_bounds)

    def test_simulation_end(self):
        start_point = '18500101T0000Z'
        cycle_duration = 'P10Y'
        simulation_end = datetime(1855, 1, 1)
        stream_time_overrides = 'None'
        expected_task_bounds = (datetime(1850, 1, 1), datetime(1855, 1, 1))

        task_bounds = calculate_mip_convert_run_bounds(
            start_point, cycle_duration, simulation_end,
            stream_time_overrides)
        self.assertEqual(task_bounds, expected_task_bounds)

    def test_stream_time_overrides(self):
        start_point = '18500101T0000Z'
        cycle_duration = 'P10Y'
        simulation_end = datetime(2001, 1, 1)
        stream_time_overrides = '[1852, 1857]'
        expected_task_bounds = (datetime(1852, 1, 1), datetime(1858, 1, 1))

        task_bounds = calculate_mip_convert_run_bounds(
            start_point, cycle_duration, simulation_end,
            stream_time_overrides)
        self.assertEqual(task_bounds, expected_task_bounds)


class TestRoseDate(unittest.TestCase):
    """
    Tests of rose_date
    """
    def test_simple(self):
        ref_date = '18500101T0000Z'
        offsets = ['P1Y']
        model_calendar = '360day'
        expected = datetime(1851, 1, 1)

        actual = rose_date(ref_date, offsets, model_calendar)
        self.assertEqual(expected, actual)

    def test_multiple_offsets(self):
        ref_date = '18500101T0000Z'
        offsets = ['P1Y', '-P1D']
        model_calendar = '360day'
        expected = datetime(1850, 12, 30)

        actual = rose_date(ref_date, offsets, model_calendar)
        self.assertEqual(expected, actual)

    def test_gregorian(self):
        ref_date = '18500101T0000Z'
        offsets = ['-P1D']
        model_calendar = 'gregorian'
        expected = datetime(1849, 12, 31)

        actual = rose_date(ref_date, offsets, model_calendar)
        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
