# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
"""
The :mod:`constants` module contains constants (values that should never
be changes by a user and exist for readability and maintainability
purposes) for CDDS Prepare.
"""
import os

ACTIVATE = 'activate'
ALLOWED_POSITIVE = ['up', 'down', None]
ARCHIVE_LOG_DIRECTORY_PERMISSIONS = 0o777

# Fields in which a change between data request versions is critical
CRITICAL_FIELDS = ['dimensions', 'cell_methods', 'units', 'positive']

CICE_HISTFREQ_FOR_VALIDATION = {'d': 10, 'h': 24}
CICE_VARIABLE_REMAP = {'icepresent': 'ice_present'}
DEACTIVATE = 'deactivate'
DEACTIVATION_RULE_LOCATION = 'https://code.metoffice.gov.uk/svn/cdds/variable_issues/trunk/'
EPILOG = ('For a full description of this script, please refer to the '
          'documentation available via '
          'https://code.metoffice.gov.uk/doc/cdds/cdds_prepare/index.html')

MIP_TABLES_DIR = '{}/mip_tables/CMIP6/01.00.29'.format(os.environ['CDDS_ETC'])
MODEL_TYPE_MAP = {'atmos': ('AGCM', 'AOGCM'),
                  'ocean': ('AOGCM', 'OGCM')}
OBGC_MODEL_STRING = 'BGC'

# The following relates the NEMO and CICE output streams to a string used to
# identify the frequency of a particular variable. For CICE this is the flag
# in the namelist, while for NEMO it is the id attribute within a file_group
# object inside the iodef.xml file.
OCEAN_STREAMS = {'inm': 'd', 'ind': 'h', 'ond': '1d', 'onm': '1m'}
PRIORITY_UNSET = 99

# Log messages that variable is / is not in inventory:
VARIABLE_IN_INVENTORY_LOG = 'Variable "{}/{}" is in the inventory database settings active: "{}".'
VARIABLE_NOT_IN_INVENTORY_LOG = 'Variable "{}/{}" can not be found in the inventory database.'

# Comments of approved variable that in inventory
VARIABLE_IN_INVENTORY_COMMENT = 'Data set "{}" version "{}" found in inventory with status "{}"'
