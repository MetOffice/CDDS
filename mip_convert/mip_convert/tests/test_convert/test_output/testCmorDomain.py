# (C) British Crown Copyright 2015-2025, Met Office.
# Please see LICENSE.md for license details.

import unittest

from util import *

from mip_convert.common import SITE_TYPE
from mip_convert.save.cmor.cmor_outputter import CmorDomain

from mip_convert.save.cmor.cmor_outputter import CmorOutputError


class DummyMaker(object):

    def __init__(self, entry, a_id):
        self.entry = entry
        self.aid = a_id

    def cmorGridId(self):
        return self.aid

    def cmorId(self):
        return self.aid

    def id_for_variable(self):
        return self.aid

    def id_for_zfactor(self):
        return self.aid

    def set_horizontal(self, ids):
        self.horiz_ids = ids


class TestGetAxisIds(unittest.TestCase):

    def axis_dirs(self):
        return self._axis_dirs

    def getAxisMaker(self, axis_dir, avar):
        return self.makers[axis_dir]

    def getAxisMakerDict(self):
        """test acts as stub axis_map"""
        ids = list(range(len(self.entries)))
        for (axis_direction, entry, a_id) in zip(self._axis_dirs, self.entries, ids):
            self.ids.append(a_id)
            maker = DummyMaker(entry, a_id)
            self.makers[axis_direction] = maker
        return self.makers

    def setUp(self):
        self.makers = dict()
        self.ids = list()
        self.var = DummyVar()

    def has_axis(self, axis_dir):
        return axis_dir in self._axis_dirs

    def has_time(self):
        return self.has_axis('T')

    def z_axis(self):
        result = []
        if 'Z' in self.axis_dirs():
            result = ['Z']
        return result

    def horizontal_axes(self):
        return [axis for axis in self.axis_dirs() if axis in ('X', 'Y', 'site')]

    def is_horizontal(self, axis_dir):
        return axis_dir in ('Y', 'X', SITE_TYPE)

    def non_spatial_axes(self):
        result = []
        for axis in self.axis_dirs():
            if axis not in self.horizontal_axes() and axis not in self.z_axis():
                result.append(axis)
        return result

    def testVarNoTime(self):
        self.entries = ('latitude', 'longitude')
        self._axis_dirs = ('Y', 'X')
        self.var.axes = [
            DummyAxis(units='days since XXXX', data=list(range(1)), axis='T'),
            DummyAxis(units='', data=list(range(1)), axis='Z'),
            DummyAxis(units='', data=['landcover'], axis='vegtype'),
            DummyAxis(units='degrees_north', data=list(range(1, 3, 2)), axis='Y'),
            DummyAxis(units='degrees_east', data=list(range(2)), axis='X', no_bounds=True),
        ]

        self.axis_provider = CmorDomain(self)
        self.assertFalse(self.axis_provider.has_time())

    def testVarSingletonHeightAndVegTye(self):
        self.entries = ('time', 'latitude', 'longitude')
        self._axis_dirs = ('T', 'Y', 'X')
        self.var.axes = [
            DummyAxis(units='days since XXXX', data=list(range(1)), axis='T'),
            DummyAxis(units='', data=list(range(1)), axis='Z'),
            DummyAxis(units='', data=['landcover'], axis='vegtype'),
            DummyAxis(units='degrees_north', data=list(range(1, 3, 2)), axis='Y'),
            DummyAxis(units='degrees_east', data=list(range(2)), axis='X', no_bounds=True),
        ]

        self.axis_provider = CmorDomain(self)
        self.getAxisMakerDict()
        ids = self.axis_provider.getAxisIds(self.var)

        self.assertTrue(self.axis_provider.has_time())
        self.assertEqual(self.ids, ids)

        # test repeat call is safe (bug overwriting static)
        self.axis_provider = CmorDomain(self)
        self.axis_provider.getAxisIds(self.var)
        self.assertTrue(True)

    def testVegTypeDomain(self):
        self.entries = ('time', 'vegtype', 'latitude', 'longitude')
        self._axis_dirs = ('T', 'vegtype', 'Y', 'X')
        self.var.axes = [
            DummyAxis(units='days since XXXX', data=list(range(1)), axis='T'),
            DummyAxis(units='1', data=['vegtype1'], axis='vegtype'),
            DummyAxis(units='degrees_north', data=list(range(1, 3, 2)), axis='Y'),
            DummyAxis(units='degrees_east', data=list(range(2)), axis='X', no_bounds=True),
        ]

        self.axis_provider = CmorDomain(self)
        self.getAxisMakerDict()
        ids = self.axis_provider.getAxisIds(self.var)

        self.assertEqual(self.ids, ids)

    def testHybridHeight(self):
        self.entries = ('time', 'hybrid_height', 'latitude', 'longitude')
        self._axis_dirs = ('T', 'Z', 'Y', 'X')
        self.var.axes = [
            DummyAxis(units='days since XXXX', data=list(range(1)), axis='T'),
            DummyHybrid(units='m', data=list(range(2)), axis='Z'),
            DummyAxis(units='degrees_north', data=list(range(1, 3, 2)), axis='Y'),
            DummyAxis(units='degrees_east', data=list(range(2)), axis='X', no_bounds=True),
        ]

        self.axis_provider = CmorDomain(self)
        self.getAxisMakerDict()
        ids = self.axis_provider.getAxisIds(self.var)

        self.assertEqual(self.ids, ids)
        self.assertEqual([self.makers['Y'].cmorId(), self.makers['X'].cmorId()], self.makers['Z'].horiz_ids)

    def testSiteDomain(self):
        self.entries = ('time', 'site', 'hybrid_height')
        self._axis_dirs = ('T', SITE_TYPE, 'Z')
        self.var.axes = [
            DummyAxis(units='days since XXXX', data=list(range(1)), axis='T'),
            DummyAxis(units='', data=list(range(2)), axis=SITE_TYPE, no_bounds=True),
            DummyHybrid(units='m', data=list(range(2)), axis='Z'),
        ]

        self.axis_provider = CmorDomain(self)
        self.getAxisMakerDict()
        ids = self.axis_provider.getAxisIds(self.var)

        self.assertEqual(self.ids, ids)
        self.assertEqual([self.makers[SITE_TYPE].cmorId(), ], self.makers['Z'].horiz_ids)

    def testErrorOnNonSingletonHeight(self):
        self.entries = ('time', 'latitude', 'longitude')
        self._axis_dirs = ('T', 'Y', 'X')
        self.var.axes = [
            DummyAxis(units='days since XXXX', data=list(range(1)), axis='T'),
            DummyAxis(units='m', data=list(range(2)), axis='Z'),
            DummyAxis(units='degrees_north', data=list(range(1, 3, 2)), axis='Y'),
            DummyAxis(units='degrees_east', data=list(range(2)), axis='X', no_bounds=True),
        ]

        self.axis_provider = CmorDomain(self)
        self.getAxisMakerDict()
        self.assertRaises(CmorOutputError, self.axis_provider.getAxisIds, self.var)

    def testErrorOnNonSingletonVegType(self):
        self.entries = ('time', 'latitude', 'longitude')
        self._axis_dirs = ('T', 'Y', 'X')
        self.var.axes = [
            DummyAxis(units='days since XXXX', data=list(range(1)), axis='T'),
            DummyAxis(units='', data=list(range(2)), axis='vegtype'),
            DummyAxis(units='degrees_north', data=list(range(1, 3, 2)), axis='Y'),
            DummyAxis(units='degrees_east', data=list(range(2)), axis='X', no_bounds=True),
        ]

        self.axis_provider = CmorDomain(self)
        self.getAxisMakerDict()
        self.assertRaises(CmorOutputError, self.axis_provider.getAxisIds, self.var)

    def testBareSoil(self):
        # should not call the axis definition for baresoil.
        #  This test is not cast very explicitly.  I don't like it
        self.entries = ('time', 'latitude', 'longitude')
        self._axis_dirs = ('T', 'Y', 'X', 'baresoil')
        self.var.axes = [
            DummyAxis(units='days since XXXX', data=list(range(1)), axis='T'),
            DummyAxis(units='degrees_north', data=list(range(1, 3, 2)), axis='Y'),
            DummyAxis(units='degrees_east', data=list(range(2)), axis='X', no_bounds=True),
        ]

        self.axis_provider = CmorDomain(self)
        self.getAxisMakerDict()
        self.axis_provider.getAxisIds(self.var)
        pass


if __name__ == '__main__':
    unittest.main()
