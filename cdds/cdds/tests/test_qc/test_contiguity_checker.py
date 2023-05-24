# (C) British Crown Copyright 2019-2023, Met Office.
# Please see LICENSE.rst for license details.

import unittest
from cdds.common.request import Request
from cdds.qc.common import DatetimeCalculator
from cdds.qc.contiguity_checker import CollectionsCheck


class CollectionsCheckTestCase(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.request = Request({
            'run_bounds': '1850-01-01-00-00-00 1851-01-01-00-00-00',
            'child_base_date': '1850-01-01-00-00-00',
            'calendar': '360_day'
        }, [])

    def test_adding_messages(self):
        cc = CollectionsCheck(self.request)
        self.assertDictEqual({}, cc.results)
        cc.add_message("foo", "foo_bar", "Baz")
        self.assertDictEqual(
            {"foo": [{"index": "foo_bar", "message": "Baz"}]},
            cc.results
        )

    def test_internal_contiguity_valid_time_dimension(self):
        cc = CollectionsCheck(self.request)
        var_key = 'foo'
        time_axis = {
            'bar.nc': [x * 30 for x in range(12)]
        }
        time_bounds = None
        frequency = '1M'  # note that in this and many other tests without run bounds this corresponds to MonPt
        run_start, run_end = self.request.run_bounds.split(" ")
        cc.check_contiguity(var_key, time_axis, time_bounds, frequency, run_start, run_end)
        self.assertDictEqual(cc.results, {})

    def test_internal_contiguity_valid_time_subsecond_difference(self):
        cc = CollectionsCheck(self.request)
        var_key = 'foo'
        time_axis = {
            'bar.nc': [x * 30 for x in range(11)] + [330.000001]
        }
        time_bounds = None
        frequency = '1M'
        run_start, run_end = self.request.run_bounds.split(" ")
        cc.check_contiguity(var_key, time_axis, time_bounds, frequency, run_start, run_end)
        self.assertDictEqual(cc.results, {})

    def test_internal_contiguity_reversed_time_dimension(self):
        cc = CollectionsCheck(self.request)
        var_key = 'foo'
        time_axis = {
            'bar1.nc': [0, 30, 60, 90],
            'bar2.nc': [210, 180, 150, 120],  # reversed only in one file
            'bar3.nc': [240, 270, 300, 330]
        }
        time_bounds = None
        frequency = '1M'
        run_start, run_end = self.request.run_bounds.split(" ")
        cc.check_contiguity(var_key, time_axis, time_bounds, frequency, run_start, run_end)
        self.assertDictEqual(cc.results, {
            'bar2.nc': [{'index': 'foo', 'message': 'Time coordinate appears to be reversed'}]})

    def test_internal_contiguity_discontinuous_time_dimension(self):
        cc = CollectionsCheck(self.request)
        var_key = 'foo'
        time_axis = {
            'bar1.nc': [0, 30, 60, 90, 120, 330],
        }
        time_bounds = None
        frequency = '1M'
        run_start, run_end = self.request.run_bounds.split(" ")
        cc.check_contiguity(var_key, time_axis, time_bounds, frequency, run_start, run_end)
        self.assertDictEqual(cc.results, {'bar1.nc': [{'index': 'foo',
                                                       'message': ('Time axis value 330 does not correspond to '
                                                                   'reference value 1850-06-01T00:00:00Z '
                                                                   '(difference -180.0 days)')}]})

    def test_internal_contiguity_diurnal_climatology(self):
        cc = CollectionsCheck(self.request)
        time_dim = [(i + 0.5) / 24.0 + 15.0 for i in range(24)] + [(i + 0.5) / 24.0 + 45.0 for i in range(24)]
        time_bnds = [((i / 24.0), ((i + 1) / 24.0 + 29.0)) for i in range(24)] + \
                    [((i / 24.0 + 30.0), ((i + 1) / 24.0 + 59.0)) for i in range(24)]
        msg = cc.check_diurnal_climatology(time_dim, time_bnds)
        self.assertIsNone(msg)

    def test_internal_contiguity_diurnal_climatology_gregorian(self):
        request = Request({
            'run_bounds': '2007-01-01-00-00-00 2007-03-01-00-00-00',
            'child_base_date': '2000-01-01-00-00-00',
            'calendar': 'Gregorian'
        }, [])
        cc = CollectionsCheck(request)
        time_dim = [(i + 0.5) / 24.0 + 2571.0 for i in range(24)] + [(i + 0.5) / 24.0 + 2601.0 for i in range(24)] + \
                   [(i + 0.5) / 24.0 + 2630.0 for i in range(24)]
        time_bnds = [((i / 24.0 + 2557.0), ((i + 1) / 24.0 + 2587.0)) for i in range(24)] + \
                    [((i / 24.0 + 2588.0), ((i + 1) / 24.0 + 2615.0)) for i in range(24)] + \
                    [((i / 24.0 + 2616.0), ((i + 1) / 24.0 + 2646.0)) for i in range(24)]
        msg = cc.check_diurnal_climatology(time_dim, time_bnds)
        self.assertIsNone(msg)

    def test_internal_contiguity_diurnal_climatology_discontinuous_time_dimension(self):
        cc = CollectionsCheck(self.request)
        time_dim = [(i + 0.5) / 24.0 + 15.0 for i in range(24)] + [(i + 0.5) / 24.0 + 46.0 for i in range(24)]
        time_bnds = [((i / 24.0), ((i + 1) / 24.0 + 29.0)) for i in range(24)] + \
                    [((i / 24.0 + 31.0), ((i + 1) / 24.0 + 60.0)) for i in range(24)]
        msgs = cc.check_diurnal_climatology(time_dim, time_bnds)
        self.assertEqual(msgs, 'Time coordinate is not continuous')

    def test_internal_contiguity_diurnal_climatology_incorrect_bounds(self):
        cc = CollectionsCheck(self.request)
        time_dim = [(i + 0.5) / 24.0 + 15.0 for i in range(24)] + [(i + 0.5) / 24.0 + 45.0 for i in range(24)]
        time_bnds = [((i / 24.0), ((i + 1) / 24.0 + 1.0)) for i in range(24)] + \
                    [((i / 24.0 + 1.0), ((i + 1) / 24.0 + 2.0)) for i in range(24)]
        msgs = cc.check_diurnal_climatology(time_dim, time_bnds)
        self.assertEqual(msgs, 'Time points are not in the middle of time bounds')

    def test_diurnal_climatology(self):
        cc = CollectionsCheck(self.request)
        var_key = 'foo'
        time_axis = {
            'bar.nc': [(i + 0.5) / 24.0 + 15.0 for i in range(24)] + [(i + 0.5) / 24.0 + 45.0 for i in range(24)]
        }
        time_bounds = {
            'bar.nc': [((i / 24.0), ((i + 1) / 24.0 + 1.0)) for i in range(24)] + [
                ((i / 24.0 + 1.0), ((i + 1) / 24.0 + 2.0)) for i in range(24)]
        }
        frequency = 'diurnal'
        run_start, run_end = self.request.run_bounds.split(" ")
        cc.check_contiguity(var_key, time_axis, time_bounds, frequency, run_start, run_end)
        self.assertDictEqual(cc.results, {'bar.nc': [
            {'index': 'foo', 'message': 'Time points are not in the middle of time bounds'}]})

    def test_valid_external_contiguity(self):
        cc = CollectionsCheck(self.request)
        var_key = 'foo'
        time_axis = {
            'bar1.nc': [15, 45, 75, 105],
            'bar2.nc': [135, 165, 195, 225],
            'bar3.nc': [255, 285, 315, 345]
        }
        time_bounds = {
            'bar1.nc': [(0, 30), (30, 60), (60, 90), (90, 120)],
            'bar2.nc': [(120, 150), (150, 180), (180, 210), (210, 240)],
            'bar3.nc': [(240, 270), (270, 300), (300, 330), (330, 360)]
        }
        frequency = '1M'
        run_start, run_end = self.request.run_bounds.split(" ")
        cc.check_contiguity(var_key, time_axis, time_bounds, frequency, run_start, run_end)
        self.assertDictEqual(cc.results, {})

    def test_valid_external_contiguity_hourly(self):
        small_number = 1e-8
        request = Request({
            'run_bounds': '1850-01-01-00-00-00 1850-01-03-00-00-00',
            'child_base_date': '1850-01-01-00-00-00',
            'calendar': '360_day'
        }, [])
        cc = CollectionsCheck(request)
        var_key = 'foo'
        time_axis = {
            'bar1.nc': [(i + 0.5) / 24.0 + small_number for i in range(24)],
            'bar2.nc': [(i + 0.5) / 24.0 + small_number for i in range(24, 48)],
        }
        time_bounds = {
            'bar1.nc': [(i / 24.0, (i + 1) / 24.0) for i in range(24)],
            'bar2.nc': [(i / 24.0, (i + 1) / 24.0) for i in range(24, 48)],
        }
        frequency = 'T1H'
        run_start, run_end = request.run_bounds.split(" ")
        cc.check_contiguity(var_key, time_axis, time_bounds, frequency, run_start, run_end)
        self.assertDictEqual(cc.results, {})

    def test_valid_external_contiguity_diurnal(self):
        cc = CollectionsCheck(self.request)
        var_key = 'foo'
        time_axis = {
            'bar1.nc': [(i + 0.5) / 24.0 + 15.0 for i in range(24)],  # 24h diurnal climatology for January
            'bar2.nc': [(i + 0.5) / 24.0 + 45.0 for i in range(24)]   # 24h diurnal climatology for February
        }
        time_bounds = {
            'bar1.nc': [((i / 24.0), ((i + 1) / 24.0 + 29.0)) for i in range(24)],
            'bar2.nc': [((i / 24.0 + 30.0), ((i + 1) / 24.0 + 59.0)) for i in range(24)]
        }
        frequency = 'diurnal'
        run_start, run_end = self.request.run_bounds.split(" ")
        cc.check_contiguity(var_key, time_axis, time_bounds, frequency, run_start, run_end)
        self.assertDictEqual(cc.results, {})

    def test_external_contiguity_with_gap(self):
        cc = CollectionsCheck(self.request)
        var_key = 'foo'
        time_axis = {
            'bar1.nc': [15, 45, 75, 105],
            'bar2.nc': [135, 165, 195, 225],
            'bar3.nc': [255, 285, 345]
        }
        time_bounds = {
            'bar1.nc': [(0, 30), (30, 60), (60, 90), (90, 120)],
            'bar2.nc': [(120, 150), (150, 180), (180, 210), (210, 240)],
            'bar3.nc': [(240, 270), (270, 300), (330, 360)]
        }
        frequency = '1M'
        run_start, run_end = self.request.run_bounds.split(" ")
        cc.check_contiguity(var_key, time_axis, time_bounds, frequency, run_start, run_end)
        expected = {
            'bar3.nc': [
                {
                    'index': 'foo',
                    'message': (
                        'Time axis value 345 does not correspond to reference value 1850-11-16T00:00:00Z '
                        '(difference -30.0 days)')
                },
                {
                    'index': 'foo',
                    'message': ('Time bounds value 330 does not correspond to reference value 1850-11-01T00:00:00Z '
                                '(difference -30.0 days)')
                },
                {
                    'index': 'foo',
                    'message': ('Time bounds value 360 does not correspond to reference value 1850-12-01T00:00:00Z '
                                '(difference -30.0 days)')
                }
            ]
        }
        self.assertDictEqual(cc.results, expected)

    def test_diurnal_climatology_with_gap(self):
        cc = CollectionsCheck(self.request)
        var_key = 'foo'
        time_axis = {
            'bar1.nc': [(i + 0.5) / 24.0 + 15.0 for i in range(24)],
            'bar2.nc': [(i + 0.5) / 24.0 + 75.0 for i in range(24)]
        }
        time_bounds = {
            'bar1.nc': [((i / 24.0), ((i + 1) / 24.0 + 29.0)) for i in range(24)],
            'bar2.nc': [((i / 24.0 + 60.0), ((i + 1) / 24.0 + 89.0)) for i in range(24)]
        }
        frequency = 'diurnal'
        run_start, run_end = self.request.run_bounds.split(" ")
        cc.check_contiguity(var_key, time_axis, time_bounds, frequency, run_start, run_end)
        self.assertDictEqual(cc.results, {'bar2.nc': [{
            'index': 'foo', 'message': 'Climatology time bounds in bar2.nc appear to be mismatched'}]})

    def test_time_bounds_in_360day_calendar(self):
        request = Request({
            'run_bounds': '1850-01-01-00-00-00 1850-07-01-00-00-00',
            'child_base_date': '1850-01-01-00-00-00',
            'calendar': '360_day'
        }, [])
        cc = CollectionsCheck(request)
        var_key = 'foo'
        time_axis = {
            'bar1.nc': [15, 45, 75],
            'bar2.nc': [105, 135, 165],
        }
        time_bounds = {
            'bar1.nc': [(0, 30), (30, 60), (60, 90)],
            'bar2.nc': [(90, 120), (120, 150), (150, 180)],
        }
        frequency = '1M'
        run_start, run_end = request.run_bounds.split(" ")
        cc.check_contiguity(var_key, time_axis, time_bounds, frequency, run_start, run_end)
        self.assertDictEqual(cc.results, {})

    def test_time_bounds_in_gregorian_calendar(self):
        request = Request({
            'run_bounds': '1850-01-01-00-00-00 1850-07-01-00-00-00',
            'child_base_date': '1850-01-01-00-00-00',
            'calendar': 'Gregorian'
        }, [])
        cc = CollectionsCheck(request)
        var_key = 'foo'
        time_axis = {
            'bar1.nc': [15.5, 45, 74.5],
            'bar2.nc': [105, 135.5, 166],
        }
        time_bounds = {
            'bar1.nc': [(0, 31), (31, 59), (59, 90)],
            'bar2.nc': [(90, 120), (120, 151), (151, 181)],
        }
        frequency = '1M'
        run_start, run_end = request.run_bounds.split(" ")
        cc.check_contiguity(var_key, time_axis, time_bounds, frequency, run_start, run_end)
        self.assertDictEqual(cc.results, {})

    def test_imprecise_run_bounds(self):
        request = Request({
            'run_bounds': '1850-01-01-00-00-00 1850-01-02-00-00-00',
            'child_base_date': '1850-01-01-00-00-00',
            'calendar': '360_day'
        }, [])
        cc = CollectionsCheck(request)
        var_key = 'foo'
        time_axis = {
            'bar1.nc': [0.5 / 72.0] + [float(i) / (72.0) for i in range(1, 1 * 24 * 3)],
        }
        time_bounds = None
        frequency = 'T1200S'
        run_start, run_end = request.run_bounds.split(" ")
        cc.check_contiguity(var_key, time_axis, time_bounds, frequency, run_start, run_end)
        self.assertEquals(len(cc.results.keys()), 1)

    def test_invalid_time_bounds(self):
        request = Request({
            'run_bounds': '1850-01-01-00-00-00 1851-01-01-00-00-00',
            'child_base_date': '1850-01-01-00-00-00',
            'calendar': '360_day'
        }, [])
        cc = CollectionsCheck(request)
        var_key = 'foo'
        time_axis = {
            'bar1.nc': [15, 45, 75],
            'bar2.nc': [105, 135, 165],
        }
        time_bounds = {
            'bar1.nc': [(0, 30), (30, 60), (60, 90)],
            'bar2.nc': [(90, 120), (120, 150), (150, 181)],
        }
        frequency = '1M'
        run_start, run_end = request.run_bounds.split(" ")
        cc.check_contiguity(var_key, time_axis, time_bounds, frequency, run_start, run_end)
        self.assertDictEqual(cc.results, {'bar2.nc': [
            {
                'index': 'foo',
                'message': ('Run bounds mismatch: end of the simulation bounds 181 does not correspond to reference '
                            'value 1851-01-01T00:00:00Z (difference 179.0 days)')
            },
            {
                'index': 'foo',
                'message': ('Run bounds mismatch: end of the simulation 165 does not correspond to reference '
                            'value 1850-12-16T00:00:00Z (difference 180.0 days)')
            },
        ]})


if __name__ == '__main__':
    unittest.main()
