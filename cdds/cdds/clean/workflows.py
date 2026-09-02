# (C) British Crown Copyright 2024-2025, Met Office.
# Please see LICENSE.md for license details.
"""Module to provide functionality for CDDS workflows"""
import logging

from cdds.common import run_command
from cdds.common.request.request import Request


def clean_workflows(request: Request) -> None:
    """Clean CDDS streams workflows with the workflow base name containing the request

    Parameters
    ----------
    request : Request
        Request containing information about the workflows
    """

    workflow_name = 'cdds_{request_id}_{stream}'
    for argument in request.conversion.cylc_args:
        if argument.startswith("--workflow-name"):
            # When loading the conversion section the `_{stream}` will already be added if
            # the `--workflow-name` is already be set. So, no need here to add `_{stream}`.
            workflow_name = argument.split("=")[1]

    request_id = request.common.workflow_basename

    for stream in request.data.streams:
        stream_workflow = workflow_name.format(request_id=request_id, stream=stream)
        clean_workflow(stream_workflow)


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
