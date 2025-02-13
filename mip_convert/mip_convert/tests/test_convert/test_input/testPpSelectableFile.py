# (C) British Crown Copyright 2015-2021, Met Office.
# Please see LICENSE.md for license details.

import unittest

from mip_convert.load.user_config import PpRequestVariable

from mip_convert.load.pp.stash_code import StashCode

from mip_convert.load.pp.pp import PpFileFactory
from mip_convert.load.pp.pp import PpError

from header_util import BaseHeader


class DummyPpField(object):

    def __init__(self, data):
        self.baseData = data


class DummyPpBaseFile(object):
    UNLOADED = -99

    def __init__(self, headers, extras, data):
        self.headers = headers
        self.extras = extras
        self.data = data
        self.loaded = self.UNLOADED
        self.closed = False
        self.filename = None

    def _pos(self, pos):
        return pos - 1

    def loadField(self, pos, force=False):
        """
        act as a stub pp_file
        """
        self.loaded = pos
        return self.data[self._pos(pos)]  # fields are indexed from 1

    def unloadField(self, pos):
        """
        act as a stub pp_file
        """
        if pos != self.loaded:
            raise Exception('unexpected unload')  # better condition?
        self.loaded = self.UNLOADED

    def allUnloaded(self):
        return self.loaded == self.UNLOADED

    def getExtraDataVectors(self, pos):
        """
        act as a stub pp_file
        """
        return self.extras[self._pos(pos)]

    def close(self):
        self.closed = True


class TestPpSelectableFile(unittest.TestCase):

    # act as a variable generator
    def makeVariable(self, headers, extras, datas):
        """
        act as a stub makeVariable
        """
        self._headers_made = headers
        self._extras_made = extras
        self._datas_made = datas

        return self

    def openpp(self, filename, failOnError=False):  # act as pp module
        """
        stub pp opener
        """
        self.base_file.filename = filename
        self.failOnError = failOnError
        return self.base_file

    def _get_var(self, stash):
        request = PpRequestVariable(None, None, None, None)
        pp_var = self.pp_file.read_selection(stash.asMsi(), **request.match_keys())
        return pp_var

    def _get_selected(self, msi):
        request = PpRequestVariable(None, None, None, None)
        return self.pp_file.select(msi, request)

    def _make_multi_lev_time(self, lbvc, levels, month_range, stash):
        headers = list()
        for month in range(month_range):
            for (lbuser4, lbuser7) in stash:
                for level in levels:
                    header = BaseHeader(lbuser4=lbuser4,
                                        lbuser7=lbuser7,
                                        lbvc=lbvc,
                                        blev=level,
                                        lbyr=1990,
                                        lbmon=month + 1,
                                        lbdat=1)
                    headers.append(header)
        return headers

    def _make_base_file(self, headers):
        data = []
        for index, header in enumerate(headers):
            data.append(DummyPpField([index + x for x in range(header.lbrow * header.lbnpt)]))

        extra = [{'item': x} for x in range(len(headers))]
        self.base_file = DummyPpBaseFile(headers, extra, data)

    def _make_selectable_file(self):
        self.pp_file = self.pp_factory.openFile(self.filePath)

    def _make_dummy_file(self, headers):
        self._make_base_file(headers)
        self._make_selectable_file()

    def _getExpected(self, stash):
        expected = list()
        extras = list()
        headers = list()
        for (input_file, header) in enumerate(self.base_file.headers):
            if header.stash_code() == stash:  # build up expected
                headers.append(header)
                expected.append(self.base_file.data[input_file].baseData)
                extras.append(self.base_file.extras[input_file])

        return headers, extras, expected

    def setUp(self):
        self.timestep = 50.
        self.failOnError = False
        self.filePath = '/path/to/a/file'
        self.pp_factory = PpFileFactory(self.timestep, self, self)

    def assertOnData(self, pp_var, stash):
        (headers, extras, expected) = self._getExpected(stash)

        self.assertEqual(self, pp_var)
        self.assertEqual(headers, self._headers_made)
        self.assertEqual(expected, self._datas_made)
        self.assertEqual(extras, self._extras_made)
        self.assertTrue(self.base_file.allUnloaded())

    def testPathName(self):
        self._make_dummy_file([])
        self.assertEqual(self.filePath, self.pp_file.pathname)
        self.assertTrue(self.failOnError)
        self.assertEqual(self.timestep, self.pp_file.timestep)
        self.assertEqual(self.pp_factory, self.pp_file.opener)

    def testClose(self):
        self._make_dummy_file([])
        self.pp_file.close()
        self.assertTrue(self.base_file.closed)

    def testReadData(self):
        stashcodes = ((1, 1), (1, 2))
        levels = [100, 200]
        headers = self._make_multi_lev_time(1, levels, 3, stashcodes)
        self._make_dummy_file(headers)

        for (item, model) in stashcodes:
            stash = StashCode(model, 0, item)
            pp_var = self._get_var(stash)
            self.assertOnData(pp_var, stash)

    def testMissingVariable(self):
        headers = [BaseHeader(lbuser4=1, lbuser7=1)]
        self._make_dummy_file(headers)
        request = PpRequestVariable(None, None, None, None)
        self.assertRaises(PpError, self.pp_file.read_selection, 'm02s00i001', **request.match_keys())


if __name__ == '__main__':
    unittest.main()
