# (C) British Crown Copyright 2019-2022, Met Office.
# Please see LICENSE.rst for license details.

import unittest
from cdds.common.request import Request
from cdds.qc.contiguity_checker import CMIP6CollectionsCheck


class CMIP6CollectionsCheckTestCase(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_adding_messages(self):
        cc = CMIP6CollectionsCheck()
        self.assertDictEqual({}, cc.results)
        cc.add_message("foo", "foo_bar", "Baz")
        self.assertDictEqual(
            {"foo": [{"index": "foo_bar", "message": "Baz"}]},
            cc.results
        )

    def test_internal_contiguity_valid_time_dimension(self):
        cc = CMIP6CollectionsCheck()
        time_dim = [0, 30, 60, 90]
        msg = cc.check_internal_contiguity(time_dim)
        self.assertIsNone(msg)

    def test_internal_contiguity_valid_time_subsecond_difference(self):
        cc = CMIP6CollectionsCheck()
        time_dim = [0, 30, 60, 90.000001]
        msg = cc.check_internal_contiguity(time_dim)
        self.assertIsNone(msg)

    def test_internal_contiguity_reversed_time_dimension(self):
        cc = CMIP6CollectionsCheck()
        time_dim = [90, 60, 30, 0]
        msg = cc.check_internal_contiguity(time_dim)
        self.assertEqual(msg, "Time coordinate appears to be reversed")

    def test_internal_contiguity_discontinuous_time_dimension(self):
        cc = CMIP6CollectionsCheck()
        time_dim = [0, 30, 70, 100]
        msg = cc.check_internal_contiguity(time_dim)
        self.assertEqual(msg, "Time coordinate is not continuous")

    def test_internal_contiguity_diurnal_climatology(self):
        cc = CMIP6CollectionsCheck()
        time_dim = [(i + 0.5) / 24.0 + 15.0 for i in range(24)] + [(i + 0.5) / 24.0 + 45.0 for i in range(24)]
        time_bnds = [((i / 24.0), ((i + 1) / 24.0 + 29.0)) for i in range(24)] + \
                    [((i / 24.0 + 30.0), ((i + 1) / 24.0 + 59.0)) for i in range(24)]
        msg = cc.check_diurnal_climatology(time_dim, time_bnds)
        self.assertIsNone(msg)

    def test_internal_contiguity_diurnal_climatology_discontinuous_time_dimension(self):
        cc = CMIP6CollectionsCheck()
        time_dim = [(i + 0.5) / 24.0 + 15.0 for i in range(24)] + [(i + 0.5) / 24.0 + 46.0 for i in range(24)]
        time_bnds = [((i / 24.0), ((i + 1) / 24.0 + 29.0)) for i in range(24)] + \
                    [((i / 24.0 + 31.0), ((i + 1) / 24.0 + 60.0)) for i in range(24)]
        msgs = cc.check_diurnal_climatology(time_dim, time_bnds)
        self.assertEqual(msgs, 'Time coordinate is not continuous')

    def test_internal_contiguity_diurnal_climatology_incorrect_bounds(self):
        cc = CMIP6CollectionsCheck()
        time_dim = [(i + 0.5) / 24.0 + 15.0 for i in range(24)] + [(i + 0.5) / 24.0 + 45.0 for i in range(24)]
        time_bnds = [((i / 24.0), ((i + 1) / 24.0 + 1.0)) for i in range(24)] + \
                    [((i / 24.0 + 1.0), ((i + 1) / 24.0 + 2.0)) for i in range(24)]
        msgs = cc.check_diurnal_climatology(time_dim, time_bnds)
        self.assertEqual(msgs, 'Time points are not in the middle of time bounds')

    def test_valid_external_contiguity(self):
        metadatas = [
            {
                "filename": "foo_1.nc",
                "time_dim": [15, 45, 75],
                "time_bnds": [(0, 30), (30, 60), (60, 90)],
                "offset": 30,
                "frequency": "mon",
                "units": "days",
                "calendar": "360_day",
                "diurnal_climatology": False,
            },
            {
                "filename": "foo_2.nc",
                "time_dim": [105, 135, 165],
                "time_bnds": [(90, 120), (120, 150), (150, 180)],
                "offset": 30,
                "frequency": "mon",
                "units": "days",
                "calendar": "360_day",
                "diurnal_climatology": False,
            },
        ]
        cc = CMIP6CollectionsCheck()
        self.assertTrue(cc.check_external_contiguity(metadatas, "foo"))

    def test_valid_external_contiguity_hourly(self):
        small_number = 1e-8
        metadatas = [
            {
                "filename": "foo_1.nc",
                "time_dim": [0.5 / 24 + small_number,
                             1.5 / 24 + small_number,
                             2.5 / 24 + small_number],
                "time_bnds": [(0, 1. / 24), (1. / 24, 2. / 24),
                              (2. / 24, 3. / 24)],
                "offset": 1. / 24 + small_number,
                "frequency": "1hr",
                "units": "days",
                "calendar": "360_day",
                "diurnal_climatology": False,
            },
            {
                "filename": "foo_2.nc",
                "time_dim": [3.5 / 24, 4.5 / 24, 5.5 / 24],
                "time_bnds": [(3, 4. / 24), (4. / 24, 5. / 24),
                              (5. / 24, 6. / 24)],
                "offset": 1. / 24,
                "frequency": "1hr",
                "units": "days",
                "calendar": "360_day",
                "diurnal_climatology": False,
            },
        ]
        cc = CMIP6CollectionsCheck()
        self.assertTrue(cc.check_external_contiguity(metadatas, "foo"))

    def test_valid_external_contiguity_diurnal(self):
        metadatas = [
            {
                "filename": "foo_1.nc",
                "time_dim": [(i + 0.5) / 24.0 + 15.0 for i in range(24)],
                "time_bnds": [((i / 24.0), ((i + 1) / 24.0 + 29.0)) for i in range(24)],
                "offset": 1. / 24,
                "frequency": "1hrCM",
                "units": "days",
                "calendar": "360_day",
                "diurnal_climatology": True,
            },
            {
                "filename": "foo_2.nc",
                "time_dim":  [(i + 0.5) / 24.0 + 45.0 for i in range(24)],
                "time_bnds": [((i / 24.0 + 30.0), ((i + 1) / 24.0 + 59.0)) for i in range(24)],
                "offset": 1. / 24,
                "frequency": "1hrCM",
                "units": "days",
                "calendar": "360_day",
                "diurnal_climatology": True,
            },
        ]
        cc = CMIP6CollectionsCheck()
        self.assertTrue(cc.check_external_contiguity(metadatas, "foo"))

    def test_external_contiguity_with_gap(self):
        metadatas = [
            {
                "filename": "foo_1.nc",
                "time_dim": [15, 45, 75],
                "time_bnds": [(0, 30), (30, 60), (60, 90)],
                "offset": 30,
                "frequency": "mon",
                "units": "days",
                "calendar": "360_day",
                "diurnal_climatology": False,
            },
            {
                "filename": "foo_2.nc",
                "time_dim": [135, 165],
                "time_bnds": [(120, 150), (150, 180)],
                "offset": 30,
                "frequency": "mon",
                "units": "days",
                "calendar": "360_day",
                "diurnal_climatology": False,
            },
        ]
        cc = CMIP6CollectionsCheck()
        self.assertFalse(cc.check_external_contiguity(metadatas, "foo"))
        self.assertEqual(
            cc.results["foo_2.nc"],
            [{
                "index": "foo",
                "message": (
                    "There is an inconsistency between foo_1.nc and foo_2.nc "
                    "(a gap of 30 days)"
                )
            }]
        )

    def test_external_contiguity_with_inconsistent_frequency(self):
        metadatas = [
            {
                "filename": "foo_1.nc",
                "time_dim": [15, 45, 75],
                "time_bnds": [(0, 30), (30, 60), (60, 90)],
                "offset": 30,
                "frequency": "day",
                "units": "days",
                "calendar": "360_day",
                "diurnal_climatology": False,
            },
            {
                "filename": "foo_2.nc",
                "time_dim": [105, 135, 165],
                "time_bnds": [(90, 120), (120, 150), (150, 180)],
                "offset": 30,
                "frequency": "mon",
                "units": "days",
                "calendar": "360_day",
                "diurnal_climatology": False,
            },
        ]
        cc = CMIP6CollectionsCheck()
        self.assertFalse(cc.check_external_contiguity(metadatas, "foo"))
        self.assertEqual(
            cc.results["foo_1.nc"],
            [{
                "index": "foo",
                "message": (
                    "Time variable does not appear to be "
                    "consistent with the frequency "
                    "attribute"
                )
            }]
        )

    def test_external_contiguity_with_inconsistent_offsets(self):
        metadatas = [
            {
                "filename": "foo_1.nc",
                "time_dim": [1.5, 2.5, 3.5],
                "time_bnds": [(1, 2), (2, 3), (3, 4)],
                "offset": 1.0,
                "frequency": "day",
                "units": "days",
                "calendar": "360_day",
                "diurnal_climatology": False,
            },
            {
                "filename": "foo_2.nc",
                "time_dim": [105, 135, 165],
                "time_bnds": [(90, 120), (120, 150), (150, 180)],
                "offset": 30,
                "frequency": "mon",
                "units": "days",
                "calendar": "360_day",
                "diurnal_climatology": False,
            },
        ]
        cc = CMIP6CollectionsCheck()
        self.assertFalse(cc.check_external_contiguity(metadatas, "foo"))
        self.assertEqual(
            cc.results["foo_2.nc"],
            [{
                "index": "foo",
                "message": (
                    "Inconsistent temporal offsets (1.0 and 30)"
                )
            }]
        )

    def test_valid_external_contiguity_diurnal_with_gap(self):
        metadatas = [
            {
                "filename": "foo_1.nc",
                "time_dim": [(i + 0.5) / 24.0 + 15.0 for i in range(24)],
                "time_bnds": [((i / 24.0), ((i + 1) / 24.0 + 29.0)) for i in range(24)],
                "offset": 1. / 24,
                "frequency": "1hrCM",
                "units": "days",
                "calendar": "360_day",
                "diurnal_climatology": True,
            },
            {
                "filename": "foo_2.nc",
                "time_dim":  [(i + 0.5) / 24.0 + 75.0 for i in range(24)],
                "time_bnds": [((i / 24.0 + 60.0), ((i + 1) / 24.0 + 89.0)) for i in range(24)],
                "offset": 1. / 24,
                "frequency": "1hrCM",
                "units": "days",
                "calendar": "360_day",
                "diurnal_climatology": True,
            },
        ]
        cc = CMIP6CollectionsCheck()
        self.assertFalse(cc.check_external_contiguity(metadatas, "foo"))
        self.assertEqual(
            cc.results["foo_2.nc"],
            [{
                "index": "foo",
                "message": "There is an inconsistency between foo_1.nc and foo_2.nc (a gap of 30 days)"
            }]
        )

    def test_time_bounds(self):
        metadatas = [
            {
                "filename": "foo_1.nc",
                "time_dim": [15, 45, 75],
                "time_bnds": [(0, 30), (30, 60), (60, 90)],
                "offset": 30,
                "frequency": "mon",
                "units": "days",
                "calendar": "360_day",
                "diurnal_climatology": False,
            },
            {
                "filename": "foo_2.nc",
                "time_dim": [105, 135, 165],
                "time_bnds": [(90, 120), (120, 150), (150, 180)],
                "offset": 30,
                "frequency": "mon",
                "units": "days",
                "calendar": "360_day",
                "diurnal_climatology": False,
            },
        ]
        request = Request({
            "run_bounds": "1850-01-01-00-00-00 1850-07-01-00-00-00",
            "child_base_date": "1850-01-01-00-00-00"
        }, [])
        cc = CMIP6CollectionsCheck()
        self.assertIsNone(cc.check_run_bounds(
            request,
            metadatas)
        )

    def test_imprecise_start_time_bound(self):
        metadatas = [
            {
                "filename": "foo_1.nc",
                "time_dim": [float(i) / (72.0) for i in range(1, 360 * 24 * 3 + 1)],
                "time_bnds": None,
                "offset": 1.0 / 72.0,
                "frequency": "subhrPt",
                "units": "days",
                "calendar": "360_day",
                "diurnal_climatology": False,
            },
        ]
        request = Request({
            "run_bounds": "1850-01-01-00-00-00 1851-01-01-00-00-00",
            "child_base_date": "1850-01-01-00-00-00"
        }, [])
        cc = CMIP6CollectionsCheck()
        self.assertIsNone(cc.check_run_bounds(
            request,
            metadatas)
        )

    def test_imprecise_end_time_bound(self):
        metadatas = [
            {
                "filename": "foo_1.nc",
                "time_dim": [float(i) / (72.0) for i in range(360 * 24 * 3)],
                "time_bnds": None,
                "offset": 1.0 / 72.0,
                "frequency": "subhrPt",
                "units": "days",
                "calendar": "360_day",
                "diurnal_climatology": False,
            },
        ]
        request = Request({
            "run_bounds": "1850-01-01-00-00-00 1851-01-01-00-00-00",
            "child_base_date": "1850-01-01-00-00-00"
        }, [])
        cc = CMIP6CollectionsCheck()
        self.assertIsNone(cc.check_run_bounds(
            request,
            metadatas)
        )

    def test_invalid_time_bounds(self):
        metadatas = [
            {
                "filename": "foo_1.nc",
                "time_dim": [15, 45, 75],
                "time_bnds": [(0, 30), (30, 60), (60, 90)],
                "offset": 30,
                "frequency": "mon",
                "units": "days",
                "calendar": "360_day",
                "diurnal_climatology": False,
            },
            {
                "filename": "foo_2.nc",
                "time_dim": [105, 135, 165],
                "time_bnds": [(90, 120), (120, 150), (150, 180)],
                "offset": 30,
                "frequency": "mon",
                "units": "days",
                "calendar": "360_day",
                "diurnal_climatology": False,
            },
        ]
        request = Request({
            "run_bounds": "1850-01-01-00-00-00 1851-01-01-00-00-00",
            "child_base_date": "1850-01-01-00-00-00"
        }, [])
        cc = CMIP6CollectionsCheck()
        self.assertEqual(
            cc.check_run_bounds(
                request,
                metadatas),
            ("End of the dataset (180 days since 1850-01-01-00-00-00) do not match the request "
             "date range (1851-01-01-00-00-00)")
        )

    def test_invalid_imprecise_start_time_bound(self):
        metadatas = [
            {
                "filename": "foo_1.nc",
                "time_dim": [float(i) / (72.0) for i in range(0, 360 * 24 * 3 - 1)],
                "time_bnds": None,
                "offset": 1.0 / 72.0,
                "frequency": "subhrPt",
                "units": "days",
                "calendar": "360_day",
                "diurnal_climatology": False,
            },
        ]
        request = Request({
            "run_bounds": "1850-01-01-00-00-00 1851-01-01-00-00-00",
            "child_base_date": "1850-01-01-00-00-00"
        }, [])
        cc = CMIP6CollectionsCheck()
        self.assertEqual(
            cc.check_run_bounds(
                request,
                metadatas),
            ("End of the dataset (359.97222222222223 days since 1850-01-01-00-00-00) do not match the request "
             "date range (1851-01-01-00-00-00)")
        )


if __name__ == '__main__':
    unittest.main()
