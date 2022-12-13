# (C) British Crown Copyright 2019-2021, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`constants` module contains constants (values that should never
be changes by a user and exist for readability and maintainability
purposes) related to the ``data_request_interface`` sub-package.
"""
CMORVAR_ATTR_MAPPINGS = {
    'comment': 'description',
    'variable_name': 'label',
    'default_priority': 'defaultPriority',
    'frequency': 'frequency',
    'long_name': 'title',
    'mip_table': 'mipTable',
    'modeling_realm': 'modeling_realm',
    'positive': 'positive',
    'type': 'type',
    'vid': 'vid',
}
# The 'DATA_REQUEST_LINKAGES' dictionary connects the data request
# object types with the properties they have that links them to other
# data request objects. This is used to build the network of DreqNodes.
DATA_REQUEST_LINKAGES = {
    'experiment': ['egid', 'mip'],
    'exptgroup': [],
    'mip': [],
    'requestItem': ['esid', 'rlid', 'tslice'],
    'timeSlice': [],
    'requestLink': ['refid'],
    'requestVarGroup': [],
    'requestVar': ['vid', 'vgid'],
    'CMORvar': [],
}
# Metadata to record in 'retrieve_data_request_variables'.
# {data request property name: key to record information under}
EXPERIMENT_METADATA_TO_RECORD = {
    'description': 'experiment description',
    'endy': 'end year',
    'ensz': 'ensemble size',
    'mip': 'mip',
    'nstart': 'number of start dates',
    'starty': 'start year',
    'tier': 'tier',
    'title': 'experiment title',
    'uid': 'experiment_uid',
    'yps': 'years per start',
}
# The following items were found by searching through the attributes of
# the dreq module and picking out strings that contain the current
# version number. This may break if dreqPy changes structure.
FIELDS_TO_ALTER_PRIOR_TO_LOAD = {
    'DOC_DIR': 'dreqPy/docs',
    'blockSchemaFile': 'dreqPy/docs/BlockSchema.csv',
    'defaultDreqPath': 'dreqPy/docs/dreq.xml',
    'defaultConfigPath': 'dreqPy/docs/dreq2Defn.xml',
    'defaultManifestPath': 'dreqPy/docs/dreqManifest.txt',
    'PACKAGE_DIR': 'dreqPy',
}
# Remarks objects appear in various places, presumably as place holders.
# These must be ignored.
IGNORED_NODE_TYPES = ['remarks']
# Number used to indicate that a request relates to all ensemble members
# of an experiment.
MAX_ENSEMBLE_SIZE = 1000
STRUCTURE_ATTR_MAPPINGS = {
    'cell_measures': 'cell_measures',
    'cell_methods': 'cell_methods',
}
VARIABLE_ATTR_MAPPINGS = {
    'output_variable_name': 'label',
    'description': 'description',
    'standard_name': 'sn',
    'units': 'units',
}
# Routes for walking the data request.
WALK_ROUTE_MAIN = ['CMORvar', 'requestVar', 'requestVarGroup',
                   'requestLink', 'requestItem']
WALK_ROUTE_A = WALK_ROUTE_MAIN + ['mip', 'experiment']
WALK_ROUTE_B = WALK_ROUTE_MAIN + ['exptgroup', 'experiment']
WALK_ROUTE_C = WALK_ROUTE_MAIN + ['experiment']
