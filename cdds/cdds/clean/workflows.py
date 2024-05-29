# (C) British Crown Copyright 2024, Met Office.
# Please see LICENSE.rst for license details.
import logging
import os

from cdds.common import run_command
from cdds.common.request.request import Request


def clean_workflows(request: Request):
    check_if_cylc8_env()

    workflow_name = 'cdds_{request_id}_{stream}'
    for argument in request.conversion.cylc_args:
        if argument.startswith("--workflow-name"):
            workflow_name = argument.split("=")[1]

    request_id = request.common.workflow_basename

    for stream in request.data.streams:
        stream_workflow = workflow_name.format(request_id=request_id, stream=stream)
        clean_workflow(stream_workflow)


def clean_workflow(workflow_name: str):
    logger = logging.getLogger(__name__)
    logger.info('Clean workflow {}'.format(workflow_name))

    clean_command = ['cylc', 'clean', workflow_name]
    stdout = run_command(clean_command)
    logger.info(stdout)


def check_if_cylc8_env():
    logger = logging.getLogger(__name__)
    cylc_version = os.environ['CYLC_VERSION']
    if not cylc_version or cylc_version != '8':
        message = 'Cylc 8 is not active. Please, run "export CYLC_VERSION=8" before cleaning the workflows.'
        logger.info(message)
        raise ValueError()
