# (C) British Crown Copyright 2023-2025, Met Office.
# Please see LICENSE.md for license details.
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
