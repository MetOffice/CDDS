# (C) British Crown Copyright 2018-2025, Met Office.
# Please see LICENSE.md for license details.
"""
Tests of mip_convert_wrapper.config_updater
"""
import unittest

from metomi.isodatetime.data import Calendar
from metomi.isodatetime.parsers import TimePointParser
from cdds.convert.mip_convert_wrapper.config_updater import calculate_mip_convert_run_bounds


class TestCalculateBounds(unittest.TestCase):
    """
    Tests of calculate_mip_convert_run_bounds.
    """
    def tearDown(self):
        Calendar.default().set_mode('360day')

    def test_simple(self):
        Calendar.default().set_mode('360day')
        start_point = '18500101T0000Z'
        cycle_duration = 'P1Y'
        simulation_end = TimePointParser().parse('20010101')
        expected_task_bounds = (TimePointParser().parse('18500101'), TimePointParser().parse('18510101'))

        task_bounds = calculate_mip_convert_run_bounds(start_point, cycle_duration, simulation_end)
        self.assertEqual(task_bounds, expected_task_bounds)

    def test_simulation_end(self):
        Calendar.default().set_mode('360day')
        start_point = '18500101T0000Z'
        cycle_duration = 'P10Y'
        simulation_end = TimePointParser().parse('18550101')
        expected_task_bounds = (TimePointParser().parse('18500101'), TimePointParser().parse('18550101'))

        task_bounds = calculate_mip_convert_run_bounds(start_point, cycle_duration, simulation_end)
        self.assertEqual(task_bounds, expected_task_bounds)

    def test_gregorian(self):
        Calendar.default().set_mode('gregorian')
        start_point = '18500101T0000Z'
        cycle_duration = '-P1D'
        simulation_end = TimePointParser().parse('20010101')
        expected_task_bounds = (TimePointParser().parse('18500101'), TimePointParser().parse('18491231'))

        task_bounds = calculate_mip_convert_run_bounds(start_point, cycle_duration, simulation_end)
        self.assertEqual(task_bounds, expected_task_bounds)


if __name__ == '__main__':
    unittest.main()
