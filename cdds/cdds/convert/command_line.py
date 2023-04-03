# (C) British Crown Copyright 2017-2022, Met Office.
# Please see LICENSE.rst for license details.
"""
Command line interfaces for cdds_convert and mip_concatenate tasks.
"""
import argparse
from datetime import datetime
import logging

from cdds.common.plugins.plugin_loader import load_plugin
from cdds.common.plugins.plugins import PluginStore

from cdds.arguments import read_default_arguments
from cdds.common import (configure_logger, common_command_line_args,
                         root_dir_args, mass_output_args, check_directory)
from cdds.deprecated.config import (update_arguments_for_proc_dir,
                                    update_arguments_paths,
                                    update_log_dir)

from cdds import __version__, _DEV
from cdds.common.constants import (REQUIRED_KEYS_FOR_PROC_DIRECTORY,
                                   DATESTAMP_TEMPLATE, DATESTAMP_PARSER_STR)
from cdds.common.request import read_request
from cdds.convert.arguments import update_user_config_data_files
from cdds.convert.exceptions import (OrganiseEnvironmentError,
                                     OrganiseTransposeError,
                                     WrapperEnvironmentError,
                                     WrapperMissingFilesError,
                                     ArgumentError)
from cdds.convert.concatenation import batch_concatenation
from cdds.convert.concatenation.concatenation_setup import concatenation_setup
from cdds.convert.convert import run_cdds_convert
from cdds.convert.mip_convert_wrapper.wrapper import run_mip_convert_wrapper
from cdds.convert.organise_files import organise_files

COMPONENT = 'convert'


def main_cdds_convert():
    """
    Initiator for the CDDS convert process.
    """

    arguments, rose_args = parse_args_cdds_convert()

    configure_logger(arguments.log_name, logging.INFO, arguments.append_log)

    try:
        run_cdds_convert(arguments, rose_args)
        exit_code = 0
    except BaseException as be1:
        logging.getLogger(__name__)
        logging.critical(be1, exc_info=1)
        exit_code = 1
    return exit_code


def parse_args_cdds_convert():
    """
    Returns the command line arguments for 'cdds_convert' and their validated
    values.

    Returns
    -------
    Command line arguments for the cdds_convert script.

    """
    arguments = read_default_arguments('cdds.convert', 'cdds_convert')
    description = 'CDDS convert process initiator'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('request',
                        type=str,
                        help=('Obtain configuration from Request JSON file')
                        )
    help_msg = 'Restrict processing suites to only to these streams.'
    parser.add_argument('-s', '--streams', default=[], nargs='*',
                        help=help_msg)
    # Use a branch of the processing suite other than that specified in the
    # config project. This is for developing changes to the suite.
    parser.add_argument('--rose_suite_branch',
                        type=str,
                        default=arguments.rose_suite_branch,
                        help='For development purposes only.'
                        )
    parser.add_argument('--simulation', action='store_true',
                        help='Run rose suite in simulation mode')

    parser.add_argument('--suite_run_args',
                        dest='rose_args',
                        type=str,
                        help='Arguments to be passed to rose suite-run. For '
                             'more info on the allowed options, please see'
                             'rose suite-run --help.',
                        default=arguments.suite_run_args)
    parser.add_argument('--skip_extract',
                        dest='skip_extract',
                        action='store_true',
                        default=arguments.skip_extract,
                        help=('Skip the extract task at the start of the suite for each stream. '
                              '[Default: {}]').format(arguments.skip_extract))
    parser.add_argument('--skip_qc',
                        dest='skip_qc',
                        action='store_true',
                        default=arguments.skip_qc,
                        help=('Skip the quality control task at the end of the suite for each stream.'
                              '[Default: {}]').format(arguments.skip_qc))
    parser.add_argument('--skip_transfer',
                        dest='skip_transfer',
                        action='store_true',
                        default=arguments.skip_transfer,
                        help=('Skip the transfer task at the end of the suite for each stream. '
                              '[Default: {}]').format(arguments.skip_transfer))
    parser.add_argument('--skip_extract_validation',
                        dest='skip_extract_validation',
                        action='store_true',
                        default=arguments.skip_extract_validation,
                        help=('Skip validation the end of the extract task. '
                              '[Default: {}]').format(arguments.skip_extract_validation))
    mass_output_args(parser, arguments.output_mass_suffix, arguments.output_mass_root)

    parser.add_argument('--no_email_notifications',
                        dest='email_notifications',
                        help='If present, no email notifications will be '
                             'sent from the processing suites.',
                        action='store_false')

    parser.add_argument('--scale_memory_limits',
                        dest='scale_memory_limits',
                        default=None,
                        type=float,
                        help='Memory scaling factor to be applied to all '
                             'batch jobs. Please contact the CDDS team for '
                             'advice before using this option.')
    parser.add_argument('--override_cycling_freq',
                        dest='override_cycling_freq',
                        default=[],
                        nargs='*',
                        help='Override default cycling frequency for specified stream. Each stream should be '
                             'specified along with the cycling frequency using the format "<stream>=<frequency>", '
                             'e.g. "ap7=P3M ap8=P1M".')

    parser.add_argument('--model_params_dir',
                        dest='model_params_dir',
                        default=None,
                        help='If present, the model parameters will be overloaded by the data in the json'
                             'files containing in the given directory.')

    parser.add_argument('--skip_configure',
                        dest='skip_configure',
                        help='If present, the configure step will be skipped.',
                        action='store_true')

    parser.add_argument('--relaxed_cmor',
                        help='If specified, CMIP6 style validation is not performed by CMOR.',
                        action='store_true'
                        )

    parser.add_argument('-d',
                        '--data_request_version',
                        default=arguments.data_request_version,
                        help='The version of the data request.')

    parser.add_argument('--root_ancil_dir',
                        default=arguments.root_ancil_dir,
                        help='Specify the root path to the location of the ancillary files.'
                             'The files should be located in a sub-directory of this path '
                             'with the name of the model_id.')

    def _validate_archive_data_version(arg):
        try:
            datetime.strptime(arg, DATESTAMP_PARSER_STR)
            return arg
        except ValueError:
            raise ArgumentError('archive_data_version must have format "{}"'.format(DATESTAMP_PARSER_STR))

    parser.add_argument('--archive_data_version',
                        default=DATESTAMP_TEMPLATE.format(dt=datetime.now()),
                        type=_validate_archive_data_version,
                        help='Set the version used when archiving data to MASS and constructing '
                             'dataset ids (format vYYYYMMDD)')
    root_dir_args(parser, arguments.root_proc_dir, arguments.root_data_dir)
    common_command_line_args(parser, arguments.log_name, arguments.log_level, __version__)

    args = parser.parse_args()

    if _DEV and arguments.output_mass_suffix == "production":
        raise ArgumentError("Cannot archive data to production location in development mode")

    arguments.add_user_args(args)
    arguments = update_arguments_paths(arguments, ['model_params_dir'])
    # Update arguments to ensure that log ends up in the right place
    request = read_request(args.request, REQUIRED_KEYS_FOR_PROC_DIRECTORY)
    arguments = update_arguments_for_proc_dir(arguments, request, COMPONENT)
    arguments.mip_era = request.mip_era
    arguments.external_plugin = request.external_plugin
    arguments.external_plugin_location = request.external_plugin_location

    # Get Cdds plugin and overload model related values if necessary
    plugin = PluginStore.instance().get_plugin()

    if arguments.model_params_dir is not None:
        check_directory(arguments.model_params_dir)
        plugin.overload_models_parameters(arguments.model_params_dir)

    user_rose_args_str = args.rose_args
    rose_args = user_rose_args_str.split(' ') + ['-v']

    # If user does not specify a run name for the rose suite, use
    # cdds_{request_id}
    if '--name' in user_rose_args_str:
        name_indices = [ix1 for ix1, arg1 in enumerate(rose_args)
                        if '--name' in arg1]
        for ix1 in name_indices:
            if '=' in rose_args[ix1]:
                ix_to_change = ix1
            else:
                ix_to_change = ix1 + 1
            rose_args[ix_to_change] = rose_args[ix_to_change] + '_{stream}'

    else:
        rose_args += ['--name=cdds_{request_id}_{stream}']

    if not arguments.skip_configure:
        arguments = update_user_config_data_files(arguments, request)

    arguments = update_log_dir(arguments, COMPONENT)
    return arguments, rose_args


def _parse_args_concat_setup():
    """
    Setup argument parser for mip_concatenate_setup
    """
    parser = argparse.ArgumentParser(description=('Batch concatenation '
                                                  'setup tool'))
    parser.add_argument('config_file', type=str,
                        help='Location of config file')
    parser.add_argument('log_file', type=str, help='Log file')
    parser.add_argument('--append_log', action='store_true',
                        help='Append to existing log file')
    parser.add_argument('--mip_era', default='CMIP6', type=str,
                        help='The MIP era (e.g. CMIP6)')
    parser.add_argument('--external_plugin', default='', type=str,
                        help='Module path to external CDDS plugin')
    parser.add_argument('--external_plugin_location', default='', type=str,
                        help='Path to external CDDS plugin implementation')
    arguments = parser.parse_args()
    load_plugin(arguments.mip_era, arguments.external_plugin, arguments.external_plugin_location)
    return arguments.config_file, arguments.log_file, arguments.append_log


def main_concatenation_setup():
    """
    Command line interface for mip_concatenate_setup tasks.
    """
    config_file, log_file, append_log = _parse_args_concat_setup()
    try:
        concatenation_setup(config_file, log_file, append_log)

        exit_code = 0
    except BaseException as be1:
        logging.getLogger(__name__)
        logging.exception(be1)
        exit_code = 1
    return exit_code


def main_concatenation_batch():
    """
    Command line interface for mip_batch_concatenate tasks.
    """
    parser = argparse.ArgumentParser(description='MIP batch concatenation '
                                                 'tool')
    parser.add_argument('database', type=str, help='task database')
    parser.add_argument('log_file', type=str, help='log file')
    parser.add_argument('-a', '--append_log', action='store_true',
                        help='append to rather than overwrite log')
    parser.add_argument('-n', '--nthreads', type=int, default=1,
                        help='number of concurrent threads to use')
    parser.add_argument('--simulate', action='store_true',
                        help=('Simulate the concatenation process by printing,'
                              ' rather than running, commands.'))
    args = parser.parse_args()

    configure_logger(args.log_file, 0, args.append_log, threaded=True)

    try:
        batch_concatenation(args.database, args.nthreads, dummy_run=args.simulate)
        exit_code = 0
    except BaseException as be1:
        logger = logging.getLogger(__name__)
        logger.critical('Concatenation failed', exc_info=1)
        exit_code = 1

    return exit_code


def main_run_mip_convert(arguments=None):
    """
    The main function for the run_mip_convert script.

    Returns
    -------
    : int
        The exit code for the script, which is 0 if execution was successful,
        non-zero otherwise.
    """
    exit_code = 0
    arguments = _parse_run_mip_convert_parameters(arguments)
    try:
        exit_code = run_mip_convert_wrapper(arguments)
    except WrapperEnvironmentError as we1:
        logging.getLogger(__name__)
        logging.exception(we1)
        exit_code = 2
    except WrapperMissingFilesError as wmf1:
        logging.getLogger(__name__)
        logging.exception(wmf1)
        exit_code = 3
    except BaseException as exc:
        logging.getLogger(__name__)
        logging.exception(exc)
        exit_code = 1
    return exit_code


def _parse_run_mip_convert_parameters(arguments):
    user_arguments = arguments
    arguments = read_default_arguments('cdds.convert', 'run_mip_convert')

    description = 'Arguments for running MIP convert'
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--mip_era',
                        default='CMIP6',
                        type=str,
                        help='The MIP era (e.g. CMIP6)')
    parser.add_argument('--external_plugin',
                        default='',
                        type=str,
                        help='Module path to external CDDS plugin')
    parser.add_argument('--external_plugin_location',
                        default='',
                        type=str,
                        help='Path to the external CDDS plugin implementation')
    parsed_arguments = parser.parse_args(args=user_arguments)
    arguments.add_user_args(parsed_arguments)
    load_plugin(arguments.mip_era, arguments.external_plugin, arguments.external_plugin_location)
    return arguments


def main_organise_files():
    """
    The main function for the organise_files script.

    Returns
    -------
    : int
        The exit code for the script, which is 0 if execution was successful,
        non-zero otherwise.
    """
    exit_code = 0
    logging.getLogger(__name__)
    try:
        organise_files()
    except OrganiseEnvironmentError as oee:
        logging.exception(oee)
        exit_code = 2
    except OrganiseTransposeError as ote:
        logging.exception(ote)
        exit_code = 3
    except BaseException as exc:
        logging.exception(exc)
        exit_code = 1
    return exit_code
