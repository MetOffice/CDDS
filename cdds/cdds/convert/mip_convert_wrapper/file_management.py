# (C) British Crown Copyright 2017-2025, Met Office.
# Please see LICENSE.md for license details.
"""
Routines for generating links to data files in order to restrict the
volume of data that MIP Convert can see and attempt to read
"""

import glob
import logging
import os
import re
import shutil

from metomi.isodatetime.data import TimePoint

from cdds.common.plugins.plugins import PluginStore
from cdds.convert.constants import (FILEPATH_JASMIN, FILEPATH_METOFFICE,
                                    NUM_FILE_COPY_ATTEMPTS,
                                    STREAMS_FILES_REGEX)
from cdds.convert.mip_convert_wrapper.file_processors import (
    parse_atmos_daily_filename, parse_atmos_monthly_filename,
    parse_atmos_submonthly_filename, parse_ocean_seaice_filename,
    parse_atmos_hourly_filename)


def filter_streams(file_list, stream):
    """
    Filters provided file list based on selected stream.

    Parameters
    ----------
    file_list: list
        List of filepaths.
    stream: str
        Stream name.

    Returns
    -------
    : list
        Filtered list of filepaths.
    """
    if stream[0] == 'a':
        # atmospheric stream
        pattern = r'[a-z0-9]{5}(\-[ripf0-9]+)?a\.' + stream[1:3] + r'[a-z0-9\_]+\.pp$'
    elif stream in ['inm', 'ind']:
        pattern = r'cice_[a-z0-9]{5}(\-[ripf0-9]+)?i_1' + stream[-1] + r'_[a-zA-Z0-9\-_]+\.nc$'
    elif stream in ['onm', 'ond']:
        pattern = r'(nemo|medusa)_[a-z0-9]{5}(\-[ripf0-9]+)?o_1' + stream[-1] + r'_[a-zA-Z0-9\-_]+\.nc$'
    p = re.compile(pattern)
    return [file_name for file_name in file_list if p.search(file_name)]


def construct_processors_dict():
    """Generate a dictionary containing processors for each stream type"""
    filename_processors = {
        'ap': parse_atmos_monthly_filename,
        'ap_submonthly': parse_atmos_submonthly_filename,
        'ap_daily': parse_atmos_daily_filename,
        'ap_hourly': parse_atmos_hourly_filename,
        'in': parse_ocean_seaice_filename,
        'on': parse_ocean_seaice_filename,
    }
    return filename_processors


def get_paths(suite_name, model_id, stream, substream, start_date: TimePoint, end_date: TimePoint, input_dir,
              work_dir, filepath_type=FILEPATH_METOFFICE):
    """
    Creates a list of paths to current input directory, directory for symlinks
    or copies of the files, and a list of the files name thatwill be input
    to this batch of processing.

    Parameters
    ----------
    suite_name: str
        The name of the suite that the ran the model
    model_id: str
        ID of the considered model
    stream: str
        The model output stream to be processed
    substream: str
        The name of the substream to be processed, if specified. If empty
        string, all variables in the stream will be processed.
    start_date: TimePoint
        The start date of the data to be processed
    end_date: TimePoint
        The end date of the data to be processed
    input_dir: str
        The base directory of the current file directory
            (this excludes the suite name and the stream name)
    work_dir: str
        The base firectory for copying or symlinking
    filepath_type: str
        Type of the file organisation.

    Returns
    -------
    Tuple of (expected_files, old_input_location, new_input_location)
    expected_files - list of expected input files for this processing
    old_input_location - The current location of the input files
    new_input_location - the location where the files will be copied to or
                         symlink will be created.

    """
    # Identify files that are to be expected
    old_input_location = os.path.join(input_dir, suite_name, stream)

    stream_prefix = find_stream_prefix(model_id, stream)
    new_input_location = os.path.join(work_dir, suite_name, stream)
    period_start = start_date
    period_end = end_date

    stream_file_regex = STREAMS_FILES_REGEX[stream_prefix]
    file_pattern = re.compile(stream_file_regex)
    filename_processor = construct_processors_dict()[stream_prefix]

    # lists to hold Jasmin path params
    all_files = []
    cycle_dirs = []

    if filepath_type == FILEPATH_JASMIN:
        for cycle_dir in os.listdir(old_input_location):
            all_new_files = os.listdir(os.path.join(old_input_location,
                                                    cycle_dir))
            new_files = filter_streams(all_new_files, stream)
            all_files.extend(new_files)
            cycle_dirs.extend([cycle_dir for fi in new_files])

        # get rid of anything that's not pp or nc
        all_files = [fi for fi in all_files if (fi.endswith(".pp")
                                                or fi.endswith(".nc"))]
    elif filepath_type == FILEPATH_METOFFICE:
        all_files = os.listdir(old_input_location)

    file_list = _assemble_file_dicts(all_files,
                                     cycle_dirs, filename_processor,
                                     stream, substream, file_pattern,
                                     period_start, period_end, model_id)
    return (file_list,
            old_input_location,
            new_input_location)


def find_stream_prefix(model_id: str, stream: str) -> str:
    """
    Finds the stream prefix for a particular stream ('ap', 'in', 'on', 'ap_submonthly, ap_daily, ap_hourly)

    :param input_location: Model ID that stream prefix should be found
    :type input_location: str
    :param stream: Stream for that prefix should be found
    :type stream: str
    :return: Prefix of the given stream
    :rtype: str
    """
    stream_prefix = stream[:2]  # `ap`, `in` or `on`
    if stream_prefix not in ['ap', 'in', 'on']:
        raise RuntimeError('Stream "{}" not recognised'.format(stream))

    if stream_prefix == 'ap':
        stream_prefix = _ap_stream_prefix(model_id, stream)
    return stream_prefix


def _ap_stream_prefix(model_id: str, stream: str) -> str:
    """
    Returns the right ap related prefix by checking if the stream frequency
    (ap, ap_submonthly, ap_daily, ap_hourly).

    :param model_id: Model ID that streams should be checked
    :type model_id: str
    :param stream: Stream that should be checked
    :type stream: str
    :return: The right ap related prefix
    :rtype: str
    """
    plugin = PluginStore.instance().get_plugin()
    stream_file_info = plugin.models_parameters(model_id).stream_file_info()
    frequency = stream_file_info.file_frequencies[stream].frequency

    if frequency in ['daily', 'quarterly']:
        return 'ap_daily'

    if frequency == '10 day':
        return 'ap_submonthly'

    if frequency == 'hourly':
        return 'ap_hourly'

    return 'ap'


def _assemble_file_dicts(all_files, cycle_dirs, filename_processor,
                         stream, substream, file_pattern,
                         period_start: TimePoint, period_end: TimePoint, model_id):
    """Assemble file dictionaries.

    Parameters
    ----------
    all_files : list
        List of all files to be processed.
    cycle_dirs : list
        List of directories organised by time cycles.
    filename_processor : function
        Filename parser.
    stream : str
        Stream name
    substream : str
        Substream name
    file_pattern : str
        Filename pattern matching the stream type
    period_start : TimePoint
        Beginning of the processed time chunk
    period_end : TimePoint
        End of the processed time chunk
    model_id: str
        ID of the considered model

    Returns
    -------
    : list
        Reorganised list of files.
    """
    file_list = []

    if not cycle_dirs:
        for stream_fname in all_files:
            try:
                file_dict = filename_processor(stream_fname, file_pattern)
                file_in_substream = (substream == '' or substream in file_dict['filename'])
                if (file_in_substream and
                        (period_start <= file_dict['start'] <= period_end
                         or period_start <= file_dict['end'] <= period_end)):
                    file_list += [file_dict]

            # TODO cleanup junk files
            # files called e.g. bi909a.p618500101.pp
            except AttributeError:
                pass
    else:
        for stream_fname, cycle_fname in zip(all_files, cycle_dirs):
            try:
                file_dict = filename_processor(stream_fname, stream, file_pattern, model_id)
                file_in_substream = (substream == '' or substream in file_dict['filename'])
                if (file_in_substream and
                        (period_start <= file_dict['start'] <= period_end or
                         period_start <= file_dict['end'] <= period_end)):
                    file_dict["cycle"] = cycle_fname
                    file_list += [file_dict]

            # TODO cleanup junk files
            # files called e.g. bi909a.p618500101.pp
            except AttributeError:
                pass
    return file_list


def copy_to_staging_dir(expected_files,
                        old_input_location,
                        new_input_location,
                        ):
    """
    Copy data from old_input_location to new_input_location. These values
    should be constructed using the get_paths function in this module.

    Parameters
    ----------
    expected_files : list
        List of expected files conversion.
    old_input_location : str
        Location of input files.
    new_input_location : str
        Location to copy input files to.

    Returns
    -------
    : int
        Number of files copied.

    Raises
    ------
    RuntimeError
        If a file cannot be copied in ``NUM_FILE_COPY_ATTEMPTS`` attempts.
    """

    logger = logging.getLogger(__name__)

    # make new directory
    logger.info('Setting up staging directory:\n {dir}\n'
                ''.format(dir=new_input_location))
    if not os.path.exists(new_input_location):
        logger.info('Creating "{}"'.format(new_input_location))
        os.makedirs(new_input_location)
    process_count = 0
    # perform copies
    for file_dict in expected_files:
        filename = file_dict['filename']
        full_path_src = os.path.join(old_input_location, filename)
        full_path_dest = os.path.join(new_input_location, filename)
        logger.info('copying file from {src} to {dest}'
                    ''.format(src=full_path_src,
                              dest=full_path_dest))
        # shutil.copy is not 100% reliable
        failure_count = 0
        # try multiple times
        for i in range(NUM_FILE_COPY_ATTEMPTS):
            try:
                shutil.copy(full_path_src, full_path_dest)
                process_count += 1
                # escape if successful
                break
            except IOError as err:
                # If attempt unsuccessful increment failure count and warn
                failure_count += 1
                logger.warn(
                    'Unable to copy file {} (attempt {} of {}): {}'.format(
                        full_path_src, i + 1, NUM_FILE_COPY_ATTEMPTS, err))
        # Fail if none of the attempts are successful
        if failure_count == NUM_FILE_COPY_ATTEMPTS:
            msg = ('Failed to copy file {} in {} attempts. Aborting.'
                   '').format(full_path_src, NUM_FILE_COPY_ATTEMPTS)
            logger.critical(msg)
            raise RuntimeError(msg)

    return process_count


def link_data(expected_files,
              old_input_location,
              new_input_location,
              ):
    """
    Identify data to be used and set up soft links only to the files
    that need to be read for this particular job step.

    Parameters
    ----------
    expected_files : list
        List of expected files conversion.
    old_input_location : str
        Location of input files.
    new_input_location : str
        Location to copy input files to.

    Returns
    -------
    : int
        Number of source files found.
    : str
        Location where symlinks have been created.
    """
    logger = logging.getLogger(__name__)

    # Set up the symlink directory
    _setup_symlink_directory(new_input_location)
    # Identify files to link to and create links
    num_links_created = _create_symlinks(expected_files,
                                         old_input_location,
                                         new_input_location,
                                         )
    return num_links_created, new_input_location


def _setup_symlink_directory(new_input_location):
    """
    Create or empty the directory for the symlinks to be created and
    return its location.

    Parameters
    ----------
    new_input_location : path to directory to create symlinks in

    Returns
    -------
    : str
        Name of the directory that has been created.
    """
    logger = logging.getLogger(__name__)
    logger.info('Setting up symlink directory "{}"'.format(new_input_location))
    if not os.path.exists(new_input_location):
        logger.info('Creating "{}"'.format(new_input_location))
        os.makedirs(new_input_location)
    else:
        logger.info('Symlinks directory "{}" already exists. Clearing '
                    'symlinks'.format(new_input_location))
        for filename in glob.glob(os.path.join(new_input_location, '*')):
            if os.path.islink(filename):
                os.unlink(filename)


def _create_symlinks(expected_files,
                     old_input_location,
                     new_input_location,
                     ):
    """
    Create the symlinks required for MIP Convert to run this task.

    Parameters
    ----------
    expected_files : list
        A list of the names of files expected for this task.
    old_input_location : str
        The location of the input filest the symlinks point to.
    new_input_location : str
        The location to use for the symlinks.

    Returns
    -------
    : int
        The number of links created
    """
    logger = logging.getLogger(__name__)
    logger.info('Looking for files in "{}"'.format(old_input_location))
    num_links_created = 0
    for file_dict in expected_files:
        filename = file_dict['filename']
        if "cycle" in file_dict:
            cycle = file_dict['cycle']
            full_path_filename = os.path.join(old_input_location,
                                              cycle, filename)
        else:
            full_path_filename = os.path.join(old_input_location, filename)
        full_path_link = os.path.join(new_input_location, filename)
        # If there is a pre-existing link in the new_input_location then
        # remove it.
        if os.path.exists(full_path_link):
            logger.info('Removing existing symlink "{}"'
                        ''.format(full_path_link))
            os.remove(full_path_link)
        # create link if the file exists
        if os.path.exists(full_path_filename):
            msg1 = 'linking from {file} to {link}'.format(
                file=full_path_filename, link=full_path_link)
            logger.debug(msg1)

            os.symlink(full_path_filename, full_path_link)
            num_links_created += 1
        else:
            logger.warning('Could not create symlink for "{}" to "{}" ("{}"): '
                           'file not found.'.format(file_dict['start'],
                                                    file_dict['end'],
                                                    filename))
    logger.info('Symlinked to {} files'.format(num_links_created))
    return num_links_created
