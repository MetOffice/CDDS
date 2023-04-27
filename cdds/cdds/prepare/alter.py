# (C) British Crown Copyright 2017-2021, Met Office.
# Please see LICENSE.rst for license details.
"""
This module contains the code required to alter
|requested variables lists|.
"""
from collections import defaultdict
import configparser
from datetime import datetime
import json
import logging

from cdds.common.io import read_json, write_json
from cdds.common.plugins.exceptions import PluginLoadError
from cdds.common.plugins.plugins import PluginStore
from cdds.common.plugins.plugin_loader import load_plugin
from cdds.common import set_checksum

from cdds import __version__
from cdds.prepare.common import retrieve_mappings
from cdds.prepare.constants import ACTIVATE, DEACTIVATE, INSERT

from mip_convert.request import get_mip_table

ALTER_INSERT_UNKNOWN_FIELD = 'unknown'
SUBSET_HISTORY_COMMENT = ('User selected a subset of variables for test '
                          'purposes.')


def alter_variable_list(parameters):
    """
    Alter the |requested variables list|.

    Parameters
    ----------
    parameters: :class:`argparse.Namespace` object
        The names of the command line arguments and their validated
        values.
    """
    # Retrieve the logger.
    logger = logging.getLogger(__name__)
    logger.info('*** Starting ***')
    logger.debug('CDDS Prepare version "{}"'.format(__version__))

    # Load and validate the 'requested variables list'.
    requested_variables = read_json(parameters.rvfile)

    # Load plugin if needed
    if parameters.change_type == INSERT:
        # TODO: redesign to allow for external plugins
        try:
            load_plugin(requested_variables['mip_era'])
        except PluginLoadError:
            logger.critical('Could not load plugin for mip era "{}"'
                            ''.format(requested_variables['mip_era']))
            logger.info('This operation cannot be performed for projects with external plugins')
            raise
    # Construct the list of rules used to determine whether to change
    # the status of the 'MIP requested variable'.
    change_rules = _construct_change_rules(
        parameters.vars, parameters.change_type, parameters.default_priority)
    logger.debug('Change rules: \n{}'.format(json.dumps(change_rules)))
    now = _get_now_iso_string()
    history_comment = {
        'time': now, 'type': parameters.change_type,
        'comment': parameters.comment,
        'override': parameters.override}

    if 'history' not in requested_variables:
        requested_variables['history'] = []

    if parameters.change_type in [ACTIVATE, DEACTIVATE]:
        variables_affected, requested_variables = _apply_activate_deactivate(
            requested_variables, parameters.change_type, change_rules,
            parameters.comment, now, override=parameters.override)
    else:  # parameters.change_type == INSERT
        variables_affected = _apply_insert(
            requested_variables,
            change_rules,
            now,
            parameters.default_priority,
            parameters.mip_table_dir
        )

    # Ensure the appropriate metadata will be written to the
    # 'requested variables list'.
    history_comment['variables_affected'] = variables_affected
    requested_variables['history'].append(history_comment)
    set_checksum(requested_variables)

    # Write the 'requested variables list'.
    logger.debug('Writing the requested variables list to "{}"'
                 ''.format(parameters.rvfile))
    write_json(parameters.rvfile, requested_variables)
    logger.info('*** Alter command complete ***')


def select_variables(rv_file, variables):
    """
    Deactivate all |MIP requested variables| in the |requested variables list|
    specified by ``rv_file`` except those listed in ``variables``.

    Parameters
    ----------
    rv_file: str
        The path to the |requested variables list|.

    variables: list
        A list of strings, each string representing a |MIP requested variable|
        to remain active in the form ``<mip_table_id>/<variable_name>``.
    """
    logger = logging.getLogger(__name__)
    logger.info('*** Starting ***')
    logger.debug('CDDS Prepare version "{}"'.format(__version__))

    logger.info('Selecting variables to process from Requested Variables file'
                '{rv_file}'.format(rv_file=rv_file))
    logger.info('The following variables will be left in their current state,'
                'with all other variables turned off:\n {vars}'
                ''.format(vars=variables))

    # Load and validate the 'requested variables list'.
    requested_variables = read_json(rv_file)

    vars_to_deactivate = []

    for var_dict in requested_variables['requested_variables']:
        var_name = '{mip_table_id}/{var}'.format(
            mip_table_id=var_dict['miptable'],
            var=var_dict['label'])
        if var_dict['active'] and var_name not in variables:
            vars_to_deactivate += [var_name]

    # Construct the list of rules used to determine whether to change
    # the status of the 'MIP requested variable'.
    change_rules = _construct_change_rules(
        vars_to_deactivate, DEACTIVATE, 1)
    logger.debug('Change rules: \n{}'.format(json.dumps(change_rules)))

    now = _get_now_iso_string()
    history_comment = {
        'time': now,
        'type': DEACTIVATE,
        'comment': SUBSET_HISTORY_COMMENT,
        'override': False}

    if 'history' not in requested_variables:
        requested_variables['history'] = []

    variables_affected, requested_variables = _apply_activate_deactivate(
        requested_variables, DEACTIVATE, change_rules, SUBSET_HISTORY_COMMENT,
        now, override=False)

    history_comment['variables_affected'] = variables_affected
    requested_variables['history'].append(history_comment)
    set_checksum(requested_variables)

    # Write the 'requested variables list'.
    logger.debug('Writing the requested variables list to "{}"'
                 ''.format(rv_file))
    write_json(rv_file, requested_variables)
    logger.info('*** Complete ***')


def _get_now_iso_string():
    return datetime.now().isoformat()


def _construct_change_rules(variables, change_type, default_priority):
    """
    Construct the list of change rules for main_alter_variable_list

    Parameters
    ----------
    variables : list
        Variables to change from command line args
    change_type : str
        Change type (one of ACTIVATE, DEACTIVATE, INSERT)
    default_priority : int
        Priority to assign when inserting a variable

    Returns
    -------
    : list
        Dictionaries representing changes to be made to the requested
        variables file.
    """
    change_rules = []
    for entry in variables:
        if ';' in entry:
            entry, _ = entry.split(';')
        miptable, cmor = entry.split('/')
        change_rule = {'label': cmor, 'miptable': miptable}
        if change_type == INSERT:
            change_rule['priority'] = default_priority
        change_rules.append(change_rule)
    return change_rules


def _check_rules(change_rules, entry):
    """
    Identify whether this entry (in the request-variables section of
    a |requested variables list|) should be changed based on the change
    rules.

    Parameters
    ----------
    change_rules : list
        List of dictionaries describing the changes to be made.
    entry : dict
        Candidate entry for changing

    Returns
    -------
    : bool
        Should this entry be changed
    : int or None
        index within the change_rules list indicating the change to be
        made
    """
    change_entry = False
    change_rule_number = None
    # Go through the change rules one by one
    for i, change_rule in enumerate(change_rules):
        rule_change = True
        for key, value in change_rule.items():
            if entry[key] != value:
                # If any field doesn't match then there is no change
                # to make
                rule_change = False
                continue
        # If a rule that changes this entry has been identified break
        # and return
        if rule_change:
            change_rule_number = i
            change_entry = True
            break
    return change_entry, change_rule_number


def _apply_activate_deactivate(requested_variables, change_type, change_rules,
                               user_comment, timestamp, override=False):
    """
    Apply change type to entries in the requested_variables structure
    as identified by the change_rules. Note that the
    requested_variables structure is altered in place.

    Parameters
    ----------
    requested_variables: dict
        Data structure describing the |requested variables list| for
        this experiment.
    change_type : str
        Either ACTIVATE or DEACTIVATE.
    change_rules : list
        Rules describing which variables are to be changed.
    user_comment: str
        Comment provided by the user on the command line.
    timestamp : str
        Timestamp for this operation. Included in the comments.
    override : bool
        If true ignore in_model and in_mapping information when
        activating variables. If false and an attempt is made to
        ACTIVATE an inactive variable then a RuntimeError is raised.

    Returns
    -------
    : defaultdict(list)
        structure describing the variables in each mip table that have
        been altered by this operation
    : dict
        The altered requested variables dictionary

    Raises
    ------
    RuntimeError
        If an attempt is made to activate a variable that
        is not in the mappings or model **without** setting override to
        True.

    """
    # Retrieve the logger.
    logger = logging.getLogger(__name__)
    variables_affected = defaultdict(list)
    additional_comment = '{type}d {timestamp} - {comment}'.format(
        type=change_type, timestamp=timestamp, comment=user_comment)
    status = change_type == ACTIVATE
    for entry in requested_variables['requested_variables']:
        # Identify whether this variable is to be changed and if so which
        # change rule to apply.
        change_entry, change_rule_number = _check_rules(change_rules, entry)
        if not change_entry:
            # If no work for this variable skip on to the next
            continue
        if ((change_type == ACTIVATE and entry['active']) or
                (change_type == DEACTIVATE and not entry['active'])):
            # If attempting to change active status to the current value
            # raise an error
            current_status = '{}active'.format(
                'in' if not entry['active'] else '')
            msg = ('requested_variables targeted by rule {} already {}:'
                   '({}/{})').format(change_rule_number,
                                     current_status,
                                     entry['miptable'],
                                     entry['label'])
            logger.info(msg)
        elif (change_type == ACTIVATE and not
              (entry['in_mappings'] and entry['in_model'])
              and not override):
            # if attempting to activate an unavailable variable without
            # override raise an error
            msg = ('Cannot activate variable: "{miptable}/{label}" '
                   'in_mappings = "{in_mappings}", '
                   'in_model = "{in_model}"').format(**entry)
            raise RuntimeError(msg)
        elif (change_type == ACTIVATE and not
              (entry['in_mappings'] and entry['in_model'])
              and override):
            # If activating and availability is to be overridden comment to
            # that effect.
            entry['comments'].append(
                'in_model and in_mappings overridden when activating. {}'
                ''.format(timestamp))

        # make the change and record variable affected
        variables_affected[entry['miptable']].append(entry['label'])
        entry['active'] = status
        entry['comments'].append(additional_comment)

    return variables_affected, requested_variables


def _apply_insert(requested_variables, change_rules, timestamp, priority,
                  mip_table_dir):
    """
    Insert the variables required, checking first that they do not
    already exist.

    Parameters
    ----------
    requested_variables : dict
        Data structure describing the |requested variables list| for
        this experiment.
    change_rules : list
        Rules describing which variables are to be inserted.
    timestamp : str
        Timestamp for this operation. Included in the comments.
    priority : int
        Priority to insert variables with
    mip_table_dir : str
        Location of the MIP tables

    Returns
    -------
    : defaultdict(list)
        Dictionary describing the variables inserted.
    """
    logger = logging.getLogger(__name__)

    stream_info = PluginStore.instance().get_plugin().stream_info()
    # Dictionary to describe the changes made by this operation.
    variables_affected = defaultdict(list)
    # Identify variables already in the 'requested variables list'.
    variables_present = [
        '{miptable}/{label}'.format(**entry)
        for entry in requested_variables['requested_variables']]
    change_errors = []
    for rule in change_rules:
        variable = '{miptable}/{label}'.format(**rule)
        if variable in variables_present:
            # If variable is already present record this.
            change_errors.append(variable)
    if change_errors:
        # If any change errors list them in the error message.
        msg = ('Cannot insert variables that are already present: "{}"'
               '').format(', '.join(change_errors))
        raise RuntimeError(msg)

    # Construct a dictionary that looks like the one produced by
    # get_data_request_variables, but without querying the data request.
    dummy_data_request_variables = defaultdict(dict)
    for rule in change_rules:
        dummy_data_request_variables[rule['miptable']][rule['label']] = None

    # Retreive the mappings based on the dummy dictionary
    mip_era = requested_variables['mip_era']
    logger.debug('Retrieving mappings for "{}"'.format(mip_era))
    mappings = retrieve_mappings(dummy_data_request_variables,
                                 mip_era, requested_variables['model_id'])
    # Load the MIP tables
    mip_tables = {}
    for mip_table in mappings:
        mip_table_json = '{}_{}.json'.format(mip_era, mip_table)
        logger.debug('Loading mip table "{}" from directory "{}"'.format(
            mip_table_json, mip_table_dir))
        mip_tables[mip_table] = get_mip_table(mip_table_dir, mip_table_json)

    # If everything is ok, insert the variables.
    for rule in change_rules:
        # Base entry for requested variables list on rule
        entry = rule
        # Pick out mapping for this variable
        mapping = mappings[rule['miptable']][rule['label']]
        # Pick out MIP table data for this variable
        if rule['label'] not in mip_tables[rule['miptable']].variables:
            msg = ('Could not find variable "{label}" in mip table '
                   '"{miptable}" when reading mip tables from '
                   '"{mip_table_dir}"'.format(
                       mip_table_dir=mip_table_dir, **rule))
            logger.critical(msg)
            raise RuntimeError(msg)
        mip_table_data = mip_tables[rule['miptable']].variables[rule['label']]
        # Is the mapping ok? If not deactivate and critical log.
        mapping_error = False
        if isinstance(mapping, configparser.Error):
            msg = ('Error retrieving mapping for "{miptable}/{label}: '
                   '"{msg}"'.format(msg=mapping, **rule))
            logger.critical(msg)
            raise RuntimeError(msg)
        else:
            if mapping.status != 'ok':
                mapping_error = True
                logger.critical(
                    'Attempting to insert variable "{}/{}" with status="{}". '
                    'Mapping will be inserted as inactive and will require '
                    'manual activation.'.format(
                        rule['miptable'], rule['label'], mapping.status))
        # Populate entry with data where possible
        stream_id, substream = stream_info.retrieve_stream_id(rule['label'], rule['miptable'])
        entry['active'] = mapping.status == 'ok'
        entry['cell_methods'] = mip_table_data['cell_methods']
        entry['comments'] = ['Inserted {}'.format(timestamp)]
        entry['dimensions'] = mip_table_data['dimensions']
        entry['frequency'] = mip_table_data['frequency']
        entry['in_mappings'] = not mapping_error
        entry['in_model'] = ALTER_INSERT_UNKNOWN_FIELD
        entry['priority'] = priority
        entry['stream'] = '{}/{}'.format(stream_id, substream) if substream is not None else stream_id
        # Add to requested variables list
        requested_variables['requested_variables'].append(entry)
        variables_affected[entry['miptable']].append(entry['label'])

    return variables_affected
