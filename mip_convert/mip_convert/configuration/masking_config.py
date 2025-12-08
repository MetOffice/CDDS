# (C) British Crown Copyright 2023-2025, Met Office.
# Please see LICENSE.md for license details.
import numpy as np

from dataclasses import dataclass
from typing import Any, Tuple, Dict


DEFAULT_GRID: str = 'default'


@dataclass
class Mask:
    """Contains all information you need to mask values
    used for a grid in a specific stream
    """
    stream: str
    grid_name: str
    slice_latitude: slice
    slice_longitude: slice

    def slice(self) -> Tuple[Any, slice, slice]:
        """Applies the result of numpy slice function corresponding to
        the stored slice latitude and slice longitude.

        Returns
        -------
        Tuple[ellipsis, slice, slice]
            Slice for this mask data
        """
        return np.s_[..., self.slice_latitude, self.slice_longitude]


def load_mask_from_config(mask_key: str, mask_value: str) -> Tuple[str, str, Mask]:
    """Returns the masking specified in the mask_key and mask_value.

    The mask_key composed of the grid and stream that masking is for:
    <stream_name>_<grid_name>
    If the gird name is not given, the masking is for every grid in
    this stream.

    The mask_value represents the slices of latitude and longitude
    as a string:
    '<lat_start>:<lat_stop>:<lat_step>,<lon_start>:<long_stop>:<long_step>'

    Parameters
    ----------
    mask_key : str
        Contains the stream name and grid
    mask_value : str
        Contains the masking for the latitude and longitude

    Returns
    -------
    Tuple[str, str, Mask]
        stream name, grid name and masking
    """
    key_splits = mask_key.split('_')
    stream_name = key_splits[1]
    grid_name = DEFAULT_GRID
    if len(key_splits) == 3:
        grid_name = key_splits[2]
    slice_latitude, slice_longitude = _split_mask_value(mask_value)
    return stream_name, grid_name, Mask(stream_name, grid_name, slice_latitude, slice_longitude)


def _split_mask_value(mask_slice_str: str) -> Tuple[slice, slice]:
    """Returns the slices of latitude and longitude defined in the given string.
    The given masking string is composed like:
    '<lat_start>:<lat_stop>:<lat_step>,<lon_start>:<long_stop>:<long_step>'

    Parameters
    ----------
    mask_slice_str : str
        Contains the latitude and longitude masking

    Returns
    -------
    Tuple[slice, slice]
        The latitude slice and the longitude slice
    """
    slice_lat_str, slice_long_str = mask_slice_str.replace(' ', '').split(',')
    slice_latitude = slice(*[None if j.lower() in ('none', '') else int(j) for j in slice_lat_str.split(':')])
    slice_longitude = slice(*[None if j.lower() in ('none', '') else int(j) for j in slice_long_str.split(':')])
    return slice_latitude, slice_longitude
