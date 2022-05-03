# (C) British Crown Copyright 2021, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`auto_deactivation` module contains code to automatically
deactivate variables with known issues.
"""
from argparse import Namespace
import json
import logging
import re

from .alter import alter_variable_list
from .constants import DEACTIVATION_RULE_LOCATION

from cdds_common.common.io import read_json
from hadsdk.common import run_command, check_svn_location


def deactivation_commands(model_id, experiment_id, rule_file=None):
    """
    Return the rules dictionary for the specified model and experiment_id

    Parameters
    ----------
    model_id : str
        Model ID, e.g. "HadGEM3-GC31-LL
    experiment_id : str
        Experiment ID, e.g. "amip"
    rule_file: str, optional
        File to load rules from if required. If unspecified retrieve from

    Returns
    -------
    : list
        Deactivation commands

    Raises
    ------
    RuntimeError
        If rules for specified model id cannot be found
    """
    logger = logging.getLogger(__name__)

    if rule_file is None:

        rule_file_url = '{}/{}.json'.format(DEACTIVATION_RULE_LOCATION, model_id)

        if not check_svn_location(rule_file_url):
            raise RuntimeError('Could not access required rule file for model "{}" '
                               'at "{}"'.format(model_id, rule_file_url))

        logger.info('Retrieving deactivation rules from "{}"'.format(rule_file_url))
        rule_file_contents = run_command(['svn', 'cat', rule_file_url])
        try:
            rule_json = json.loads(rule_file_contents)
        except BaseException as exc:
            logger.critical('Reading rules from "{}" failed'.format(rule_file_url))
            logger.exception(exc)
            raise
    else:
        logger.info('Retrieving deactivation rules from "{}"'.format(rule_file))
        try:
            rule_json = read_json(rule_file)
        except BaseException as exc:
            logger.critical('Reading rules from "{}" failed'.format(rule_file))
            logger.exception(exc)
            raise

    commands_to_apply = []

    for expt_id, rules in rule_json.items():
        rule_applied = False
        if expt_id == '*':
            rule_applied = True
            commands_to_apply += rules
        elif '*' in expt_id:
            pattern = '^{}$'.format(expt_id.replace('*', '.*'))
            if re.match(pattern, experiment_id):
                rule_applied = True
                commands_to_apply += rules
        elif expt_id == experiment_id:
            rule_applied = True
            commands_to_apply += rules
        if rule_applied:
            logger.debug('Deactivation rule for experiment_id "{}" added to list'.format(expt_id))

    return commands_to_apply


def apply_deactivation_rules(rvf_file_location, commands_to_apply):
    """
    Apply deactivation rules to specified file in turn.

    Parameters
    ----------
    rvf_file_location : str
        Location of the requested variables file
    commands_to_apply : list of lists of str
        Commands to apply in sequence
    """
    logger = logging.getLogger(__name__)
    for command in commands_to_apply:
        # prepare_alter code is written around the object passed back
        # from argparse, so we have to construct one
        logger.info('Deactivating: "{}"'.format('", "'.join(command[:-1])))
        command_namespace = Namespace(
            rvfile=rvf_file_location,
            change_type='deactivate',
            default_priority=0,
            vars=command[:-1],
            comment=command[-1],
            override=False,
        )
        try:
            alter_variable_list(command_namespace)
        except BaseException as exc:
            logger.exception(exc, exc_info=1)
            raise


def run_auto_deactivate_variables(auto_deactivation_rules_file, output_file, model_id, experiment_id):
    """
    Perform the automatic deactivation of variables function on the
    specified output file given the rules file and simulation
    information.

    Parameters
    ----------
    auto_deactivation_rules_file : str or None
        File containing rules to use. If None then refer to the
        cdds/variable_issues repository
    output_file : str
        Location of the requested variables file to operate on
    model_id : str
        Model ID, e.g. "UKESM1-0-LL"
    experiment_id : str
        Experiment ID, e.g. "piControl"
    """
    logger = logging.getLogger(__name__)
    logger.info('*** Starting variable auto deactivation ***')
    commands_to_run = deactivation_commands(
        model_id, experiment_id, rule_file=auto_deactivation_rules_file)
    try:
        apply_deactivation_rules(output_file, commands_to_run)
    except BaseException as exc:
        logger.critical('Failed in applying deactivation rules')
        logger.exception(exc, exc_info=1)
        raise
