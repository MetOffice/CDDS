# (C) British Crown Copyright 2019-2025, Met Office.
# Please see LICENSE.md for license details.
"""The :mod:`constants` module contains constants (values that should never be changed by a user and exist for
readability and maintainability purposes) for CDDS archive.
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
    'yr': {'str': '%Y', "iso": "P1Y"},
    'yrPt': {'str': '%Y', "iso": "P1Y"},
    'dec': {'str': '%Y', "iso": "P1Y"},
    'mon': {'str': '%Y%m', "iso": "P1M"},
    'monC': {'str': '%Y%m', "iso": "P1M"},
    'day': {'str': '%Y%m%d', "iso": "P1D"},
    '6hr': {'str': '%Y%m%d%H%M', "iso": "PT6H"},
    '3hr': {'str': '%Y%m%d%H%M', "iso": "PT3H"},
    '1hr': {'str': '%Y%m%d%H%M', "iso": "PT1H"},
    '1hrCM': {'str': '%Y%m%d%H%M', "iso": "PT1H"},
    '6hrPt': {'str': '%Y%m%d%H%M', "iso": "PT6H"},
    '3hrPt': {'str': '%Y%m%d%H%M', "iso": "PT3H"},
    '1hrPt': {'str': '%Y%m%d%H%M', "iso": "PT1H"},
    # None in the list below forces the code to pick up the offset from the
    # filenames themselves
    'subhrPt': {'str': '%Y%m%d%H%M%S'},
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
