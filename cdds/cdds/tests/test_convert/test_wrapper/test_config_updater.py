# (C) British Crown Copyright 2018-2021, Met Office.
# Please see LICENSE.rst for license details.
"""
Tests of mip_convert_wrapper.config_updater
"""
import unittest

from metomi.isodatetime.data import Calendar
from metomi.isodatetime.parsers import TimePointParser
from cdds.convert.mip_convert_wrapper.config_updater import calculate_mip_convert_run_bounds, rose_date


class TestCalculateBounds(unittest.TestCase):
    """
    Tests of calculate_mip_convert_run_bounds.
    """
    def test_simple(self):
        start_point = '18500101T0000Z'
        cycle_duration = 'P1Y'
        simulation_end = TimePointParser().parse('20010101')
        expected_task_bounds = (TimePointParser().parse('18500101'), TimePointParser().parse('18510101'))

        task_bounds = calculate_mip_convert_run_bounds(start_point, cycle_duration, simulation_end)
        self.assertEqual(task_bounds, expected_task_bounds)

    def test_simulation_end(self):
        start_point = '18500101T0000Z'
        cycle_duration = 'P10Y'
        simulation_end = TimePointParser().parse('18550101')
        expected_task_bounds = (TimePointParser().parse('18500101'), TimePointParser().parse('18550101'))

        task_bounds = calculate_mip_convert_run_bounds(start_point, cycle_duration, simulation_end)
        self.assertEqual(task_bounds, expected_task_bounds)


class TestRoseDate(unittest.TestCase):
    """
    Tests of rose_date
    """
    def tearDown(self):
        model_calendar = '360day'
        Calendar.default().set_mode(model_calendar)

    def test_simple(self):
        model_calendar = '360day'
        Calendar.default().set_mode(model_calendar)
        ref_date = '18500101T0000Z'
        offsets = 'P1Y'
        expected = TimePointParser().parse('18510101')

        actual = rose_date(ref_date, offsets)
        self.assertEqual(expected, actual)

    def test_gregorian(self):
        model_calendar = 'gregorian'
        Calendar.default().set_mode(model_calendar)
        ref_date = '18500101T0000Z'
        offsets = '-P1D'
        expected = TimePointParser().parse('18491231')

        actual = rose_date(ref_date, offsets)
        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
