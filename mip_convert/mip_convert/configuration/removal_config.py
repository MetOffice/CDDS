# (C) British Crown Copyright 2024, Met Office.
# Please see LICENSE.rst for license details.
import numpy as np

from dataclasses import dataclass
from typing import Tuple, Any


@dataclass
class HaloRemoval:
    """
    Contains all information you need to remove halo values
    """
    stream: str
    slice_latitude: slice
    slice_longitude: slice


def load_halo_removal_from_config(removal_key: str, removal_value: str) -> Tuple[str, HaloRemoval]:
    """
    Returns the halo removal specified in the removal_key and removal_value.

    The removal_value represents the slices of latitude and longitude
    as a string:
    '<lat_start>:<lat_stop>:<lat_step>,<lon_start>:<long_stop>:<long_step>'

    :param removal_key: Contains the stream name
    :type removal_key: str
    :param removal_value: Contains the removal for the latitude and longitude
    :type removal_value: str
    :return: stream name and removal masking
    :rtype: Tuple[str, str, HaloRemoval]
    """
    key_splits = removal_key.split('_')
    stream_name = key_splits[1]
    slice_latitude, slice_longitude = _split_halo_removal_value(removal_value)
    return stream_name, HaloRemoval(stream_name, slice_latitude, slice_longitude)


def _split_halo_removal_value(removal_slice_str: str) -> Tuple[slice, slice]:
    """
    Returns the slices of latitude and longitude defined in the given string.
    The given halo removal string is composed like:
    '<lat_start>:<lat_stop>:<lat_step>,<lon_start>:<long_stop>:<long_step>'

    :param removal_slice_str: Contains the latitude and longitude removals
    :type removal_slice_str: str
    :return: The latitude slice and the longitude slice
    :rtype: Tuple[slice, slice]
    """
    slice_lat_str, slice_long_str = removal_slice_str.replace(' ', '').split(',')
    slice_latitude = slice(*[None if j.lower() in ('none', '') else int(j) for j in slice_lat_str.split(':')])
    slice_longitude = slice(*[None if j.lower() in ('none', '') else int(j) for j in slice_long_str.split(':')])
    return slice_latitude, slice_longitude
