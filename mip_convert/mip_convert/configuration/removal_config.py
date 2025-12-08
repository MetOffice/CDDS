# (C) British Crown Copyright 2024-2025, Met Office.
# Please see LICENSE.md for license details.
import numpy as np

from dataclasses import dataclass
from typing import Tuple, Any


@dataclass
class HaloRemoval:
    """Contains all information you need to remove halo values"""
    stream: str
    slice_latitude: slice
    slice_longitude: slice


def load_halo_removal_from_config(removal_key: str, removal_value: str) -> Tuple[str, HaloRemoval]:
    """Returns the halo removal specified in the removal_key and removal_value.

    The removal_value represents the slices of latitude and longitude
    as a string:
    '<lat_start>:<lat_stop>:<lat_step>,<lon_start>:<long_stop>:<long_step>'

    Parameters
    ----------
    removal_key : str
        Contains the stream name
    removal_value : str
        Contains the removal for the latitude and longitude

    Returns
    -------
    Tuple[str, str, HaloRemoval]
        stream name and removal masking
    """
    key_splits = removal_key.split('_')
    stream_name = key_splits[1]
    slice_latitude, slice_longitude = _split_halo_removal_value(removal_value)
    return stream_name, HaloRemoval(stream_name, slice_latitude, slice_longitude)


def _split_halo_removal_value(removal_slice_str: str) -> Tuple[slice, slice]:
    """Returns the slices of latitude and longitude defined in the given string.
    The given halo removal string is composed like:
    '<lat_start>:<lat_stop>:<lat_step>,<lon_start>:<long_stop>:<long_step>'

    Parameters
    ----------
    removal_slice_str : str
        Contains the latitude and longitude removals

    Returns
    -------
    Tuple[slice, slice]
        The latitude slice and the longitude slice
    """
    slice_lat_str, slice_long_str = removal_slice_str.replace(' ', '').split(',')
    slice_latitude = slice(*[None if j.lower() in ('none', '') else int(j) for j in slice_lat_str.split(':')])
    slice_longitude = slice(*[None if j.lower() in ('none', '') else int(j) for j in slice_long_str.split(':')])
    return slice_latitude, slice_longitude
