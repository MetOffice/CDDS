# (C) British Crown Copyright 2018-2021, Met Office.
# Please see LICENSE.rst for license details.
"""
This module contains the code to generate the
|model configuration information|.
"""
import atexit
import copy
from collections import defaultdict
from configparser import ConfigParser
import logging
import os
import shutil
import tempfile
from xml.etree import ElementTree

from cdds.common.io import read_json
from cdds.common.plugins.plugins import PluginStore

from cdds.common.rose_config import load as config_load

from cdds.common import check_svn_location, determine_rose_suite_url, run_command

from cdds.prepare.constants import (CICE_HISTFREQ_FOR_VALIDATION,
                                    CICE_VARIABLE_REMAP, MODEL_TYPE_MAP,
                                    OBGC_MODEL_STRING, OCEAN_STREAMS)


TMPDIRS = []
# The model types we know about


def retrieve_model_suite_variables(model_to_mip_mappings, mip_era, model_type,
                                   suite_id, branch, revision):
    """
    Return the |MIP requested variables| from the model suite.

    Parameters
    ----------
    model_to_mip_mappings : dict of :class:`VariableModelToMIPMapping`
        The |model to MIP mappings| for the |MIP requested variables|.
    mip_era: str
        The |MIP era|.
    model_type: str
        The |model type|.
    suite_id: str
        The |suite identifier|.
    branch: str
        The branch of the model suite, referred to by the
        |suite identifier|, to use.
    revision: int
        The revision of the model suite, referred to by the
        |suite identifier|, to use.

    Returns
    -------
    : dict
        The |MIP requested variables| from the model suite in the form
        ``{'enabled': ['mip_table1/var_name1', ...],
        'disabled': ['mip_table2/var_name2', ...]}``.
    """
    logger = logging.getLogger(__name__)
    model_suite_variables = {'enabled': [], 'disabled': []}
    all_variables = {}
    canonical_types = _canonical_model_types(model_type)

    if len(canonical_types) == 0:
        logger.critical(
            'No canonical model types for "{}", '
            'from model type "{}":\n'
            '  so no variables will be retrieved'.format(
                suite_id, model_type))

    if 'atmos' in canonical_types:
        logger.debug('Identifying atmosphere variables in suite')
        # Retrieve atmos 'MIP requested variables'.
        atmos_enabled = create_atmos_enabled(suite_id, branch, revision)
        atmos_variables = consolidate_atmos_enabled(atmos_enabled)
        all_variables.update(atmos_variables)

    if 'ocean' in canonical_types:
        logger.debug('Identifying ocean variables in suite')
        # Retrieve ocean 'MIP requested variables'.
        ocean_variables = create_ocean_enabled(
            model_to_mip_mappings, mip_era, suite_id, branch, revision,
            model_type)
        all_variables.update(ocean_variables)

    # Determine the state of each 'MIP requested variable' in the suite.
    logger.debug('Determining state of each MIP requested variable')
    for mip_requested_variable, var_info in sorted(all_variables.items()):
        key = 'disabled'
        if len(var_info['enabled']) == 1 and True in var_info['enabled']:
            key = 'enabled'
        model_suite_variables[key].append(mip_requested_variable)

    return model_suite_variables


def _canonical_model_types(model_type):
    """
    Given a |model type| return a set of canonical types.

    A canonical type is one of the strings ``'atmos'`` or
    ``'ocean'``, which tells us what variables to try to retrieve.

    Parameters
    ----------
    model_type: str
        The |model type| of the model, which should be a
        whitespace-separated list of CMIP6-standard tokens.

    Returns
    -------
    : set
        A set of canonical model types.

    Examples
    --------
    >>> sorted(_canonical_model_types('AOGCM'))
    ['atmos', 'ocean']

    >>> _canonical_model_types('AGCM')
    {'atmos'}

    >>> _canonical_model_types('NONSENSE')
    set()

    >>> _canonical_model_types('AGCM,')
    set()
    """
    canonical_types = set()
    for model_type_token in model_type.split():
        for (canonical_type, tokens) in MODEL_TYPE_MAP.items():
            for token in tokens:
                if model_type_token == token:
                    canonical_types.add(canonical_type)
                    break       # no point in looking at any more
    return canonical_types


def create_atmos_enabled(suite_id, branch, revision):
    """
    Return the |STASH| that are enabled in the atmosphere |model|.

    Parameters
    ----------
    suite_id: str
        The |suite identifier|.
    branch: str
        The branch of the model suite, referred to by the
        |suite identifier|, to use.
    revision: int
        The revision of the model suite, referred to by the
        |suite identifier|, to use.

    Returns
    -------
    : dict
        The |STASH| that are enabled in the atmosphere |model|.
    """
    return _elaborate_atmos_dictionary(
        [_get_input(suite_id, branch, revision, 'rose-app.conf')],
        [_get_input(suite_id, branch, revision, 'atmos_dictionary.json')])


def _get_input(suite_id, branch, revision, filename):
    path = os.path.join('app', 'um', filename)
    directory = export_file_from_suite(suite_id, branch, path, revision)
    return os.path.join(directory, filename)


def consolidate_atmos_enabled(atmos_enabled):
    """
    Return the |MIP requested variables| that are enabled in the
    atmosphere |model|.

    Parameters
    ----------
    atmos_enabled: dict
        The |STASH| that are enabled in the atmosphere |model|.

    Returns
    -------
    : dict
        The |MIP requested variables| that are enabled in the
        atmosphere |model|.
    """
    consolidated = defaultdict(lambda: defaultdict(list))
    for var_info in list(atmos_enabled.values()):
        mip_table = var_info['sheet_name']
        var_name = var_info['cmor']
        mip_requested_variable = '{}/{}'.format(mip_table, var_name)
        for key, value in var_info.items():
            if value not in consolidated[mip_requested_variable][key]:
                consolidated[mip_requested_variable][key].append(value)
    return consolidated


def create_ocean_enabled(model_to_mip_mappings, mip_era, suite_id, branch,
                         revision, model_type):
    """
    Return the |MIP requested variables| that are enabled in the ocean
    |model|.

    Parameters
    ----------
    model_to_mip_mappings : dict of :class:`VariableModelToMIPMapping`
        The |model to MIP mappings| for the |MIP requested variables|.
    mip_era : str
        The |MIP era|.
    suite_id: str
        The |suite identifier|.
    branch: str
        The branch of the model suite, referred to by the
        |suite identifier|, to use.
    revision: int
        The revision of the model suite, referred to by the
        |suite identifier|, to use.
    model_type: str
        A string which identifies the components of the model being processed.

    Returns
    -------
    : dict
        The |MIP requested variables| that are enabled in the ocean
        |model|.
    """
    logger = logging.getLogger(__name__)
    raw_ocean_enabled = {}
    logger.debug('Reading NEMO config files')
    obgc_in_model = OBGC_MODEL_STRING in model_type
    raw_nemo_enabled = _nemo_and_medusa_enabled(suite_id, branch, revision,
                                                obgc_in_model)
    raw_ocean_enabled.update(raw_nemo_enabled)
    logger.debug('Reading CICE config files')
    raw_cice_enabled = _cice_enabled(suite_id, branch, revision)
    raw_ocean_enabled.update(raw_cice_enabled)

    logger.debug('Constructing ocean enabled information')
    ocean_enabled = {}
    stream_info = PluginStore.instance().get_plugin().stream_info()
    # It won't be possible to determine whether a
    # 'MIP requested variable' exists in the model unless it has a
    # 'model to MIP mapping', so looping over the
    # 'MIP requested variables' in the 'model to MIP mappings' first:
    for mip_table_id, info in model_to_mip_mappings.items():
        for variable_name, model_to_mip_mapping in info.items():
            variable_key = '{}/{}'.format(mip_table_id, variable_name)
            # Retrieve the 'stream identifier' for the
            # 'MIP requested variable'.
            stream_id, _ = stream_info.retrieve_stream_id(variable_name, mip_table_id)
            if stream_id not in OCEAN_STREAMS:
                # No need to record if not ocean.
                continue
            if isinstance(model_to_mip_mapping, Exception):
                ocean_enabled[variable_key] = {'enabled': [False]}
                continue
            # Confirm all 'input variables' in the 'model to MIP mapping'
            # are enabled in the mode.
            all_input_variables_enabled = True
            for input_variable in model_to_mip_mapping.loadables:
                # Ignore any constraints.
                for token in input_variable.tokens:
                    # 'token' is a tuple containing the names,
                    # comparators and values for a single
                    # 'input variable', e.g.
                    # ('variable_name', '=', 'tos').
                    if 'variable_name' in token:
                        variable_name = token[-1]
                enabled_key = '{}/{}'.format(stream_id, variable_name)
                if enabled_key in raw_ocean_enabled:
                    if not raw_ocean_enabled[enabled_key]['enabled']:
                        all_input_variables_enabled = False
                else:
                    all_input_variables_enabled = False

            ocean_enabled[variable_key] = {
                'enabled': [all_input_variables_enabled]}
    return ocean_enabled


def _get_iodef_filename_in_suite(suite_id, branch, revision):
    rose_app_conf_fname = 'rose-app.conf'
    rose_app_conf_path = os.path.join('app', 'nemo_cice', rose_app_conf_fname)
    temp_dir = export_file_from_suite(suite_id, branch, rose_app_conf_path,
                                      revision)
    local_conf_path = os.path.join(temp_dir, rose_app_conf_fname)
    # the default which will be used unless something is found in rose-app.conf
    iodef_filename = 'iodef.xml'

    with open(local_conf_path) as rose_conf_file:
        rose_conf_txt = rose_conf_file.readlines()
    # We need to skip the first two due to the non-standard nature of the
    # ini file formatting for rose-app.conf files.
    rose_conf_txt = str(''.join(rose_conf_txt[2:]))
    parser = ConfigParser()
    parser.read_string(rose_conf_txt)
    iodef_key = 'file:iodef.xml'
    if iodef_key in parser.sections():
        iodef_filename = dict(parser.items(iodef_key))['source']
    return iodef_filename


def _nemo_and_medusa_enabled(suite_id, branch, revision, obgc_in_model):
    logger = logging.getLogger()
    filename_iodef = _get_iodef_filename_in_suite(suite_id, branch, revision)

    path = os.path.join('app', 'nemo_cice', 'file', filename_iodef)
    logger.info(
        'retrieving file {fname} from suite {id}/{branch}@{rev}'.format(
            fname=filename_iodef,
            id=suite_id,
            branch=branch,
            rev=revision))
    directory = export_file_from_suite(suite_id, branch, path, revision)
    path_iodef = os.path.join(directory, filename_iodef)
    logger.info('reading iodef file from {0}'.format(path_iodef))
    iodef_cfg, groups_present = _read_iodef_into_dict(path_iodef, 2)

    if groups_present:
        if obgc_in_model:
            filename_field_def = 'field_def_bgc.xml'
            path_fd_suite = os.path.join('app', 'nemo_cice', 'file',
                                         filename_field_def)
            fd_dir = export_file_from_suite(suite_id, branch, path_fd_suite,
                                            revision)
            path_field_def = os.path.join(fd_dir, filename_field_def)
            field_cfg = _read_field_def_xml_into_dict(path_field_def, 0)
            _expand_field_groups(iodef_cfg, field_cfg)

    nemo_enabled = _construct_enabled_var_from_iodef(iodef_cfg)
    return nemo_enabled


def export_file_from_suite(suite_id, branch, filename, revision):
    """
    Return the full path to the directory where the file exported from
    the Rose suite will be written.

    Parameters
    ----------
    suite_id: str
        The |suite identifier|.
    branch: str
        The branch of the model suite, referred to by the
        |suite identifier|, to use.
    filename: str
        The path in the branch where the file to be exported resides.
    revision: int
        The revision of the model suite, referred to by the
        |suite identifier|, to use.

    Returns
    -------
    : str
        The full path to the directory where the file exported from the
        Rose suite will be written.
    """
    path = tempfile.mkdtemp()
    TMPDIRS.append(path)
    root_url = determine_rose_suite_url(suite_id)
    if not check_svn_location(root_url):
        root_url = determine_rose_suite_url(suite_id, internal=False)
    url_template = '{}/{}/{}@{}'
    url = url_template.format(root_url, branch, filename, revision)
    command = ['svn', 'export', '--force', url, path]
    run_command(command)
    return path


def _construct_enabled_var_from_iodef(config):
    logger = logging.getLogger()
    vars_enabled = defaultdict(dict)
    for fg_id, file_group in config.items():
        enabled = file_group['enabled'] == '.TRUE.'
        stream_id = _retrieve_nemo_stream_id(file_group['id'])
        # `stream_id` is only checked once variables in the corresponding
        # `file_group` are identified. Otherwise there will be warnings about
        # frequencies where NEMO is not generating any variables , e.g. `2h`
        # in HadGEM3/UKESM1.
        for file_id, file_group_file in file_group['files'].items():
            for field_id, field in file_group_file['fields'].items():
                variable_name = field['name']
                if stream_id is None:
                    logger.warning(
                        'Variable "{}": File group "{}" not linked to '
                        'corresponding output stream'
                        ''.format(variable_name, fg_id))
                model_variable = '{}/{}'.format(stream_id, variable_name)
                vars_enabled[model_variable]['enabled'] = enabled
    return vars_enabled


def _read_iodef_into_dict(iodef_path, lines_to_skip):
    with open(iodef_path) as file_handle:
        config = file_handle.readlines()

    # The first two lines of the 'iodef.xml' file invalidate the XML.
    nemo_et = ElementTree.fromstring(''.join(config[lines_to_skip:]))
    cfg_dict = {}
    groups_present = False
    for file_group in nemo_et.iter('file_group'):
        file_group_dict = file_group.attrib
        file_group_dict['files'] = {}
        for file_group_file in file_group.iter('file'):
            file_dict = file_group_file.attrib
            file_dict['fields'] = {}
            file_dict['field_groups'] = {}
            for field in file_group_file.iter('field'):
                if 'name' in field.attrib:
                    file_dict['fields'][field.attrib['name']] = field.attrib
            for field_group in file_group_file.iter('field_group'):
                try:
                    if field_group.attrib['enabled'] == '.TRUE.':
                        fg_dict = copy.copy(field_group.attrib)
                        fg_dict['enabled'] = True
                        name = fg_dict['group_ref']
                        file_dict['field_groups'][name] = fg_dict
                        groups_present = True
                except KeyError:
                    # if field group does not have expected attributes, skip
                    pass
            file_group_dict['files'][file_dict['id']] = file_dict
        cfg_dict[file_group_dict['id']] = file_group_dict
    return cfg_dict, groups_present


def _read_field_def_xml_into_dict(field_def_path, lines_to_skip):
    with open(field_def_path) as file_handle:
        config = file_handle.readlines()
    nemo_et = ElementTree.fromstring(''.join(config[lines_to_skip:]))
    cfg_dict = {}

    # should be only 1 field_definition element in the xml file
    field_def = [fd for fd in nemo_et.iter('field_definition')][0]
    for field_group in field_def.iter('field_group'):
        fg_dict = field_group.attrib
        fg_dict['fields'] = {}
        id_fg = fg_dict['id']
        for field in field_group.iter('field'):
            try:
                field_dict = copy.copy(field.attrib)
                if 'id' in field_dict:
                    id_field = field_dict['id']
                    # the fields in the field_def.xml file have different
                    # attributes from the fields in the iodef.xml. We are
                    # only interested in the name of the fields, so a name is
                    # added to the dictionary from the field def so it can be
                    # used togther with fields from the iodef file to
                    # determine what fields are turned on in the model, and
                    # therefore which mip variables can be produced
                    field_dict['name'] = id_field
                elif 'field_ref' in field_dict:
                    id_field = field_dict['field_ref']
                fg_dict['fields'][id_field] = field_dict
            except KeyError as ke1:
                pass
        cfg_dict[id_fg] = fg_dict
    return cfg_dict


def _expand_field_groups(iodef_dict, field_def_dict):
    for fg_id, file_group in iodef_dict.items():
        enabled = file_group['enabled'] == '.TRUE.'
        stream_id = _retrieve_nemo_stream_id(file_group['id'])
        # `stream_id` is only checked once variables in the corresponding
        # `file_group` are identified. Otherwise there will be warnings about
        # frequencies where NEMO is not generating any variables , e.g. `2h`
        # in HadGEM3/UKESM1.
        for file_id, file_group_file in file_group['files'].items():
            for (group_ref,
                 field_group) in file_group_file['field_groups'].items():
                if field_group['enabled']:
                    fields_in_gropup = field_def_dict[group_ref]['fields']
                    file_group_file['fields'].update(fields_in_gropup)
    return iodef_dict


def _cice_enabled(suite_id, branch, revision):
    cice_enabled = defaultdict(dict)
    filename = 'rose-app.conf'
    path = os.path.join('app', 'nemo_cice', filename)
    directory = export_file_from_suite(suite_id, branch, path, revision)
    config_node = config_load(os.path.join(directory, filename))
    stream_ids = _check_cice_frequency_info(config_node)
    cice_variables = _get_cice_variables(config_node, stream_ids)
    for cice_variable in cice_variables:
        cice_enabled[cice_variable]['enabled'] = True
    return cice_enabled


def _get_cice_variables(config_node, stream_ids):
    """
    Examples
    --------
    >>> from cdds.common.rose_config import ConfigNode
    >>> config_node = ConfigNode()
    >>> _ = config_node.set(
    ...     keys=["namelist:icefields_mechred_nml", "f_ardgn"],
    ...     value="'x'")
    >>> _ = config_node.set(
    ...     keys=["namelist:icefields_nml", "f_congel"],
    ...     value="'d'")
    >>> # icepresent is output as variable ice_present.
    >>> _ = config_node.set(
    ...     keys=["namelist:icefields_nml", "f_icepresent"],
    ...     value="'d'")
    >>> _ = config_node.set(
    ...     keys=["namelist:icefields_pond_nml", "f_hpond"],
    ...     value="'dh'")

    >>> stream_ids = {'d': 'inm', 'h': 'ind'}
    >>> print(_get_cice_variables(config_node, stream_ids))
    ['ind/hpond', 'inm/congel', 'inm/hpond', 'inm/ice_present']

    >>> stream_ids = {'h': 'ind'}
    >>> print(_get_cice_variables(config_node, stream_ids))
    ['ind/hpond']
    """
    cice_variables = []
    namelists = ['namelist:icefields_mechred_nml', 'namelist:icefields_nml',
                 'namelist:icefields_pond_nml']
    for (keys, sub_node) in config_node.walk():
        if len(keys) == 1 and keys[0] in namelists:
            for option in sub_node:
                variable_name = option[2:]  # Remove 'f_'
                if variable_name in CICE_VARIABLE_REMAP:
                    variable_name = CICE_VARIABLE_REMAP[variable_name]
                frequencies = sub_node[option].value.strip('\'"')
                if frequencies in ['x', '.false.']:
                    # If no frequency is defined, the 'MIP table' can't be
                    # determined, so no 'MIP requested variable' can be added.
                    continue
                if '.true.' in frequencies:
                    frequencies = ''.join(list(stream_ids.keys()))
                for frequency in frequencies:
                    if frequency in stream_ids:
                        stream_id = stream_ids[frequency]
                        cice_variables.append(
                            '{}/{}'.format(stream_id, variable_name))
    return sorted(cice_variables)


def _check_cice_frequency_info(config_node):
    """
    Examples
    --------
    >>> from cdds.common.rose_config import ConfigNode
    >>> # Frequency values as expected.
    >>> config_node = ConfigNode()
    >>> _ = config_node.set(keys=["namelist:setup_nml", "histfreq"],
    ...     value="'d','h','x','x','x'")
    >>> _ = config_node.set(keys=["namelist:setup_nml", "histfreq_n"],
    ...     value="10,24,1,1,1")
    >>> output = _check_cice_frequency_info(config_node)
    >>> for key, value in sorted(output.items()):
    ...     print(key, value)
    d inm
    h ind

    >>> # Frequency values not as expected.
    >>> another_config_node = ConfigNode()
    >>> _ = another_config_node.set(
    ...     keys=["namelist:setup_nml", "histfreq"],
    ...     value="'d','h','x','x','x'")
    >>> _= another_config_node.set(
    ...     keys=["namelist:setup_nml", "histfreq_n"],
    ...     value="1,24,1,1,1")
    >>> output = _check_cice_frequency_info(another_config_node)
    >>> for key, value in sorted(output.items()):
    ...     print(key, value)
    h ind
    """
    # Retrieve the logger.
    logger = logging.getLogger(__name__)

    cice_stream_ids = {
        freq: stream_id
        for stream_id, freq in OCEAN_STREAMS.items()
        if stream_id.startswith('in')}
    expected_values = CICE_HISTFREQ_FOR_VALIDATION
    frequency_ids = [
        item.strip('\'"') for item in config_node.get_value(
            keys=['namelist:setup_nml', 'histfreq']).split(',')]
    frequency_values = [
        int(item) for item in config_node.get_value(
            keys=['namelist:setup_nml', 'histfreq_n']).split(',')]
    frequency_info = dict(list(zip(frequency_ids, frequency_values)))
    for frequency_id, frequency_value in expected_values.items():
        if frequency_info[frequency_id] != frequency_value:
            stream_id = cice_stream_ids[frequency_id]
            del cice_stream_ids[frequency_id]
            logger.critical(
                'Frequency value for "{}" ({}) not as expected ({}); MIP '
                'requested variables for stream "{}" will not be enabled'
                ''.format(
                    frequency_id, frequency_info[frequency_id],
                    frequency_value, stream_id))
    return cice_stream_ids


def _retrieve_nemo_stream_id(frequency):
    """
    Examples
    --------
    >>> _retrieve_nemo_stream_id('1d')
    'ond'
    >>> _retrieve_nemo_stream_id('1m')
    'onm'
    >>> # 3h/6h stream not in OCEAN_STREAMS dictionary, so return None.
    >>> _retrieve_nemo_stream_id('3h') is None
    True
    >>> _retrieve_nemo_stream_id('6h') is None
    True
    """
    stream_id = None
    defaults = {
        freq: stream for stream, freq in OCEAN_STREAMS.items()
        if stream.startswith('on')}
    if frequency in defaults:
        stream_id = defaults[frequency]
    return stream_id


def _elaborate_atmos_dictionary(cfs, ads):
    # given some config files and some atmos dictionary files, build
    # an elaborated atmos dictionary which contains the 'present' and
    # 'enabled' entries derived from the config files.
    cemap = None
    for cf in cfs:
        cemap = _config_enabled_map(cf, extending=cemap)
    result = {}
    for ad in ads:
        for (k, e) in read_json(ad).items():
            ce = _hashable(_canonicalise_ad_entry(e))
            if ce in cemap:
                e['present'] = True
                e['enabled'] = cemap[ce]
            else:
                e['present'] = False
                e['enabled'] = None
            result[k] = e
    return result


def _config_stash_requests(config):
    # Extract the stash requests in config and return them as a dict
    # of dicts, keyed by their ids.  There is an extra key in each
    # request which tells you whether it is enabled or not.  This is
    # just extracting things from the ConfigNode objects that the rose
    # API defines.  It is slightly casual about checking whether
    # things are enabled other than at top-level, but I don't think
    # that matters for stash requests.
    stash_requests = {}
    for (keys, sub_nodes) in config.walk():
        if len(keys) == 1 and keys[0].startswith('namelist:umstash_streq'):
            # a top level stash request
            stash_request = {key: sub_nodes[key].value for key in sub_nodes}
            stash_request['enabled'] = (
                True if sub_nodes.state == sub_nodes.STATE_NORMAL else False)
            stash_requests[keys[0]] = stash_request
    return stash_requests


def _canonicalise_ad_entry(entry):
    # take a stash request entry from atmos dictionary and turn it
    # into a canonical version of itself, with just the bits needed
    # for matching.
    return {'isec': int(entry['section']),
            'item': int(entry['item']),
            'dom_name': entry['dom_name'],
            'tim_name': entry['tim_name'],
            'use_name': entry['use_name'],
            'package': entry['package']}


def _canonicalise_cf_entry(entry):
    # Take a stash request entry derived from a config file and
    # canonicalise it for comparison, with just the bits needed for
    # matching.
    return {'isec': int(entry['isec'].strip("'")),
            'item': int(entry['item'].strip("'")),
            'dom_name': entry['dom_name'].strip("'"),
            'tim_name': entry['tim_name'].strip("'"),
            'use_name': entry['use_name'].strip("'"),
            'package': entry['package'].strip("'")}


def _hashable(o):
    # A hashable version of o (assuming o never changes) This is
    # probably incomplete, but it will do.  Note that, for instance,
    # hashable((("a", 1), ("b", 2))) and hashable({"a": 1, "b": 2})
    # are equal: this is OK on the assumption that all the data
    # structures you're trying to use as hash keys have the same type
    # (where 'type' here means 'entire type').
    if isinstance(o, dict):
        return tuple(sorted((k, _hashable(v)) for (k, v) in o.items()))
    elif isinstance(o, (set, list, tuple)):
        return tuple(_hashable(v) for v in o)
    else:
        assert hasattr(o, '__hash__'), 'unexpectedly unhashable'
        return o


def _config_enabled_map(filename, extending=None):
    # Read a rose-app.conf and return a dict mapping hashable
    # canonicalised entries to a boolean saying whether they were
    # enabled or not.  If extending is given this can extend an
    # existing mapping.  Note this includes disabled entries
    mapping = {} if extending is None else extending
    for value in list(_config_stash_requests(config_load(filename)).values()):
        mapping[_hashable(_canonicalise_cf_entry(value))] = value['enabled']
    return mapping


@atexit.register
def _clean():
    if TMPDIRS:
        for directory_to_delete in TMPDIRS:
            if os.path.isdir(directory_to_delete):
                shutil.rmtree(directory_to_delete)
