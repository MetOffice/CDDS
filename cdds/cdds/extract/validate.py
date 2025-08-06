# (C) British Crown Copyright 2023-2025, Met Office.
# Please see LICENSE.md for license details.

import logging
import os

from metomi.isodatetime.data import Calendar

from cdds.common import generate_datestamps_nc, generate_datestamps_pp
from cdds.common.cdds_files.cdds_directories import component_directory, log_directory
from cdds.common.plugins.plugins import PluginStore
from cdds.common.request.request import read_request
from cdds.extract.common import (
    FileContentError,
    StashError,
    StreamValidationResult,
    build_mass_location,
    configure_mappings,
    configure_variables,
    get_data_target,
    get_stash_from_pp,
    get_streamtype,
    validate_netcdf,
)
from cdds.extract.constants import STREAMTYPE_NC, STREAMTYPE_PP
from cdds.extract.filters import Filters


def validate_streams(streams, args):
    logger = logging.getLogger(__name__)

    request = read_request(args.request)
    plugin = PluginStore.instance().get_plugin()
    model_params = plugin.models_parameters(request.metadata.model_id)
    stream_file_info = model_params.stream_file_info()
    stream = streams[0]

    var_list = configure_variables(os.path.join(component_directory(request, "prepare"),
                                                plugin.requested_variables_list_filename(request)))

    # configure mappings for each variables
    mappings = Filters(plugin.proc_directory(request), var_list)
    mappings.set_mappings(request)
    mapping_status = configure_mappings(mappings)

    if request.data.mass_ensemble_member:
        mappings.ensemble_member_id = request.data.mass_ensemble_member
        file_type = get_streamtype(stream)
        mappings.source = build_mass_location(request.data.mass_data_class,
                                              request.data.model_workflow_id,
                                              stream,
                                              file_type,
                                              request.data.mass_ensemble_member)
    else:
        mappings.ensemble_member_id = None
    mappings.stream = stream

    # generate expected filenames
    file_frequency = stream_file_info.file_frequencies[stream].frequency

    stream_validation = StreamValidationResult(stream)

    if stream in mapping_status:
        data_target = get_data_target(os.path.join(plugin.data_directory(request), 'input'),
                                      request.data.model_workflow_id, stream)
        streamtype = get_streamtype(stream)
        _, _, _, stash_codes = (mappings.format_filter(streamtype, stream))
        if streamtype == STREAMTYPE_PP:
            datestamps, _ = generate_datestamps_pp(request.data.start_date, request.data.end_date, file_frequency)
            filenames = mappings.generate_filenames_pp(datestamps)

        elif streamtype == STREAMTYPE_NC:
            datestamps, _ = generate_datestamps_nc(request.data.start_date, request.data.end_date, file_frequency)
            filenames = []
            substreams = list(mappings.filters.keys())
            for sub_stream in substreams:
                filenames += mappings.generate_filenames_nc(datestamps, sub_stream)

        validate(data_target, stream, stash_codes, stream_validation, filenames, file_frequency)
    else:
        logger.info('skipped [{}]: there are no variables requiring this stream'.format(stream))
    stream_validation.log_results(log_directory(request, "extract"))

    return stream_validation


def validate(path, stream, stash_codes, validation_result, filenames, file_frequency):
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
    streamtype = get_streamtype(stream)
    validate_file_names(path, validation_result, filenames, streamtype)
    if streamtype == STREAMTYPE_PP:
        logger = logging.getLogger(__name__)
        logger.info("Checking STASH fields")
        stash_in_file = get_stash_fields(path, validation_result)
        check_expected_stash(stash_in_file, validation_result, path, stash_codes)
        check_consistent_stash(stash_in_file, validation_result, path, file_frequency)
    elif streamtype == STREAMTYPE_NC:
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
    logger.info("Checking for missing and unexpected files")

    actual_files = set([file for file in os.listdir(path) if file.endswith(file_type)])
    expected_files = set(filenames)

    validation_result.add_file_names(expected_files, actual_files)


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


def get_stash_fields(path: str, validation_result: StreamValidationResult) -> dict[str, dict[int, int]]:
    """ Validates if pp files in a given location contain all required
    stash codes,

    :param path: Path of interest.
    :type path: str
    :param validation_result: Holds errors and results of validation.
    :type validation_result: StreamValidationResult
    :return:
    :rtype: dict[in, int]
    """
    stash_in_file = {}
    pp_files = [file for file in os.listdir(path) if file.endswith('.pp')]

    if pp_files:
        for pp_file in sorted(pp_files):
            stash = get_stash_from_pp(os.path.join(path, pp_file))
            if stash is None:
                validation_result.add_file_content_error(
                    FileContentError(os.path.join(path, pp_file), "unreadable file"))
            stash_in_file[pp_file] = stash
    return stash_in_file


def check_expected_stash(
    stash_in_file: dict[str, dict[int, int]],
    validation_result: StreamValidationResult,
    path: str,
    expected_stash: set[int],
):
    """ Checks that all the expected stash codes are found in each file.

    :param stash_in_file: Stash entries in files.
    :type stash_in_file: dict[str, dict[int, int]]
    :param validation_result: Validation results for a given stream.
    :type validation_result: StreamValidationResult
    :param path: Path to files.
    :type path: str
    :param expected_stash: The set of expected stash codes.
    :type expected_stash: set[int]
    """

    for file, stash in stash_in_file.items():
        if expected_stash.difference(set(stash.keys())):
            stash_diff = expected_stash.difference(set(stash.keys()))
            if stash_diff:
                error = StashError(os.path.join(path, file), "STASH errors")
                for diff in stash_diff:
                    error.add_stash_error(diff)
                validation_result.add_file_content_error(error)


def check_consistent_stash(
    stash_in_file: dict,
    validation_result: StreamValidationResult,
    path: str,
    file_frequency: str
):
    """ Checks that the number of stash entries is consistent across all files.

    :param stash_in_file: Stash entries in files.
    :type stash_in_file: dict
    :param validation_result: Validation results for a given stream.
    :type validation_result: StreamValidationResult
    :param path: Path to files.
    :type path: str
    """

    if Calendar.default().mode == "gregorian" and file_frequency in ["monthly", "seasonal"]:
        logger = logging.getLogger(__name__)
        logger.info("Skipping stash consistency check due to gregorian calendar.")
        return None

    referencedict = ()
    for file, stash in stash_in_file.items():
        if referencedict == ():
            referencedict: tuple[str, dict] = (file, stash)
        elif referencedict[1] != stash:
            error = StashError(os.path.join(path, file), "STASH errors relative to reference values")
            for key, value in referencedict[1].items():
                if key not in stash or stash[key] != value:
                    error.add_stash_error(key)
            for key in stash:
                if key not in referencedict[1]:
                    error.add_stash_error(key)
            validation_result.add_file_content_error(error)
