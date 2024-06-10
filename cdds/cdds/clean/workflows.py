# (C) British Crown Copyright 2024, Met Office.
# Please see LICENSE.rst for license details.
"""
Module to provide functionality for CDDS workflows
"""
import logging

from cdds.common import run_command
from cdds.common.request.request import Request


def clean_workflows(request: Request) -> None:
    """
    Clean CDDS streams workflows with the workflow base name
    containing the request

    :param request: Request containing information about the workflows
    :type request: Request
    """
    check_if_cylc_version()

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
    """
    Clean the workflow with the given name

    :param workflow_name: Name of the workflow that should be cleaned
    :type workflow_name: str
    """
    logger = logging.getLogger(__name__)
    logger.info('Clean workflow {}'.format(workflow_name))

    clean_command = ['cylc', 'clean', workflow_name]
    stdout = run_command(clean_command)
    logger.info(stdout)


def check_if_cylc_version() -> None:
    """
    Check that cylc >= 8 is active and raise an exception if not
    """
    logger = logging.getLogger(__name__)

    cylc_version_command = ['cylc', '--version']
    cylc_version = run_command(cylc_version_command)

    if not cylc_version or not cylc_version.startswith('8'):
        message = 'Cylc version >=8 must be active.'
        logger.critical(message)
        raise ValueError(message)
