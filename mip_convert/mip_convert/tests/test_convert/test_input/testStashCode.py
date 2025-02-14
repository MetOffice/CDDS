# (C) British Crown Copyright 2015-2025, Met Office.
# Please see LICENSE.md for license details.

import unittest

from mip_convert.load.pp.stash_code import from_msi
from mip_convert.load.pp.stash_code import from_header
from mip_convert.load.pp.stash_code import StashCode


class TestStashCode(unittest.TestCase):

    def header_dict(self, model, sec_item):
        return {
            'lbuser7': int(model),
            'lbuser4': int(sec_item),
        }

    def testInvalidMsiRaisesValueError(self):
        self.assertRaises(ValueError, from_msi, "invalid")

    def testEquals(self):
        ref_stash = (1, 0, 1)
        examples = [
            ((1, 0, 1), True),
            ((1, 0, 2), False),
            ((1, 1, 1), False),
            ((2, 0, 1), False),
        ]
        for (stash2, expected) in examples:
            self.assertEqual(expected, StashCode(*ref_stash) == StashCode(*stash2))

    def testOutput(self):
        examples = [
            (1, 1, 1, '1001', 'm01s01i001'),
            (2, 30, 1, '30001', 'm02s30i001'),
            (1, 0, 1, '1', 'm01s00i001'),
        ]
        for (model, section, item, section_item, msi) in examples:
            code = StashCode(model, section, item)
            self.assertEqual(section_item, code.asSecItem())
            self.assertEqual(msi, code.asMsi())
            self.assertEqual(self.header_dict(model, section_item), code.asDict())

    def testFromMsiString(self):
        code = from_msi("m01s01i001")
        self.assertEqual(StashCode(1, 1, 1), code)

    def testFromPpHeader(self):
        self.lbuser4 = 1 * 1000 + 1
        self.lbuser7 = 1
        code = from_header(self)
        self.assertEqual(StashCode(1, 1, 1), code)


if __name__ == '__main__':
    unittest.main()
