# (C) British Crown Copyright 2017-2022, Met Office.
# Please see LICENSE.rst for license details.
"""
Routines to read MIP Convert config templates and write them out with
the appropriate parameters filled in.
"""
from datetime import datetime
import errno
import jinja2
import logging
import os
import re
import subprocess

from cdds.common.constants import CYLC_DATE_FORMAT, MIP_CONVERT_DATETIME_FORMAT


def calculate_mip_convert_run_bounds(start_point, cycle_duration,
                                     simulation_end, stream_time_overrides,
                                     offset=None, model_calendar='360day'):
    """
    Return a pair of datetime objects describing the  bounds for MIP
    Convert to run in this step.

    Parameters
    ----------
    start_point : str
        Starting point of this run.
    cycle_duration : str
        Duration of this cycle according to cylc.
    simulation_end : datetime
        Simulation end date for processing.
    stream_time_overrides: str
        Text describing the overrides to start and end dates for this
        stream. Taken from STREAM_TIME_OVERRIDES environment variable.
    offset : str, optional
        additional offset to be applied in the calculation, e.g. '-P1D'
    model_calendar : str, optional
        Calendar to be used

    Returns
    -------
    : tuple
        datetimes of the start and end for this step
    """
    logger = logging.getLogger(__name__)
    offsets = [cycle_duration]
    if offset is not None:
        offsets.append(offset)

    job_start_dt = datetime.strptime(start_point, CYLC_DATE_FORMAT)
    job_end_dt = rose_date(start_point, offsets, model_calendar)

    if job_end_dt > simulation_end:
        job_end_dt = simulation_end

    if stream_time_overrides != 'None':
        logger.info('Updating time range for STREAM_TIME_OVERRIDES')
        result = re.search(r'\[(\d+),\s*(\d+)\]',
                           stream_time_overrides)
        stream_start_year, stream_end_year = [int(i) for i in result.groups()]
        job_start_dt, job_end_dt = _update_run_bounds_for_stream_override(
            job_start_dt, job_end_dt, stream_start_year, stream_end_year)

    return job_start_dt, job_end_dt


def rose_date(ref_date, offsets, model_calendar):
    """
    Use the rose date command to obtain a date offset from a reference
    date.

    Parameters
    ----------
    ref_date : str
        Reference date
    offsets : list
        List of offsets, each of which should be an ISO time delta,
        e.g. "P1Y" for one year
    model_calendar : str
        Calendar to work with.

    Returns
    -------
    : datetime
        Resulting datetime object.
    """
    command = ['rose', 'date', ref_date,
               '--calendar={}'.format(model_calendar)]
    command += ['--offset={}'.format(i) for i in offsets]
    result = subprocess.check_output(command)
    return datetime.strptime(result.strip().decode(), CYLC_DATE_FORMAT)


def _update_run_bounds_for_stream_override(job_start_dt, job_end_dt,
                                           stream_start_year, stream_end_year,
                                           model_calendar='360day'):
    """
    Update the run bounds for this job to account for stream overrides

    Parameters
    ----------
    job_start_dt : datetime
        job start datetime
    job_end_dt : datetime
        job end datetime
    stream_start_year : int
        first year to process for this stream
    stream_end_year : int
        final year to process for this stream
    model_calendar : str
        calendar to be used

    Returns
    -------
    : tuple
         updated datetime objects for the start and end of this job,
    """
    assert model_calendar == '360day', ('Not able to deal with calendars '
                                        'other than 360day')
    stream_start_dt = datetime(stream_start_year, 1, 1)
    stream_end_dt = datetime(stream_end_year + 1, 1, 1)

    run_bounds = []
    if job_start_dt < stream_start_dt:
        run_bounds.append(stream_start_dt)
    else:
        run_bounds.append(job_start_dt)
    if job_end_dt > stream_end_dt:
        run_bounds.append(stream_end_dt)
    else:
        run_bounds.append(job_end_dt)

    return tuple(run_bounds)


def setup_cfg_file(input_dir, output_dir, mip_convert_config_dir, component,
                   start_time, end_time, timestamp, user_config_template_name,
                   cmor_log_filename_template):
    """
    Construct the mip_convert.cfg file from the templates. The
    resulting config file is written to the current directory.

    Parameters
    ----------
    input_dir : str
        Input directory for MIP Convert to load data from.
    output_dir : str
        Directory for MIP Convert to write data to.
    mip_convert_config_dir : str
        Directory to obtain MIP Convert config file templates from.
    component : str
        Model component. This is used to locate the correct MIP Convert
        config file template, e.g. if component is "ocean", then the
        template "mip_convert.ocean.cfg" in the MIP Convert config dir
        will be used.
    start_time : datetime
        Start date for this job step.
    end_time: datetime
        End date for this job step.
    timestamp : str
        Time stamp string to use in output file names.
    user_config_template_name: str
        The template for the name of the |user configuration file|.
    cmor_log_filename_template: str
        The template for the name of the cmor log file.
    Returns
    -------
    : bool
        True if there is work to do by this job step
    """
    logger = logging.getLogger(__name__)
    logger.info('Setting up mip_convert config file')
    logger.info('Calculating time range to use')

    if not os.path.exists(output_dir):
        logger.info('Creating output directory "{}"'.format(output_dir))
        if os.path.exists(os.path.dirname(output_dir)):
            try:
                os.makedirs(output_dir)
            except OSError as err:
                if err.errno == errno.EEXIST:
                    logger.warning(
                        'Output directory already exists: os.makedirs raised'
                        'OSError: "{}"\nContinuing.'.format(err))
                else:
                    logger.critical('Failed to create output directory. '
                                    'OSError: "{}"'.format(err.strerror))
                    raise
        else:
            raise RuntimeError('Could not create output dir "{}"'
                               ''.format(output_dir))

    component_dir = os.path.join(output_dir, component)
    if not os.path.isdir(component_dir):
        logger.info('Creating component directory "{}" within output '
                    'directory "{}"'.format(component, output_dir))
        try:
            os.makedirs(component_dir)
        except OSError as err:
            if err.errno == errno.EEXIST:
                logger.warning(
                    'Component directory already exists: os.makedirs raised'
                    'OSError: "{}"\nContinuing.'.format(err))
            else:
                logger.critical('Failed to create component directory. '
                                'OSError: "{}"'.format(err.strerror))
                raise

    jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(
        mip_convert_config_dir))
    template = jinja_env.get_template(
        user_config_template_name.format(component))
    interpolations = {
        'start_date': MIP_CONVERT_DATETIME_FORMAT.format(start_time),
        'end_date': MIP_CONVERT_DATETIME_FORMAT.format(end_time),
        'input_dir': input_dir,
        'output_dir': component_dir,
        'cmor_log': cmor_log_filename_template.format(timestamp)}
    logger.info('Interpolating:\n  ' +
                '\n  '.join(['{}: {}'.format(variable, value)
                             for variable, value in list(interpolations.items())]))
    output_config = template.render(**interpolations)

    output_file_name = user_config_template_name.format(timestamp)
    logger.info('Writing to {}'.format(os.path.join(os.getcwd(),
                                                    output_file_name)))
    with open(output_file_name, 'w') as filehandle:
        filehandle.write(output_config)
    logger.info('Config file written')
    return True
