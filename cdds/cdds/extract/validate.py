# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.

import logging
import os

from cdds.common import generate_datestamps_pp, generate_datestamps_nc
from cdds.common.plugins.plugins import PluginStore
from cdds.common.cdds_files.cdds_directories import component_directory, log_directory
from cdds.common.request.request import read_request
from cdds.extract.common import (
    configure_mappings, configure_variables,
    get_data_target, get_streamtype,
    validate_stash_fields, validate_netcdf,
    StreamValidationResult, build_mass_location,
)
from cdds.extract.constants import STREAMTYPE_PP, STREAMTYPE_NC
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
            filenames = mappings._generate_filenames_pp(datestamps)

        elif streamtype == STREAMTYPE_NC:
            datestamps, _ = generate_datestamps_nc(request.data.start_date, request.data.end_date, file_frequency)
            filenames = []
            substreams = list(mappings.filters.keys())
            for sub_stream in substreams:
                filenames += mappings._generate_filenames_nc(datestamps, sub_stream)

        validate(data_target, stream, stash_codes, stream_validation, filenames)
    else:
        logger.info('skipped [{}]: there are no variables requiring this stream'.format(stream))
    stream_validation.log_results(log_directory(request, "extract"))

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
    streamtype = get_streamtype(stream)
    validate_file_names(path, validation_result, filenames, streamtype)
    if streamtype == STREAMTYPE_PP:
        validate_directory_pp(path, stash_codes, validation_result)
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
