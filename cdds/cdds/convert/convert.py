# (C) British Crown Copyright 2017-2025, Met Office.
# Please see LICENSE.rst for license details.
"""
The main gateway module for the cdds_convert application.
"""
from argparse import Namespace

import cdds.convert.process

from cdds.configure.user_config import create_user_config_files
from cdds.common.request.request import read_request, Request
from cdds.convert.arguments import ConvertArguments


def get_cylc_args_list(cylc_args, stream_ids, request_id):
    """

    Parameters
    ----------

    cylc_args: list
        A list of template strings representing arguments to be passed to the
        cylc vip command through the subprocess modules. This function
        will fill in template arguments for each stream. More
        information on the avilable options can be found through running
        cylc vip --help on the command line.

    stream_ids: list
        A list of the names of the |stream identifiers| to be processed.

    request_id: string
        The CDDS |request identifier|.

    Returns
    -------
    list: A list of arguments to be passed to the cylc vip command via
          ConvertProcess.submit_workflow and subprocess. Each element is a list
          of strings.

    """
    cylc_args_list = []
    for stream in stream_ids:
        cylc_args_stream = [
            s1.format(stream=stream,
                      request_id=request_id)
            for s1 in cylc_args + ['--opt-conf-key={stream}']]
        cylc_args_list.append(cylc_args_stream)

    return cylc_args_list


def run_cdds_convert(arguments: ConvertArguments, request: Request) -> None:
    """
    Start a workflow to process data for each stream of processing.

    :param arguments: The arguments specific to the 'cdds_convert' script.
    :type arguments: ConvertArguments
    :param request: The request information of 'cdds_convert'
    :type request: Request
    """
    if not request.conversion.skip_configure:
        _generate_user_config_files(arguments, request)

    process = cdds.convert.process.ConvertProcess(arguments, request)

    process.validate_streams()
    process.checkout_convert_workflow()
    process.update_convert_workflow_parameters()

    # loop over stream submitting workflow with relevant opt conf key
    # e.g. cylc vip --opt-conf-key=ap4
    streams_info = process.stream_components
    streams = list(streams_info.keys())
    stream_args_list = get_cylc_args_list(request.conversion.cylc_args, streams, process.request_id)
    for cylc_args_stream in stream_args_list:
        process.submit_workflow(
            simulation=request.common.simulation,
            cylc_args=cylc_args_stream,
        )


def _generate_user_config_files(arguments: ConvertArguments, request: Request) -> None:
    requested_variables_file = arguments.requested_variables_list_file
    create_user_config_files(request, requested_variables_file, arguments.output_cfg_dir)
