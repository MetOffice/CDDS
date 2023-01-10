# (C) British Crown Copyright 2019-2021, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`constants` module contains constants (values that should never
be changes by a user and exist for readability and maintainability
purposes) for CDDS archive.
"""

DATA_PUBLICATION_STATUS_DICT = {
    'AVAILABLE': 'available',
    'EMBARGOED': 'embargoed',
    'SUPERSEDED': 'superseded',
    'WITHDRAWN': 'withdrawn',
}
# based in table 2 of page 16 of the following document:
# https://docs.google.com/document/d/
#     1h0r8RZr_f3-8egBMMh7aqLwy3snpD6_MrDz1q8n5XUk/edit
OUTPUT_FILE_DT_STR = {
    'yr': {'str': '%Y', 'delta': [360, 0]},
    'yrPt': {'str': '%Y', 'delta': [360, 0]},
    'dec': {'str': '%Y', 'delta': [360, 0]},
    'mon': {'str': '%Y%m', 'delta': [30, 0]},
    'monC': {'str': '%Y%m', 'delta': [30, 0]},
    'day': {'str': '%Y%m%d', 'delta': [1, 0]},
    '6hr': {'str': '%Y%m%d%H%M', 'delta': [0, 6 * 3600]},
    '3hr': {'str': '%Y%m%d%H%M', 'delta': [0, 3 * 3600]},
    '1hr': {'str': '%Y%m%d%H%M', 'delta': [0, 1 * 3600]},
    '1hrCM': {'str': '%Y%m%d%H%M', 'delta': [0, 1 * 3600]},
    '6hrPt': {'str': '%Y%m%d%H%M', 'delta': [0, 6 * 3600]},
    '3hrPt': {'str': '%Y%m%d%H%M', 'delta': [0, 3 * 3600]},
    '1hrPt': {'str': '%Y%m%d%H%M', 'delta': [0, 1 * 3600]},
    # None in the list below forces the code to pick up the offset from the
    # filenames themselves
    'subhrPt': {'str': '%Y%m%d%H%M%S', 'delta': [0, None]},
}

MASS_STATUS_DICT = {
    'FIRST_PUBLICATION':
        {'description': 'First publication',
         'valid': True,
         },
    'PROCESSING_CONTINUATION':
        {'description': 'Continue aborted data storage process',
         'valid': True,
         },
    'APPENDING':
        {'description': 'Append (in time) to already published data.',
         'valid': True,
         },
    'PREPENDING':
        {'description': 'Prepend (in time) to already published data.',
         'valid': True,
         },
    'PREVIOUSLY_WITHDRAWN':
        {
            'description': 'Publishing data for variable where '
                           'previously withdrawn.',
            'valid': True,
        },
    'ALREADY_PUBLISHED':
        {
            'description': 'Attempting to publish data for variable '
                           'and time period already in available state.',
            'valid': False,
        },
    'PARTIALLY_PUBLISHED':
        {
            'description': 'Attempting to publish data for variable and time '
                           'period where part of the time period is already '
                           'in available state.',
            'valid': False,
        },
    'DATESTAMP_REUSE':
        {
            'description': 'Attempting to publish data with a previously '
                           'used datestamp.',
            'valid': False,
        },
    'MULTIPLE_EMBARGOED':
        {
            'description': 'Attempting to publish data when there is '
                           'already data in the embargoed state with '
                           'a different datestamp.',
            'valid': False,
        },
    'UNKNOWN':
        {
            'description': 'Unknown invalid state.',
            'valid': False,
        },
}
SPICE_STORE_LOG_NAME = 'cdds_store_spice.log'
SPICE_STORE_MEMORY = '1G'
SPICE_STORE_QUEUE = 'normal'
SPICE_STORE_SCRIPT_NAME = 'cdds_store_spice.sh'
SPICE_STORE_WALLTIME = '06:00:00'
STORE_COMMAND = 'cdds_store {args}'
SUPERSEDED_INFO_FILE_STR = '{mip_table_id}_{variable_id}_superseded.log'
VARIABLE_OUTPUT_SUBPATH_FACET_STRING = 'stream_id|mip_table_id|variable_id'
