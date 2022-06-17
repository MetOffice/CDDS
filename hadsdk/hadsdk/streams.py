# (C) British Crown Copyright 2018-2021, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`streams` module contains the code required to handle
|streams|.
"""
import os
import re

from hadsdk.config import load_override_values


# def retrieve_stream_id(variable_name, mip_table_id, mip_era, overrides_path):
#     """
#     Return the |stream identifier| for the |MIP requested variable|.
#
#     If a |stream identifier| override for the |MIP requested variable|
#     exists in ``streams.cfg``, it is used over the default
#     |stream identifier| for the |MIP table|. If no |stream identifier|
#     is found, ``unknown`` is returned.
#
#     Parameters
#     ----------
#     variable_name: str
#         The |MIP requested variable name|.
#     mip_table_id : str
#         The |MIP table identifier|.
#     mip_era: str
#         The |MIP era|.
#     overrides_path: str
#         The full path to the configuration file containing the
#         |stream identifier| overrides.
#
#     Returns
#     -------
#     : (str, str)
#         The |stream identifier| for the |MIP requested variable| and
#         the substream, if available (else None).
#     """
#     try:
#         mip_table = '{}_{}'.format(mip_era, mip_table_id)
#         stream = load_override_values(overrides_path)[mip_table][variable_name]
#     except KeyError:
#         try:
#             stream = default_stream_ids()[mip_era][mip_table_id]
#         except KeyError:
#             stream = 'unknown'
#
#     stream_pattern = r'([\w]+)'
#     substream_pattern = r'([\w-]+)'
#     pattern = '{}/{}'.format(stream_pattern, substream_pattern)
#
#     substream_search = re.match(pattern, stream)
#     if substream_search is not None:
#         stream, substream = substream_search.groups()[:2]
#     else:
#         substream = None
#
#     return stream, substream
#
#
# def default_stream_ids():
#     """
#     Return the default |stream identifiers|.
#     """
#     return {
#         'CMIP5': {
#             '3hr': 'apk', '6hrPlev': 'apc', '6hrlev': 'apg', 'Amon': 'apm',
#             'Lmon': 'apm', 'LImon': 'apm', 'Oday': 'opa', 'Omon': 'opm',
#             'Oyr': 'opy', 'CF3hr': 'apk', 'CFday': 'apa', 'CFmon': 'apm',
#             'CFsubhr': 'ape', 'day': 'apa'},
#         'CMIP6': {
#             '3hr': 'ap8', '6hrLev': 'ap7', '6hrPlev': 'ap7',
#             '6hrPlevPt': 'ap7', 'AERday': 'ap6', 'AERhr': 'ap9',
#             'AERmon': 'ap4', 'AERmonZ': 'ap4', 'Amon': 'ap5', 'CF3hr': 'ap8',
#             'CFday': 'ap6', 'CFmon': 'ap5', 'CFsubhr': 'apt', 'E1hr': 'ap9',
#             'E1hrClimMon': 'ap9', 'E3hr': 'ap8', 'E3hrPt': 'ap8',
#             'E6hrZ': 'ap7', 'Eday': 'ap6', 'EdayZ': 'ap6', 'Efx': 'ancil',
#             'Emon': 'ap5', 'EmonZ': 'ap5', 'Esubhr': 'apt', 'Eyr': 'ap5',
#             'LImon': 'ap5', 'Lmon': 'ap5', 'Oday': 'ond', 'Ofx': 'ancil',
#             'Omon': 'onm', 'SIday': 'ind', 'SImon': 'inm', 'day': 'ap6',
#             'fx': 'ancil', 'prim1hrpt': 'ap9', 'prim3hr': 'ap8',
#             'prim3hrpt': 'ap8', 'prim6hr': 'ap7', 'prim6hrpt': 'ap7',
#             'primDay': 'ap6', 'primMon': 'ap5', 'primSIday': 'ap6',
#             'Cres6hrPt': 'ap7', 'CresAERmon': 'ap4', 'CresAERday': 'ap6',
#             'Cres1HrMn': 'ap9'},
#         'GCModelDev': {
#             'Amon': 'apm'}
#     }


# def get_files_per_year(stream_id, highres=False):
#     """
#     Calculates how many files of input data are expected per year for a
#     particular stream.
#
#     Parameters
#     ----------
#     stream_id: str
#         The |Stream ID| to get the number of files for.
#     highres: bool
#         True if processing high resolution model data.
#
#     Returns
#     -------
#     : int
#         The number of files per year for the specified stream.
#     """
#
#     stream_length = {
#         "ap4": 12,
#         "ap5": 12,
#         "apu": 12,
#         "apm": 12,
#         "apt": 36,
#         "onm": 12,
#         "inm": 12,
#         "ap6": 36,
#         "ap7": 36,
#         "ap8": 36,
#         "ap9": 36,
#         "ond": 12 if highres else 4,
#         "ind": 12,
#     }
#     return stream_length[stream_id]


# def calculate_expected_number_of_files(stream, substreams,
#                                        highres=False):
#     """Calculates expected number of files in a stream
#
#     Parameters
#     ----------
#     stream: dict
#         stream attributes
#     substreams: list
#         list of substreams
#     highres: boolean
#         True if files are on eORCA025 grid, False if on eORCA1.
#     Returns
#     -------
#     int
#         expected no. of files
#     """
#
#     years = stream["end_date"].year - stream["start_date"].year
#     months = stream["end_date"].month - stream["start_date"].month
#     expected_files = ((years * 12 + months) / 12.0 * get_files_per_year(
#         stream["stream"], highres) * len(substreams))
#     return int(expected_files)
#
#
# def stream_overrides():
#     """
#     Return the full path to the file containing the stream overrides.
#     """
#     return os.path.join(os.path.dirname(__file__), 'streams.cfg')
