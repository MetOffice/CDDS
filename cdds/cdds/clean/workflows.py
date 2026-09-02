# (C) British Crown Copyright 2024-2025, Met Office.
# Please see LICENSE.md for license details.
"""Module to provide functionality for CDDS workflows"""
import logging

from cdds.common import run_command
from cdds.common.request.request import Request


def run_teardown(request: Request) -> None:
    """Remove data directory and clean the CDDS workflow associated with the given request.

    Parameters
    ----------
    request : Request
        Request containing information about the workflow
    """

    workflow_name = 'cdds_{request_id}'
    for argument in request.conversion.cylc_args:
        if argument == '--workflow-name' or argument.startswith('--workflow-name'):
            raise ValueError(
                "'--workflow-name' detected in the request file's cylc_args, "
                "please contact the CDDS team for more information."
            )

    request_id = request.common.workflow_basename

    clean_workflow(workflow_name.format(request_id=request_id))


def clean_workflow(workflow_name: str) -> None:
    """Clean the workflow with the given name

    Parameters
    ----------
    workflow_name : str
        Name of the workflow that should be cleaned
    """
    logger = logging.getLogger(__name__)
    logger.info('Clean workflow {}'.format(workflow_name))

    clean_command = ['cylc', 'clean', workflow_name]
    stdout = run_command(clean_command)
    logger.info(stdout)
