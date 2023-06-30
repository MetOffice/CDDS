# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.

import logging
import os

from cdds.common import generate_datestamps
from cdds.common.constants import REQUIRED_KEYS_FOR_PROC_DIRECTORY
from cdds.common.plugins.plugins import PluginStore
from cdds.common.plugins.streams import StreamAttributes
from cdds.common.request import read_request
from cdds.extract.common import (
    configure_mappings, configure_variables,
    file_count, get_data_target, get_streams,
    validate_stash_fields, validate_netcdf,
    StreamValidationResult
)
from cdds.extract.filters import Filters
from cdds.deprecated.config import FullPaths


def validate_streams(streams, args):
    logger = logging.getLogger(__name__)

    request = read_request(args.request, REQUIRED_KEYS_FOR_PROC_DIRECTORY)
    full_paths = FullPaths(args, request)
    model_id = request.model_id
    model_params = PluginStore.instance().get_plugin().models_parameters(model_id)
    stream_file_info = model_params.stream_file_info()

    var_list = configure_variables(os.path.join(full_paths.component_directory("prepare"),
                                                full_paths.requested_variables_list_filename))

    # configure mappings for each variables
    mappings = Filters(full_paths.proc_directory, var_list)
    mappings.set_mappings(args.mip_table_dir, request)
    mapping_status = configure_mappings(mappings)
    
    # generate expected filenames
    start, end = request.run_bounds.split()
    start, end = "".join(start.split("-")[:3]), "".join(end.split("-")[:3])
    datestamps, _ = generate_datestamps(start, end, file_frequency = stream_file_info.file_frequencies["ap6"].frequency)
    if request.mass_ensemble_member:
        ensemble_member = request.mass_ensemble_member
    else:
        ensemble_member = None
    mappings.ensemble_member_id = ensemble_member
    mappings.stream = streams[0]
    filenames = mappings._generate_filenames(datestamps)

    stream_details = get_streams(request.streaminfo, request.suite_id, streams)
    if not stream_details:
        logger.info('Command line stream selection {[]} not found in the request file'.format(', '.join(streams)))
    # we're no longer looping through multiple streams
    stream = stream_details[0]
    stream_validation = StreamValidationResult(stream['stream'])

    if stream['stream'] in mapping_status:
        data_target = get_data_target(full_paths.input_data_directory, stream)
        _, _, _, stash_codes = (mappings.format_filter(stream['streamtype'], stream['stream']))
        substreams = list(mappings.filters.keys())
        validate(data_target, stream, stash_codes, substreams, stream_file_info, stream_validation, filenames)
    else:
        logger.info('skipped [{}]: there are no variables requiring this stream'.format(stream['stream']))
    stream_validation.log_results(full_paths.log_directory("extract"))
    return stream_validation


def validate(path, stream, stash_codes, substreams, stream_file_info, validation_result, filenames):
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
    substreams: list
        list of substreams
    validation_result: cdds.common.StreamValidationResult
        An object to hold results from the stream validation
    """
    if stream["streamtype"] == "pp":
        validate_file_count_pp(path, validation_result, filenames)
        validate_directory_pp(path, stash_codes, validation_result)
    elif stream["streamtype"] == "nc":
        validate_file_count(path, stream, substreams, stream_file_info, validation_result)
        validate_directory_netcdf(path, validation_result)


def validate_file_count(path, stream, substreams, stream_file_info, validation_result):
    """
    Checks number of files present at a given location and
    validates it against values expected for a given stream
    and substream.

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
    # num files check
    logger.info("Checking file count")
    # count files of specific type in directory
    extension = ".{}".format(stream["streamtype"])
    actual = file_count(path, extension)
    # ocean resolution
    stream_attribute = StreamAttributes(stream["stream"], stream["start_date"], stream["end_date"])
    expected = stream_file_info.calculate_expected_number_of_files(stream_attribute, substreams)
    validation_result.add_file_counts(expected, actual)

def validate_file_count_pp(path, validation_result, filenames):
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
    logger.info("Checking file count")

    actual_files = set(os.listdir(path))
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
