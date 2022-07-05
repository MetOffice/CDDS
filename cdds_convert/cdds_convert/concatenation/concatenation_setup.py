# (C) British Crown Copyright 2017-2021, Met Office.
# Please see LICENSE.rst for license details.
"""
CMOR netCDF file aggregation routines
"""
import cf_units
from configparser import ConfigParser
from datetime import datetime
import fnmatch
import logging
import netCDF4
try:
    import cftime as cft
except ImportError:
    import netcdftime as cft
import os
import re
import sqlite3

from common.cdds_plugins.plugins import PluginStore
from cdds_convert.constants import (CMOR_FILENAME_PATTERN,
                                    TASK_STATUS_NOT_STARTED)
from cdds_convert.exceptions import ArgumentError
from cdds_convert.organise_files import construct_expected_concat_config
from hadsdk.common import configure_logger
from hadsdk.constants import LOG_TIMESTAMP_FORMAT, TIME_UNIT


def organise_concatenations(reference_date, start_date, end_date,
                            reinitialisation_years, filenames, output_dir):
    """
    Using the supplied dates and reinitialisation period arrange the
    files into groups to be concatenated together and return a
    dictionary describing the work to do.

    Parameters
    ----------
    reference_date : datetime
        Reference date for working out chunking, i.e. the start of
        the simulation
    start_date : datetime
        Start date for processing. Any files which correspond to dates
        before this point will be ignored
    end_date : datetime
        End date for processing. Any files which correspond to dates
        after this point will be ignored
    reinitialisation_years : float
        The size in years of the time window covered by the data in a single
        output file from the concatenation task.
    filenames : list
        names of the files to process.
    output_dir : str
        location of the directory to write the output concatenated files to.

    Returns
    -------
    dict
        Relates each output file to the list of files that should be
        concatenated to create it.
    """
    reference_date_n = TIME_UNIT.date2num(reference_date)
    start_date_n = TIME_UNIT.date2num(start_date)
    end_date_n = TIME_UNIT.date2num(end_date)
    chunk_start = reference_date_n
    chunk_end = min(chunk_start + 360 * reinitialisation_years,
                    end_date_n)
    time_chunks = {(chunk_start, chunk_end): []}

    while chunk_end != end_date_n:
        chunk_start = chunk_end
        chunk_end = min(chunk_start + 360 * reinitialisation_years,
                        end_date_n)
        time_chunks[(chunk_start, chunk_end)] = []

    for filename in filenames:
        file_start_time, file_end_time = times_from_filename(filename)
        if file_end_time <= start_date_n or file_start_time >= end_date_n:
            continue
        for chunk in time_chunks:
            chunk_start, chunk_end = chunk
            # if the start of the file period falls in the chunk, then include
            # it in the chunk. This ensures that files that go across chunks
            # are still included in one period or the other
            if chunk_start <= file_start_time < chunk_end:
                time_chunks[chunk].append(filename)
                break

    # Obtain all facets of the file name except for the date range
    # (final facet)

    fname_components = os.path.basename(filenames[0]).split('_')
    base_filename = '_'.join(fname_components[:-1])
    var_name = fname_components[0]
    mip_table = fname_components[1]
    # Set output directory as the same location as the first input file
    base_dir = os.path.join(output_dir, mip_table, var_name)

    concatenation_work = {}

    # remove chunks with no files
    time_chunks = dict([(k1, v1) for k1, v1 in list(time_chunks.items()) if v1])

    for chunk_files in list(time_chunks.values()):
        chunk_files.sort()
        actual_chunk_start_time = chunk_files[0].split('_')[-1].split('-')[0]
        actual_chunk_end_time = chunk_files[-1].split('_')[-1].split('-')[1]
        # Check for climatology netcdf files and modify the extension appropriately.
        if '-clim.nc' in chunk_files[-1]:
            extension = '-clim.nc'
        else:
            extension = '.nc'
        actual_chunk_end_time = actual_chunk_end_time.replace('.nc', '')
        output_filename = '{0}_{1}-{2}{3}'.format(base_filename,
                                                  actual_chunk_start_time,
                                                  actual_chunk_end_time,
                                                  extension)
        output_path = os.path.join(base_dir, output_filename)
        if output_path in chunk_files:
            chunk_files.remove(output_path)
        concatenation_work[output_path] = chunk_files
    return concatenation_work


def list_cmor_files(location, pattern, mip_table=None, recursive=False):
    """
    Retrieve the list of input CMOR format files in location that match
    the supplied pattern.

    Parameters
    ----------
    location :  str
        location to search for files
    pattern : str
        glob to match files against
    mip_table : str
        The name of the mip table currently being processed
    recursive : bool, optional
        if True recursively search through supplied location

    Returns
    -------
    list
        filenames found
    """
    ncfiles = []
    if mip_table is None:
        location_to_search = location
    else:
        location_to_search = os.path.join(location, mip_table)

    for root, _, files in os.walk(location_to_search):
        for filename in fnmatch.filter(files, pattern):
            if re.match(CMOR_FILENAME_PATTERN, filename):
                ncfiles.append(os.path.join(root, filename))
        if not recursive:
            break
    return ncfiles


def write_concatenation_work_db(concatenation_work, output_file,
                                close_db=True):
    """
    Write the concatenation work information to a sqlite database file.

    Parameters
    ----------
    concatenation_work : dict
        Work to be done
    output_file : str
        File name to write to (".db" will be appended if not
        already in the file name).
    close_db : bool
        if True close the database, otherwise return the connection
        object (used for testing)

    Returns
    -------
    sqlite.Connection or None
        connection to sqlite database if close_db is False
    """
    logger = logging.getLogger(__name__)
    logger.info('Total number of concatenation tasks: {}'
                ''.format(len(concatenation_work)))

    # :memory: is a special file name used by sqlite to only create the
    # database in memory. Used here to permit testing.
    if not output_file.endswith('.db') and output_file != ':memory:':
        output_file += '.db'
    if output_file != ':memory:':
        if os.path.exists(output_file):
            logger.warning('Database "{}" already exists'.format(output_file))
            timestamp = datetime.utcnow().strftime(LOG_TIMESTAMP_FORMAT)
            output_file_renamed = '.'.join([output_file, timestamp])
            logger.warning('Renaming "{}" to "{}"'.format(
                output_file, output_file_renamed))
            try:
                os.rename(output_file, output_file_renamed)
            except OSError as err:
                msg = ('Could not rename concatenation database "{}": '
                       '"{}"').format(output_file, str(err))
                logger.exception(msg)
                raise

    logger.info('Writing concatenation task list to sqlite database "{}"'
                ''.format(output_file))
    conn = sqlite3.connect(output_file)
    cursor = conn.cursor()
    create_sql = ('CREATE TABLE concatenation_tasks '
                  '(output_file TEXT UNIQUE, variable TEXT, '
                  'input_files TEXT NOT NULL, candidate_file TEXT NOT NULL, '
                  'start_timestamp REAL, complete_timestamp REAL, '
                  'status TEXT)')
    cursor.execute(create_sql)
    insert_sql = ('INSERT INTO concatenation_tasks '
                  '(output_file, variable, input_files, candidate_file, '
                  'status) VALUES (?, ?, ?, ?, "{}")'
                  '').format(TASK_STATUS_NOT_STARTED)

    for result_file in sorted(concatenation_work):
        input_files = concatenation_work[result_file]
        # the candidate file is the temporary file that the concatenation
        # command will write to. When finished, the file will be moved to
        # the final output location specified by result file. If the ncrcat
        # comand fails, then we won't have a corrupted file in the output
        # directory, and there is less chance of the move command failing
        # or timing out.
        candidate_file = os.path.join(
            os.path.dirname(input_files[0]),
            os.path.splitext(os.path.basename(result_file))[0]
            + '_candidate.nc')
        variable = '/'.join(os.path.basename(result_file).split('_')[:2][::-1])
        values = [result_file, variable, ' '.join(input_files), candidate_file]
        cursor.execute(insert_sql, values)
    conn.commit()
    logger.info('Changes to database "{}" committed.'.format(output_file))

    if close_db:
        conn.close()
        return None
    else:
        return conn


def times_from_filename(filename, calendar='360_day'):
    """
    From a CMOR filename return the start and end dates from the last
    facet

    Parameters
    ----------
    filename : str
        name of the file
    calendar : str, optional
        calendar (not used yet)

    Returns
    -------
    tuple
        start date and end dates in units specified by TIME_UNITS
    """
    facets = filename.strip('.nc').split('_')
    tfacets = facets[-1].split('-')
    start = 'YYYY01010000'
    end = 'YYYY12300000'
    start = start.replace(start[:len(tfacets[0])], tfacets[0])
    end = end.replace(end[:len(tfacets[1])], tfacets[1])

    pattern = r'(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})'
    start_info = [int(i) for i in re.search(pattern, start).groups()]
    end_info = [int(i) for i in re.search(pattern, end).groups()]
    start_dt = cft.datetime(*start_info)
    end_dt = cft.datetime(*end_info)

    return TIME_UNIT.date2num(start_dt), TIME_UNIT.date2num(end_dt)


def get_reinitialisation_period(filename, model_id):
    """
    Use the shape of data in the file to obtain the reinitialisation
    period from the sizing file.

    Parameters
    ----------
    filename : str
        Name of the file to use for sizing
    model_id : str
        The |model identifier| for the data being processed in this package.

    Returns
    -------
    float
        Number of years of data to go in each file.

    Raises
    ------
    SizingError
        if the sizing info doesn't have the expected structure
    """
    logger = logging.getLogger(__name__)

    plugin = PluginStore.instance().get_plugin()
    model_params = plugin.models_parameters(model_id)

    frequency, shape_key = get_file_frequency_shape(filename)
    logger.info('Obtained frequency "{}" and shape key "{}" for file "{}"'.format(frequency, shape_key, filename))
    sizing_period = model_params.sizing_info(frequency, shape_key)
    logger.info('Reinitialisation period: {} years'.format(sizing_period))
    return sizing_period


def get_file_frequency_shape(filename):
    """
    Read a netcdf file and extract the frequency attribute and shape of
    the data variable (excluding the time axis).

    Parameters
    ----------
    filename : str
        Name of a file obtain shape from. Must begin with the variable
        name.

    Returns
    -------
    : str
        The frequency (as defined in the
        `CMIP6 Global Attributes document`_).
    : str
        Variable shape key of form "X-Y-Z" where X, Y, Z are integers
        describing the shape of the data variable. Note that time axes
        are not included in the shape key.
    """
    ncid = netCDF4.Dataset(filename)
    var_name = os.path.basename(filename).split('_')[0]
    dims = ncid.variables[var_name].dimensions
    spatial_shape = [len(ncid.dimensions[i]) for i in dims
                     if not i.startswith('time')]
    key = '-'.join([str(i) for i in spatial_shape])
    return ncid.frequency, key


def build_concatenation_work_dict(available_variables, config,
                                  reference_date, start_date, end_date,
                                  model_id):
    """
    Return a dictionary describing the concatenation work to be done.

    Parameters
    ----------
    available_variables : set
        Set of tuples of (MIP table, CMOR variable)
    config : dict
        Config dictionary
    reference_date : datetime
        Reference date for simulation
    start_date : datetime
        Start date for processing
    end_date: datetime
        End date for processing
    model_id: str
        The |model identifier| for this package.

    Returns
    -------
    dict
        Concatenation work
    """
    logger = logging.getLogger(__name__)
    all_concatenation_work = {}
    for mip_table, variable_name in available_variables:
        logger.info('MIP variable: {}/{}'.format(mip_table, variable_name))
        filename_pattern = '{}_{}_*'.format(variable_name, mip_table)
        input_files_dir = config['staging_location']

        input_filenames = list_cmor_files(input_files_dir,
                                          filename_pattern,
                                          mip_table=mip_table,
                                          recursive=config['recursive'])
        if len(input_filenames) == 1:
            logger.info('Found single file {}'.format(input_filenames[0]))
        else:
            logger.info('Found {} files ({} to {})'
                        ''.format(len(input_filenames), input_filenames[0], input_filenames[-1]))

        logger.info('Getting sizing information')
        reinitialisation_years = get_reinitialisation_period(
            input_filenames[0], model_id)
        output_dir = config['output_location']
        concatenation_work = organise_concatenations(reference_date,
                                                     start_date, end_date,
                                                     reinitialisation_years,
                                                     input_filenames,
                                                     output_dir)
        logger.info('Identified {} concatenation tasks for this variable'
                    ''.format(len(concatenation_work)))
        all_concatenation_work.update(concatenation_work)
    return all_concatenation_work


def load_concatenation_setup_config(config_file):
    """
    Read the supplied file and obtain the information needed to run
    the setup stage of the concatenation operation.

    Parameters
    ----------
    config_file : str
        The path of the configuration file to read.

    Returns
    -------
    dict
        arguments from the config file
    """
    parser = ConfigParser(delimiters='=')
    parser.optionxform = str
    parser.read(config_file)
    main_config = parser['main']
    expected_concat_config = construct_expected_concat_config()
    expected = {}
    for key, (func, default) in expected_concat_config.items():
        if key not in main_config:
            if default is not None:
                expected[key] = default
            else:
                raise ArgumentError('option "{}" must be specified in '
                                    'configuration file'.format(key))
        else:
            expected[key] = func(main_config[key])
    return expected


def concatenation_setup(config_file, log_file, append_log):
    """
    Setup up concatenation tasks for a particular cycle and stream of data.

    Parameters
    ----------
    config_file: str
        Path to the config file create by the organise files task
    log_file: str
        Path to the concatenate log file.
    append_log: Boolean
        True if the logger should append the message to an existing log file
        if it exists. If False, the logger will overwrite any existing file.

    """

    configure_logger(log_file, 0, append_log=append_log)
    logger = logging.getLogger(__name__)
    logger.info('Starting MIP Concatenate batch setup')
    config = load_concatenation_setup_config(config_file)
    logger.info('Input parameters:')
    for i in sorted(config):
        logger.info('  {} : {}'.format(i, config[i]))

    reference_date = cft.datetime(config['reference_year'], 1, 1)
    start_date = cft.datetime(config['start_year'], 1, 1)
    end_date = cft.datetime(config['end_year'] + 1, 1, 1)

    available_variables = set()
    for filename in list_cmor_files(config['staging_location'], '*',
                                    recursive=config['recursive']):
        variable_tuple = tuple(os.path.basename(filename).split('_')[1::-1])
        available_variables.add(variable_tuple)

    all_concatenation_work = build_concatenation_work_dict(
        available_variables, config, reference_date, start_date, end_date,
        config['model_id'])

    write_concatenation_work_db(all_concatenation_work, config['output_file'])
    logger.info('Concatenation setup complete. Exiting')
