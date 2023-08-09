# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.
import numpy as np

from dataclasses import dataclass
from typing import Any, Tuple, Dict


DEFAULT_GRID: str = 'default'


@dataclass
class Mask:
    stream: str
    grid_name: str
    slice_latitude: slice
    slice_longitude: slice

    def slice(self) -> Tuple[Any, slice, slice]:
        """
        Applies the result of numpy slice function corresponding to
        the stored slice latitude and slice longitude.

        :return: Slice for this mask data
        :rtype: Tuple[ellipsis, slice, slice]
        """
        return np.s_[..., self.slice_latitude, self.slice_longitude]


def load_mask_from_config(mask_key: str, mask_value: str) -> Tuple[str, str, Mask]:
    key_splits = mask_key.split('_')
    stream_name = key_splits[1]
    grid_name = DEFAULT_GRID
    if len(key_splits) == 3:
        grid_name = key_splits[2]
    slice_latitude, slice_longitude = _split_mask_value(mask_value)
    return stream_name, grid_name, Mask(stream_name, grid_name, slice_latitude, slice_longitude)


def _split_mask_value(mask_slice_str: str):
    slice_lat_str, slice_long_str = mask_slice_str.replace(' ', '').split(',')
    slice_latitude = slice(*[None if j.lower() in ('none', '') else int(j) for j in slice_lat_str.split(':')])
    slice_longitude = slice(*[None if j.lower() in ('none', '') else int(j) for j in slice_long_str.split(':')])
    return slice_latitude, slice_longitude
