# (C) British Crown Copyright 2024-2025, Met Office.
# Please see LICENSE.md for license details.
"""Module to provide functionality for tearing down CDDS workflows"""
import logging
import shutil

from cdds.common import run_command
from cdds.common.request.request import Request


def _confirm_teardown(data_dir: str, workflow_name: str) -> bool:
    """Require explicit user confirmation before deleting data."""
    response = input(
        "This will permanently delete input and output data from '{}', and clean it's associated workflow '{}'. \n"
        "Type 'yes' to continue: ".format(data_dir, workflow_name)
    ).strip().lower()

    return response == 'yes'


def run_teardown(request: Request) -> None:
    """Remove data directory and clean the CDDS workflow associated with the given request.

    Parameters
    ----------
    request : Request
        Request containing information about the workflow
    """
    logger = logging.getLogger(__name__)
    # First check workflow name wasn't used in cylc_args field.
    # Possibly a hangover from an older version of cdds.
    # Have switched to an error just in case someone tries to use it.
    for argument in request.conversion.cylc_args or []:
        # Catch both '--workflow-name' and '--workflow-name=<value>' forms.
        if argument == '--workflow-name' or argument.startswith('--workflow-name'):
            raise ValueError(
                "'--workflow-name' detected in the request file's cylc_args, "
                "please contact the CDDS team for guidance, or remove associated workflows by hand."
            )
    data_dir = request.common.root_data_dir
    request_id = request.common.workflow_basename
    workflow_name = f'cdds_{request_id}'

    if not _confirm_teardown(data_dir, workflow_name):

        logger.info("Teardown cancelled; no data was removed.")
        return

    clean_workflow(workflow_name)
    remove_data_dir(data_dir)
    logger.info('cdds_clean complete.')


def remove_data_dir(data_dir: str) -> None:
    """Remove the specified data directory.

    Parameters
    ----------
    data_dir : str
        Path to the data directory to be removed.
    """
    logger = logging.getLogger(__name__)
    logger.info('Removing data directory: {}'.format(data_dir))

    try:
        shutil.rmtree(data_dir)
    except OSError:
        logger.exception('Failed to remove data directory: %s', data_dir)
        raise

    logger.info('Data directory removal complete.')


def clean_workflow(workflow_name: str) -> None:
    """Clean the workflow with the given name.

    Parameters
    ----------
    workflow_name : str
        Name of the workflow that should be cleaned.
    """

    logger = logging.getLogger(__name__)
    logger.info('Clean workflow {}'.format(workflow_name))

    clean_command = ['cylc', 'clean', workflow_name]
    stdout = run_command(clean_command)
    logger.info(stdout)

