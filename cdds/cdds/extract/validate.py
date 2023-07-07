# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.

import logging
import os

from cdds.common import generate_datestamps, generate_datestamps_nc
from cdds.common.constants import REQUIRED_KEYS_FOR_PROC_DIRECTORY
from cdds.common.plugins.plugins import PluginStore
from cdds.common.request import read_request
from cdds.extract.common import (
    configure_mappings, configure_variables,
    get_data_target, get_streams,
    validate_stash_fields, validate_netcdf,
    StreamValidationResult, build_mass_location,
)
from cdds.extract.filters import Filters
from cdds.deprecated.config import FullPaths


def validate_streams(streams, args):
    logger = logging.getLogger(__name__)

    request = read_request(args.request, REQUIRED_KEYS_FOR_PROC_DIRECTORY)
    full_paths = FullPaths(args, request)
    model_params = PluginStore.instance().get_plugin().models_parameters(request.model_id)
    stream_file_info = model_params.stream_file_info()
    stream_details = get_streams(request.streaminfo, request.suite_id, streams)
    stream = stream_details[0]

    var_list = configure_variables(os.path.join(full_paths.component_directory("prepare"),
                                                full_paths.requested_variables_list_filename))

    # configure mappings for each variables
    mappings = Filters(full_paths.proc_directory, var_list)
    mappings.set_mappings(args.mip_table_dir, request)
    mapping_status = configure_mappings(mappings)

    if request.mass_ensemble_member:
        mappings.ensemble_member_id = request.mass_ensemble_member
        file_type = stream["streamtype"]
        mappings.source = build_mass_location(request.mass_data_class,
                                              request.suite_id,
                                              streams[0],
                                              file_type,
                                              request.mass_ensemble_member)
    else:
        mappings.ensemble_member_id = None
    mappings.stream = streams[0]

    # generate expected filenames
    start, end = request.run_bounds.split()
    start, end = "".join(start.split("-")[:3]), "".join(end.split("-")[:3])
    file_frequency = stream_file_info.file_frequencies[streams[0]].frequency

    if not stream_details:
        logger.info('Command line stream selection {[]} not found in the request file'.format(', '.join(streams)))
    # we're no longer looping through multiple streams

    stream_validation = StreamValidationResult(stream['stream'])

    if stream['stream'] in mapping_status:
        data_target = get_data_target(full_paths.input_data_directory, stream)
        _, _, _, stash_codes = (mappings.format_filter(stream['streamtype'], stream['stream']))

        if stream["streamtype"] == "pp":
            datestamps, _ = generate_datestamps(start, end, file_frequency)
            filenames = mappings._generate_filenames_pp(datestamps)

        elif stream["streamtype"] == "nc":
            datestamps, _ = generate_datestamps_nc(start, end, file_frequency)
            filenames = []
            substreams = list(mappings.filters.keys())
            for sub_stream in substreams:
                filenames += mappings._generate_filenames_nc(datestamps, sub_stream)

        validate(data_target, stream, stash_codes, stream_validation, filenames)
    else:
        logger.info('skipped [{}]: there are no variables requiring this stream'.format(stream['stream']))
    stream_validation.log_results(full_paths.log_directory("extract"))

    return stream_validation


def validate(path, stream, stash_codes, validation_result, filenames):
    """Simple validation based on checking correct number of files have
    been extracted, and stash codes comparison in the case of pp streams.

    In the case of ncdf files, it tests if they can be opened at all.

    Parameters
    ----------
    path:str
        directory path containing files to validate
    stream:dict
        stream attributes
    stash_codes : set
        a set of short stash codes appearing in filters
    validation_result: cdds.common.StreamValidationResult
        An object to hold results from the stream validation
    """
    validate_file_names(path, validation_result, filenames, stream["streamtype"])
    if stream["streamtype"] == "pp":
        validate_directory_pp(path, stash_codes, validation_result)
    elif stream["streamtype"] == "nc":
        validate_directory_netcdf(path, validation_result)


def validate_file_names(path, validation_result, filenames, file_type):
    """ Compare a list of expected files against the files on disk. If strict=True then
    validation will fail if there are additional files that are not expected.

    Parameters
    ----------
    path: str
        Path to the dataset.
    stream: dict
        Stream description dictionary.
    substreams: list
        List of expected substreams.
    validation_result: cdds.common.StreamValidationResult
        An object to hold results from the stream validation
    """
    logger = logging.getLogger(__name__)
    logger.info("Checking for missing files")

    actual_files = set([file for file in os.listdir(path) if file.endswith(file_type)])
    expected_files = set(filenames)

    validation_result.add_file_names(expected_files, actual_files)


def validate_directory_pp(path, stash_codes, validation_result):
    """
    Checks that PP files at provided location can be read and
    contain |STASH| codes consistent with the reference
    set given as a second argument.
    Returns overall validation status, error message(s),
    and a listof unreadable files (if present).

    Parameters
    ----------
    path: str
        Path pointing to the location of a set of PP files.
    stash_codes: set
        A set of unique |STASH| codes that the set of files will
        be validated against.
    validation_result: cdds.common.StreamValidationResult
        An object to hold results from the stream validation
    """
    logger = logging.getLogger(__name__)
    logger.info("Checking STASH fields")
    validate_stash_fields(path, stash_codes, validation_result)


def validate_directory_netcdf(path, validation_result):
    """
    Checks that |netCDF| files at provided location can be read.
    Returns overall validation status, error message(s), and a list
    of unreadable files (if present).

    Parameters
    ----------
    path: str
        Path pointing to the location of |netCDF| dataset.
    validation_result: cdds.common.StreamValidationResult
        An object to hold results from the stream validation
    """
    logger = logging.getLogger(__name__)
    logger.info("Checking netCDF files in \"{}\"".format(path))
    for root, _, files in os.walk(path):
        for datafile in sorted(files):
            error = validate_netcdf(os.path.join(root, datafile))
            if error is not None:
                validation_result.add_file_content_error(error)
