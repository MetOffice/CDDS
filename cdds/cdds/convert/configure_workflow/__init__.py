# (C) British Crown Copyright 2024-2025, Met Office.
# Please see LICENSE.md for license details.
import argparse
import logging
from typing import Tuple

from cdds import _DEV
from cdds.common import check_directory, configure_logger
from cdds.common.cdds_files.cdds_directories import update_log_dir
from cdds.common.plugins.plugins import PluginStore
from cdds.common.request.request import Request, read_request
from cdds.common.constants import PRINT_STACK_TRACE
from cdds.configure.user_config import create_user_config_files
from cdds.convert.arguments import ConvertArguments, add_user_config_data_files
from cdds.convert.configure_workflow.calculate_isodatetimes import CalculateISODatetimes
from cdds.convert.configure_workflow.configure_template_variables import ConfigureTemplateVariables
from cdds.convert.configure_workflow.stream_components import StreamComponents
from cdds.convert.configure_workflow.stream_model_parameters import StreamModelParameters
from cdds.convert.configure_workflow.workflow_manager import WorkflowManager
from cdds.convert.exceptions import ArgumentError

COMPONENT = 'convert'
CONVERT_LOG_NAME = 'cdds_convert'


def main_cdds_convert() -> int:
    """Initialise the CDDS convert process.

    Returns
    -------
    int
        Exit code
    """
    arguments, request = parse_args_cdds_convert()

    log_name = update_log_dir(CONVERT_LOG_NAME, request, 'convert')

    configure_logger(log_name, request.common.log_level, False)

    try:
        run_cdds_convert(arguments, request)
        exit_code = 0
    except BaseException as exception:
        logging.getLogger(__name__)
        logging.critical(exception, exc_info=PRINT_STACK_TRACE)
        exit_code = 1
    return exit_code


def parse_args_cdds_convert() -> Tuple[ConvertArguments, Request]:
    """Returns the command line arguments and the request for 'cdds_convert'

    Returns
    -------
    Tuple[ConvertArguments, Request]
        Tuple of command line arguments and request object
    """
    description = 'CDDS convert process initiator'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('request',
                        type=str,
                        help='Obtain configuration from request configuration file'
                        )
    parser.add_argument('-s',
                        '--streams',
                        default=[],
                        nargs='*',
                        help='Restrict processing suites to only to these streams.'
                        )
    parser.add_argument('-n',
                        '--no-submit',
                        action='store_true',
                        help='Do not run cylc vip on the templated workflow.'
                        )

    args = parser.parse_args()
    request = read_request(args.request)

    if _DEV and request.data.output_mass_suffix == "production":
        raise ArgumentError("Cannot archive data to production location in development mode")

    # Get Cdds plugin and overload model related values if necessary
    plugin = PluginStore.instance().get_plugin()

    if request.conversion.model_params_dir:
        check_directory(request.conversion.model_params_dir)
        plugin.overload_models_parameters(request.conversion.model_params_dir)

    arguments = ConvertArguments(request_path=args.request, streams=args.streams, no_submit=args.no_submit)
    if not request.conversion.skip_configure:
        arguments = add_user_config_data_files(arguments, request)

    return arguments, request


def run_cdds_convert(arguments: ConvertArguments, request: "Request") -> None:
    """
    Parameters
    ----------
    arguments : ConvertArguments
        The arguments specific to the 'cdds_convert' script.
    request : Request
        The request information of 'cdds_convert'
    """
    logger = logging.getLogger(__name__)

    requested_variables_file = arguments.requested_variables_list_file
    if not request.conversion.skip_configure:
        create_user_config_files(request, requested_variables_file, arguments.output_cfg_dir)

    stream_components = StreamComponents(arguments, request)
    stream_components.build_stream_components()
    stream_components.validate_streams()

    stream_variables = stream_jinja2_variables(request, stream_components)

    workflow_configuration = ConfigureTemplateVariables(
        arguments,
        request,
        stream_variables,
    )

    workflow_manager = WorkflowManager(request, workflow_configuration)
    workflow_manager.checkout_convert_workflow()
    workflow_manager.update()
    workflow_manager.clean_workflow()

    if arguments.no_submit:
        logger.info("Skipping running cylc vip. Templated workflow path:")
        logger.info(workflow_manager.workflow_destination)
    else:
        workflow_manager.run_workflow()


def stream_jinja2_variables(request, stream_components):
    jijna2_variables = {}

    for stream in stream_components.active_streams:
        stream_info = StreamModelParameters(
            request=request,
            stream=stream,
            components=stream_components,
        )
        isodatetime = CalculateISODatetimes(
            start_date=request.data.start_date,
            end_date=request.data.end_date,
            cycling_frequency=stream_info.cycling_frequency(),
            concatenation_window=stream_info.concatenation_period(),
            base_date=request.metadata.base_date,
        )

        jijna2_variables[stream] = isodatetime.as_jinja2() | stream_info.as_jinja2()

    return restructure_dictionary(jijna2_variables)


def restructure_dictionary(old_dict):
    new_dict = {}
    for stream_key, sub_dict in old_dict.items():
        for inner_key, value in sub_dict.items():
            if inner_key not in new_dict.keys():
                new_dict[inner_key] = {stream_key: value}
            else:
                new_dict[inner_key][stream_key] = value
    return new_dict
