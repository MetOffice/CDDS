# (C) British Crown Copyright 2016-2025, Met Office.
# Please see LICENSE.md for license details.
"""
The :mod:`command_line` module contains the main functions for the
command line scripts in the ``bin`` directory.
"""
import argparse
import glob
import logging
import os

from cdds import __version__
from cdds.common.cdds_files.cdds_directories import update_log_dir
from cdds.common.plugins.plugin_loader import load_plugin
from cdds.common.request.request import read_request
from cdds.extract.common import stream_file_template
from cdds.extract.lang import set_language
from cdds.extract.runner import ExtractRunner
from cdds.extract.halo_removal import dehalo_multiple_files
from cdds.extract.validate import validate_streams
from cdds.common import configure_logger

from mip_convert.plugins.plugin_loader import load_mapping_plugin


COMPONENT = 'extract'
LOG_NAME = 'cdds_extract'


def parse_cdds_extract_command_line(user_arguments):
    """
    Return the names of the command line arguments for ``cdds_extract_spice``
    and their validated values.

    If this function is called from the Python interpreter with ``arguments``
    that contains any of the ``--version``, ``-h`` or ``--help`` options, the
    Python interpreter will be terminated.

    The output from this function can be used as the value of the ``arguments``
    parameter in the call to :func:`cdds.extract.command_line.main_cdds_extract_spice`.

    Parameters
    ----------
    user_arguments: list of strings
        The command line arguments to be parsed.

    Returns
    -------
    : :class:`cdds.arguments.Arguments` object
        The names of the command line arguments and their validated values.
    """
    parser = argparse.ArgumentParser(description='Extract the requested data from MASS on SPICE via a batch job')
    parser.add_argument('request',
                        help='The full path to the cfg file containing the information from the request.')
    parser.add_argument('-s',
                        '--streams',
                        default=None, nargs='*',
                        help='Restrict extraction only to these streams')
    arguments = parser.parse_args(user_arguments)
    return arguments


def main_cdds_extract(arguments=None):
    """
    Extract the requested data from MASS via command line.

    Parameters
    ----------
    arguments: list of strings
        The command line arguments to be parsed.
    """
    lang = set_language()
    # Parse the arguments.
    args = parse_cdds_extract_command_line(arguments)
    request = read_request(args.request)

    load_mapping_plugin(request.conversion.mip_convert_plugin,
                        request.conversion.mip_convert_external_plugin,
                        request.conversion.mip_convert_external_plugin_location)

    # Add stream suffix to the log name if running extract just for some streams
    log_name = LOG_NAME + '_' + "_".join(args.streams) if args.streams else LOG_NAME
    log_name = update_log_dir(log_name, request, 'extract')

    # Create the configured logger.
    configure_logger(log_name, request.common.log_level, False)
    # Retrieve the logger.
    logger = logging.getLogger(__name__)

    try:
        runner = ExtractRunner(args, lang)
        runner.run_extract()
        exit_code = 0
    except BaseException as exc:
        logger.critical(exc, exc_info=1)
        exit_code = 1
    return exit_code


def parse_remove_ocean_haloes_command_line(user_arguments):
    """
    Return the names of the command line arguments for ``remove_ocean_haloes``
    and their validated values.

    Parameters
    ----------
    user_arguments: list of strings
        The command line arguments to be parsed.

    Returns
    -------
    : :class:`cdds.arguments.Arguments` object
        The names of the command line arguments and their validated values.
    """
    parser = argparse.ArgumentParser(description='Strip ocean haloes from multiple files')
    parser.add_argument('destination', help='Directory to write stripped files to')
    parser.add_argument('filenames', nargs='+', help='Files to strip haloes from')
    parser.add_argument('model_id', help='The model_id of the model which produced the output')
    parser.add_argument('--overwrite', help='Overwrite files in target directory')
    parser.add_argument('--mip_era', default='CMIP6', help='The cdds plugin to load, "CMIP6" loaded by default')
    parser.add_argument('--plugin_module', help='The directory of an external plugin module')

    return parser.parse_args(user_arguments)


def parse_validate_streams_command_line(user_arguments):
    """
    Return the names of the command line arguments for ``validate_streams``
    and their validated values.

    Parameters
    ----------
    user_arguments: list of strings
        The command line arguments to be parsed.

    Returns
    -------
    : :class:`cdds.arguments.Arguments` object
        The names of the command line arguments and their validated values.
    """

    parser = argparse.ArgumentParser(description='Validate extracted data')
    parser.add_argument('request',
                        help='The full path to the JSON file containing the information from the request.')
    parser.add_argument('-s',
                        '--streams',
                        default=None, nargs='*',
                        help='Restrict validation only to these streams')
    # Add arguments common to all scripts.
    arguments = parser.parse_args(user_arguments)
    return arguments


def main_validate_streams(arguments=None):
    """

    Validates files in the 'input' directory.
    Parameters
    ----------
    arguments: list of strings
        The command line arguments to be parsed.
    """
    args = parse_validate_streams_command_line(arguments)
    request = read_request(args.request)

    # Load mapping plugin
    load_mapping_plugin(request.conversion.mip_convert_plugin,
                        request.conversion.mip_convert_external_plugin,
                        request.conversion.mip_convert_external_plugin_location)

    # Add stream suffix to the log name if running extract just for some streams
    log_name = 'validate' + '_' + "_".join(args.streams) if args.streams else LOG_NAME
    log_name = update_log_dir(log_name, request, 'extract')

    # Create the configured logger.
    configure_logger(log_name, request.common.log_level, False)

    # Retrieve the logger.
    logger = logging.getLogger(__name__)

    try:
        streams = args.streams
        if not streams:
            logger.critical("no streams selected")
            exit_code = 1
        elif len(streams) > 1:
            # for historical reasons the original code would allow user to run validation for multiple
            # streams. Extract has been parallelised since those early days and we split processing, including
            # data retrieval, into single streams. That's why the data structure is a list, although
            # we no longer iterate through streams, only take the first (and hopefully the only) element.
            logger.critical("can validate only one stream at the time")
            exit_code = 1
        else:
            validation_result = validate_streams(streams, args)
            if validation_result.valid:
                exit_code = 0
            else:
                exit_code = 1
    except BaseException as exc:
        logger.critical(exc, exc_info=1)
        exit_code = 1
    return exit_code


def main_remove_ocean_haloes(arguments=None):
    """
    Strip haloes from multiple ocean files

    Parameters
    ----------
    arguments: list of strings
        The command line arguments to be parsed.
    """
    # Parse the arguments
    args = parse_remove_ocean_haloes_command_line(arguments)

    # Create the configured logger.
    configure_logger(LOG_NAME, logging.INFO, False)

    # Retrieve the logger.
    logger = logging.getLogger(__name__)

    # Log version.
    logger.info('Using Extract version {}'.format(__version__))

    load_plugin(args.mip_era, args.plugin_module)

    try:
        dehalo_multiple_files(args.filenames, args.destination, args.overwrite, args.model_id)
        exit_code = 0
    except BaseException as exc:
        logger.critical(exc, exc_info=1)
        exit_code = 1
    return exit_code


def main_path_reformatter():
    """
    Main function of the path_reformatter script.
    """
    args = parse_arguments()
    suite_id = args.suite_id
    full_root_path = os.path.join(args.input_dir, suite_id)

    timesteps = next(os.walk(full_root_path))[1]

    for stream in args.streams:
        print('Collecting all input files for stream {} under {}'.format(stream, full_root_path))

        filename_templates = stream_file_template(stream, suite_id)
        data_files = []

        if args.output_dir is None:
            output_dir = os.path.join(full_root_path, stream)
        else:
            output_dir = os.path.join(args.output_dir, stream)

        try:
            os.mkdir(output_dir)
            print('Creating directory for stream {}...'.format(stream))
        except FileExistsError:
            pass

        for timestep_dir in timesteps:
            for glob_template in filename_templates:
                data_files.extend(glob.glob(os.path.join(full_root_path, timestep_dir, glob_template)))

        print('{} files found...'.format(len(data_files)))

        print('Creating symlinks in {}'.format(output_dir))

        for data_file in data_files:
            try:
                os.symlink(data_file, os.path.join(output_dir, os.path.basename(data_file)))
            except FileExistsError:
                print('{} exists, skipping...'.format(os.path.basename(data_file)))
                pass

        print('Done')


def parse_arguments():
    """
    Parse command line arguments.

    Returns
    -------
    Command line arguments for the path_formatter script.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('input_dir', help='Input data directory (full filepath including the /input/ subdirectory)')
    parser.add_argument('output_dir', help='Reprocessed input directory (defaulting to the --input_dir)', default=None)
    parser.add_argument('suite_id', help='Suite id')
    parser.add_argument('streams', help='Streams to be symlinked', nargs='*')
    args = parser.parse_args()
    return args
