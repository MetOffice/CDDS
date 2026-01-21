# (C) British Crown Copyright 2019-2025, Met Office.
# Please see LICENSE.md for license details.

import unittest
from metomi.isodatetime.parsers import TimePointParser

from cdds.qc.contiguity_checker import CollectionsCheck
from cdds.tests.factories.request_factory import simple_request


class CollectionsCheckTestCase(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.request = simple_request()
        self.request.metadata.base_date = TimePointParser().parse('1850-01-01T00:00:00')
        self.request.metadata.calendar = '360_day'
        self.request.data.start_date = TimePointParser().parse('1850-01-01T00:00:00')
        self.request.data.end_date = TimePointParser().parse('1851-01-01T00:00:00')

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
            'bar.nc': [x * 30 for x in range(13)]  # time points at midnight of the 1st of each month
        }
        time_bounds = None
        frequency = 'P1M'  # note that in this and many other tests without run bounds this corresponds to MonPt
        run_start = self.request.data.start_date
        run_end = self.request.data.end_date
        cc.check_contiguity(var_key, time_axis, time_bounds, frequency, run_start, run_end)
        self.assertDictEqual(cc.results, {})

    def test_internal_contiguity_valid_time_dimension_and_bounds(self):
        cc = CollectionsCheck(self.request)
        var_key = 'foo'
        time_axis = {
            'bar.nc': [x * 30 + 15.0 for x in range(12)]  # conventional mid-points with defined bounds
        }
        time_bounds = {
            'bar.nc': [(x * 30, x * 30 + 30) for x in range(12)]
        }
        frequency = 'P1M'
        run_start = self.request.data.start_date
        run_end = self.request.data.end_date
        cc.check_contiguity(var_key, time_axis, time_bounds, frequency, run_start, run_end)
        self.assertDictEqual(cc.results, {})

    def test_internal_contiguity_instantaneous(self):
        self.request.data.start_date = TimePointParser().parse('1850-01-01T00:00:00')
        self.request.data.end_date = TimePointParser().parse('1850-03-01T00:00:00')

        cc = CollectionsCheck(self.request)
        var_key = 'foo'
        time_axis = {
            'bar1.nc': [(i + 0.0) / 24.0 for i in range(1, 24 * 30 + 1)],
            'bar2.nc': [(i + 0.0) / 24.0 for i in range(24 * 30 + 1, 48 * 30 + 1)],
        }
        frequency = 'PT1H'
        run_start = self.request.data.start_date
        run_end = self.request.data.end_date
        cc.check_contiguity(var_key, time_axis, None, frequency, run_start, run_end)
        self.assertDictEqual(cc.results, {})

    def test_internal_contiguity_instantaneous_no_adjustment(self):
        self.request.data.start_date = TimePointParser().parse('1850-01-01T00:00:00')
        self.request.data.end_date = TimePointParser().parse('1850-03-01T00:00:00')

        cc = CollectionsCheck(self.request)
        var_key = 'foo'
        time_axis = {
            'bar1.nc': [(i + 0.0) / 24.0 for i in range(1, 24 * 30)],
            'bar2.nc': [(i + 0.0) / 24.0 for i in range(24 * 30, 48 * 30 + 1)],
        }
        frequency = 'PT1H'
        run_start = self.request.data.start_date
        run_end = self.request.data.end_date
        cc.check_contiguity(var_key, time_axis, None, frequency, run_start, run_end)
        self.assertDictEqual(cc.results, {})

    def test_internal_contiguity_valid_time_subsecond_difference(self):
        cc = CollectionsCheck(self.request)
        var_key = 'foo'
        time_axis = {
            'bar.nc': [x * 30 for x in range(12)] + [360.000001]
        }
        time_bounds = None
        frequency = 'P1M'
        run_start = self.request.data.start_date
        run_end = self.request.data.end_date
        cc.check_contiguity(var_key, time_axis, time_bounds, frequency, run_start, run_end)
        self.assertDictEqual(cc.results, {})

    def test_internal_contiguity_reversed_time_dimension(self):
        cc = CollectionsCheck(self.request)
        var_key = 'foo'
        time_axis = {
            'bar1.nc': [0, 30, 60, 90],
            'bar2.nc': [210, 180, 150, 120],  # reversed only in one file
            'bar3.nc': [240, 270, 300, 330, 360]
        }
        time_bounds = None
        frequency = 'P1M'
        run_start = self.request.data.start_date
        run_end = self.request.data.end_date
        cc.check_contiguity(var_key, time_axis, time_bounds, frequency, run_start, run_end)
        self.assertDictEqual(cc.results, {
            'bar2.nc': [{'index': 'foo', 'message': 'Time coordinate appears to be reversed'}]})

    def test_internal_contiguity_discontinuous_time_dimension(self):
        cc = CollectionsCheck(self.request)
        var_key = 'foo'
        time_axis = {
            'bar1.nc': [0, 30, 60, 90, 120, 140, 150, 160, 170, 180, 190, 330, 360],
        }
        time_bounds = None
        frequency = 'P1M'
        run_start = self.request.data.start_date
        run_end = self.request.data.end_date
        cc.check_contiguity(var_key, time_axis, time_bounds, frequency, run_start, run_end)
        self.assertDictEqual(cc.results, {'bar1.nc': [{'index': 'foo',
                                                       'message': ('Time axis value 140 does not correspond to '
                                                                   'reference value 1850-06-01T00:00:00Z '
                                                                   '(difference 10.0 days)')},
                                                      {'index': 'foo',
                                                       'message': ('Time axis value 150 does not correspond to '
                                                                   'reference value 1850-07-01T00:00:00Z '
                                                                   '(difference 30.0 days)')},
                                                      {'index': 'foo',
                                                       'message': ('Time axis value 160 does not correspond to '
                                                                   'reference value 1850-08-01T00:00:00Z '
                                                                   '(difference 50.0 days)')},
                                                      {'index': 'foo',
                                                       'message': ('Time axis value 170 does not correspond to '
                                                                   'reference value 1850-09-01T00:00:00Z '
                                                                   '(difference 70.0 days)')},
                                                      {'index': 'foo',
                                                       'message': ('Time axis value 180 does not correspond to '
                                                                   'reference value 1850-10-01T00:00:00Z '
                                                                   '(difference 90.0 days)')},
                                                      {'index': 'foo',
                                                       'message': ('Time axis value 190 does not correspond to '
                                                                   'reference value 1850-11-01T00:00:00Z '
                                                                   '(difference 110.0 days)')},
                                                      ]})

    def test_internal_contiguity_diurnal_climatology(self):
        cc = CollectionsCheck(self.request)
        time_dim = [(i + 0.5) / 24.0 + 15.0 for i in range(24)] + [(i + 0.5) / 24.0 + 45.0 for i in range(24)]
        time_bnds = [((i / 24.0), ((i + 1) / 24.0 + 29.0)) for i in range(24)] + \
                    [((i / 24.0 + 30.0), ((i + 1) / 24.0 + 59.0)) for i in range(24)]
        msg = cc.check_diurnal_climatology(time_dim, time_bnds)
        self.assertIsNone(msg)

    def test_internal_contiguity_diurnal_climatology_gregorian(self):
        request = simple_request()
        request.metadata.base_date = TimePointParser().parse('2000-01-01T00:00:00')
        request.metadata.calendar = 'Gregorian'
        request.data.start_date = TimePointParser().parse('2007-01-01T00:00:00')
        request.data.end_date = TimePointParser().parse('2007-03-01T00:00:00')
        cc = CollectionsCheck(request)
        time_dim = [(i + 0.5) / 24.0 + 2571.0 for i in range(24)] + [(i + 0.5) / 24.0 + 2601.0 for i in range(24)] + \
                   [(i + 0.5) / 24.0 + 2630.0 for i in range(24)]
        time_bnds = [((i / 24.0 + 2557.0), ((i + 1) / 24.0 + 2587.0)) for i in range(24)] + \
                    [((i / 24.0 + 2588.0), ((i + 1) / 24.0 + 2615.0)) for i in range(24)] + \
                    [((i / 24.0 + 2616.0), ((i + 1) / 24.0 + 2646.0)) for i in range(24)]
        msg = cc.check_diurnal_climatology(time_dim, time_bnds)
        self.assertIsNone(msg)

#    def test_internal_contiguity_diurnal_climatology_obs4mips(self):
#        request = Request({
#            'run_bounds': '2007-01-01T00:00:00 2009-01-01T00:00:00',
#            'base_date': '2000-01-01T00:00:00',
#            'calendar': 'Gregorian'
#        }, [])
#        cc = CollectionsCheck(request)
#        from netCDF4 import Dataset
#        ds1 = Dataset('/data/users/pflorek/diurnal/rlut_1hrCM_GERB-HR-ED01-1-0_BE_gn_200701-200712.nc')
#        ds2 = Dataset('/data/users/pflorek/diurnal/rlut_1hrCM_GERB-HR-ED01-1-0_BE_gn_200801-200812.nc')
#        time_dim = [val for val in ds1.variables["time"][:].data] + [val for val in ds2.variables["time"][:].data]
#        time_bnds = [val for val in ds1.variables["climatology_bnds"][:].data] + [
#            val for val in ds2.variables["climatology_bnds"][:].data]
#        msg = cc.check_diurnal_climatology(time_dim, time_bnds)
#        self.assertIsNone(msg)

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
        frequency = '1hrCM'
        run_start = self.request.data.start_date
        run_end = self.request.data.end_date
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
        frequency = 'P1M'
        run_start = self.request.data.start_date
        run_end = self.request.data.end_date
        cc.check_contiguity(var_key, time_axis, time_bounds, frequency, run_start, run_end)
        self.assertDictEqual(cc.results, {})

    def test_valid_external_contiguity_hourly(self):
        small_number = 1e-8
        request = simple_request()
        request.data.start_date = TimePointParser().parse('1850-01-01T00:00:00')
        request.data.end_date = TimePointParser().parse('1850-01-03T00:00:00')
        request.metadata.base_date = TimePointParser().parse('1850-01-01T00:00:00')
        request.metadata.calendar = '360_day'
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
        frequency = 'PT1H'
        run_start = request.data.start_date
        run_end = request.data.end_date
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
        frequency = '1hrCM'
        run_start = self.request.data.start_date
        run_end = self.request.data.end_date
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
        frequency = 'P1M'
        run_start = self.request.data.start_date
        run_end = self.request.data.end_date
        cc.check_contiguity(var_key, time_axis, time_bounds, frequency, run_start, run_end)
        expected = {'bar1.nc': [{'index': 'foo',
                                 'message': 'Total length of time coordinate, 11, is '
                                            'different from 12 implied by time bounds '
                                            '(from 1850-01-01T00:00:00Z to '
                                            '1851-01-01T00:00:00Z) and time frequency '
                                            '(P1M)'}],
                    'bar2.nc': [{'index': 'foo',
                                 'message': 'Total length of time coordinate, 11, is '
                                            'different from 12 implied by time bounds '
                                            '(from 1850-01-01T00:00:00Z to '
                                            '1851-01-01T00:00:00Z) and time frequency '
                                            '(P1M)'}],
                    'bar3.nc': [{'index': 'foo',
                                 'message': 'Total length of time coordinate, 11, is '
                                            'different from 12 implied by time bounds '
                                            '(from 1850-01-01T00:00:00Z to '
                                            '1851-01-01T00:00:00Z) and time frequency '
                                            '(P1M)'}]}
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
        frequency = '1hrCM'
        run_start = self.request.data.start_date
        run_end = self.request.data.end_date
        cc.check_contiguity(var_key, time_axis, time_bounds, frequency, run_start, run_end)
        self.assertDictEqual(cc.results, {'bar2.nc': [{
            'index': 'foo', 'message': 'Climatology time bounds in bar2.nc appear to be mismatched'}]})

    def test_time_bounds_in_360day_calendar(self):
        request = simple_request()
        request.data.start_date = TimePointParser().parse('1850-01-01T00:00:00')
        request.data.end_date = TimePointParser().parse('1850-07-01T00:00:00')
        request.metadata.base_date = TimePointParser().parse('1850-01-01T00:00:00')
        request.metadata.calendar = '360_day'
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
        frequency = 'P1M'
        run_start = request.data.start_date
        run_end = request.data.end_date
        cc.check_contiguity(var_key, time_axis, time_bounds, frequency, run_start, run_end)
        self.assertDictEqual(cc.results, {})

    def test_time_bounds_in_gregorian_calendar(self):
        request = simple_request()
        request.data.start_date = TimePointParser().parse('1850-01-01T00:00:00')
        request.data.end_date = TimePointParser().parse('1850-07-01T00:00:00')
        request.metadata.base_date = TimePointParser().parse('1850-01-01T00:00:00')
        request.metadata.calendar = 'Gregorian'
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
        frequency = 'P1M'
        run_start = request.data.start_date
        run_end = request.data.end_date
        cc.check_contiguity(var_key, time_axis, time_bounds, frequency, run_start, run_end)
        self.assertDictEqual(cc.results, {})

    def test_imprecise_run_bounds(self):
        request = simple_request()
        request.data.start_date = TimePointParser().parse('1850-01-01T00:00:00')
        request.data.end_date = TimePointParser().parse('1850-01-02T00:00:00')
        request.metadata.base_date = TimePointParser().parse('1850-01-01T00:00:00')
        request.metadata.calendar = '360_day'
        cc = CollectionsCheck(request)
        var_key = 'foo'
        time_axis = {
            'bar1.nc': [0.5 / 72.0] + [float(i) / (72.0) for i in range(1, 1 * 24 * 3)],
        }
        time_bounds = None
        frequency = 'PT1200S'
        run_start = self.request.data.start_date
        run_end = self.request.data.end_date
        cc.check_contiguity(var_key, time_axis, time_bounds, frequency, run_start, run_end)
        self.assertEqual(len(cc.results.keys()), 1)

    def test_invalid_time_bounds(self):
        request = simple_request()
        request.data.start_date = TimePointParser().parse('1850-01-01T00:00:00')
        request.data.end_date = TimePointParser().parse('1851-01-01T00:00:00')
        request.metadata.base_date = TimePointParser().parse('1850-01-01T00:00:00')
        request.metadata.calendar = '360_day'
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
        frequency = 'P1M'
        run_start = self.request.data.start_date
        run_end = self.request.data.end_date
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
