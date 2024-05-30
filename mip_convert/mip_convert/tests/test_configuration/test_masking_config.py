# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
from unittest import TestCase

from mip_convert.configuration.masking_config import load_mask_from_config


class TestLoadMaskFromConfig(TestCase):

    def test_masking_loading(self):
        stream, grid, mask = load_mask_from_config('stream_onm_grid-T', '-1:,180:')
        self.assertEqual(stream, 'onm')
        self.assertEqual(grid, 'grid-T')
        self.assertEqual(mask.slice_latitude.start, -1)
        self.assertEqual(mask.slice_latitude.stop, None)
        self.assertEqual(mask.slice_latitude.step, None)
        self.assertEqual(mask.slice_longitude.start, 180)
        self.assertEqual(mask.slice_longitude.stop, None)
        self.assertEqual(mask.slice_longitude.step, None)

    def test_masking_loading_default_grid(self):
        stream, grid, mask = load_mask_from_config('stream_inm', '-1:2,180:300')
        self.assertEqual(stream, 'inm')
        self.assertEqual(grid, 'default')
        self.assertEqual(mask.slice_latitude.start, -1)
        self.assertEqual(mask.slice_latitude.stop, 2)
        self.assertEqual(mask.slice_latitude.step, None)
        self.assertEqual(mask.slice_longitude.start, 180)
        self.assertEqual(mask.slice_longitude.stop, 300)
        self.assertEqual(mask.slice_longitude.step, None)
