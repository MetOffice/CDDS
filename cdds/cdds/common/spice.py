# (C) British Crown Copyright 2019-2025, Met Office.
# Please see LICENSE.md for license details.
"""Code to set up a batch script to run CDDS components on spice"""
import logging
import os

from cdds.common.constants import SCRIPT_TEMPLATE, PRINT_STACK_TRACE
from cdds.common import run_command


def write_spice_job_script(job_script, substitutions):
    """Write a batch script to the supplied location using the
    substitutions provided.

    Parameters
    ----------
    job_script : str
        The full path to write the batch job script to.
    substitutions : dict
        Dictionary of substitutions to use when writing the script.
    """
    logger = logging.getLogger(__name__)

    for field in ['email', 'partition']:
        if field in substitutions:
            logger.warning('Overwriting field "{}" with default value')

    substitutions['email'] = get_email_of_current_user()
    try:
        script_text = SCRIPT_TEMPLATE.format(**substitutions)
    except KeyError:
        logger.critical('Writing batch script to "{}" failed.'.format(job_script), exc_info=PRINT_STACK_TRACE)
        raise
    logger.info('Writing batch script to "{}"'.format(job_script))
    logger.debug('SPICE batch script content:\n{}'.format(script_text))
    with open(job_script, 'w') as script_file_handle:
        script_file_handle.write(script_text)


def get_user():
    """Return the name of the user running this script

    Returns
    -------
    str
        The name of user running this script.
    """

    return os.getlogin()


def get_email_of_current_user():
    """Return the e-mail address of the user running this script.

    Returns
    -------
    str
        The e-mail address of user running this script.
    """
    logger = logging.getLogger(__name__)
    aliases = run_command(['getent', 'aliases'])
    email = None
    login = get_user()
    for line in aliases.split('\n'):
        # Try except clause needed to combat occasional, unreproducible issues
        # with the output of "getent aliases" command.
        try:
            username, user_email = [i.strip() for i in line.split(':')]
        except ValueError:
            logger.critical('Could not interpret line from "getent aliases" '
                            'command: "{}". Skipping.'.format(line.strip()))
            continue

        if username == login:
            email = user_email
            break

    if email is None:
        logger.warning('Email address of current user could not be determined')

    return email


def submit_spice_job_script(job_script):
    """Submit the job script specified to SPICE.

    Parameters
    ----------
    job_script : str
        The full path to the job script to be submitted.
    """
    logger = logging.getLogger(__name__)
    command = ['sbatch', job_script]
    logger.info('Submitting job script "{}"'.format(job_script))
    output = run_command(command)
    logger.info('Output from sbatch command: "{}"'.format(output.strip()))
    logger.info('Deleting job script')
    try:
        os.unlink(job_script)
    except OSError:
        logger.critical('Deleting job script failed', exc_info=PRINT_STACK_TRACE)
