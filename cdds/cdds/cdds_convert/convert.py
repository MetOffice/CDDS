# (C) British Crown Copyright 2017-2021, Met Office.
# Please see LICENSE.rst for license details.
"""
The main gateway module for the cdds_convert application.
"""

import cdds_convert.process

from cdds_configure.user_config import read_and_validate_request, create_user_config_files


def get_rose_args_list(rose_args, stream_ids, request_id):
    """

    Parameters
    ----------

    rose_args: list
        A list of template strings representing arguments to be passed to the
        rose suite-run command through the subprocess modules. This function
        will fill in template arguments for each stream. More
        information on the avilable options can be found through running
        rose suite-run --help on the command line.

    stream_ids: list
        A list of the names of the |stream identifiers| to be processed.

    request_id: string
        The CDDS |request identifier|.

    Returns
    -------
    list: A list of arguments to be passed to the rose suite-run command via
          ConvertProcess.submit_suite and subprocess. Each element is a list
          of strings.

    """
    rose_args_list = []
    for stream in stream_ids:
        rose_args_stream = [
            s1.format(stream=stream,
                      request_id=request_id)
            for s1 in rose_args + ['--opt-conf-key={stream}']]
        rose_args_list.append(rose_args_stream)

    return rose_args_list


def run_cdds_convert(arguments, rose_args):
    """
    Start a suite running to process data for each stream of processing.

    Parameters
    ----------
    arguments: :class:`hadsdk.arguments.Arguments` object
        The arguments specific to the `cdds_convert` script.
    rose_args: list
        List of string objects that will be passed as arguments to the
        rose suite-run command.

    """
    if not arguments.skip_configure:
        run_generate_user_config_files(arguments)

    process = cdds_convert.process.ConvertProcess(arguments)

    process.validate_streams()
    process.checkout_convert_suite()
    process.update_convert_suite_parameters()

    # loop over stream submitting suite with relevant opt conf key
    # e.g. rose suite-run --opt-conf-key=ap4
    streams_info = process.stream_components
    streams = list(streams_info.keys())
    stream_args_list = get_rose_args_list(rose_args, streams,
                                          process.request_id)
    for rose_args_stream in stream_args_list:
        process.submit_suite(
            simulation=arguments.simulation,
            rose_args=rose_args_stream,
        )


def run_generate_user_config_files(arguments):
    """
    Generates the |user configuration files| respectively to data in the given arguments.

    Parameters
    ----------
    arguments: :class:`hadsdk.arguments.Arguments` object
        The arguments specific to the `cdds_convert` script.
    """
    requested_variables_file = arguments.requested_variables_list_file
    template_name = arguments.user_config_template_name

    request = read_and_validate_request(arguments.request, arguments.args)
    create_user_config_files(request, requested_variables_file, template_name, arguments.output_cfg_dir)
