# (C) British Crown Copyright 2024-2025, Met Office.
# Please see LICENSE.md for license details.
"""Module to provide functionality for tearing down CDDS workflows"""
import logging
import os
import shutil

from cdds.common import run_command
from cdds.common.plugins.plugins import PluginStore
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
                "please contact the CDDS team for guidance, or remove associated workflows and data by hand."
            )

    plugin = PluginStore.instance().get_plugin()
    workflow_data_dir = plugin.data_directory(request)
    cdds_workflow_name = f'cdds_{request.common.workflow_basename}'

    if not _confirm_teardown(workflow_data_dir, cdds_workflow_name):

        logger.info("Teardown cancelled; no data was removed.")
        return

    clean_workflow(cdds_workflow_name)
    remove_data_dir(workflow_data_dir)
    logger.info('cdds_clean complete')


def remove_data_dir(data_dir: str) -> None:
    """Remove input and output directories within the specified data directory.

    Parameters
    ----------
    data_dir : str
        Path to the data directory containing input and output folders.
    """
    logger = logging.getLogger(__name__)
    logger.info('Removing input and output directories in: {}'.format(data_dir))

    removed_any = False
    for folder_name in ('input', 'output'):
        target_dir = os.path.join(data_dir, folder_name)
        if os.path.exists(target_dir):
            try:
                shutil.rmtree(target_dir)
                removed_any = True
                logger.info(f'Removed "{target_dir}" directory')
            except OSError:
                logger.exception(f'Failed to remove "{target_dir}" directory')
                raise
        else:
            logger.info(f'\n{target_dir} directory does not exist, skipping')

    if removed_any:
        logger.info('Data directory removal step complete')


def clean_workflow(workflow_name: str) -> None:
    """Clean the workflow with the given name.

    Parameters
    ----------
    workflow_name : str
        Name of the workflow that should be cleaned.
    """

    logger = logging.getLogger(__name__)
    logger.info('Running cylc clean on workflow {}'.format(workflow_name))

    clean_command = ['cylc', 'clean', workflow_name]
    stdout = run_command(clean_command)
    logger.info(stdout)
