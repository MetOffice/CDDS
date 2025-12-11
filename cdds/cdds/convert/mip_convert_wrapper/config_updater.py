# (C) British Crown Copyright 2017-2025, Met Office.
# Please see LICENSE.md for license details.
"""Routines to read MIP Convert config templates and write them out with
the appropriate parameters filled in.
"""
import errno
import logging
import os
from typing import Tuple

import jinja2
from metomi.isodatetime.data import TimePoint
from metomi.isodatetime.parsers import DurationParser, TimePointParser

from cdds.common.constants import CYLC_DATE_FORMAT, MIP_CONVERT_DATETIME_FORMAT


def calculate_mip_convert_run_bounds(
        start_point: str, cycle_duration: str, simulation_end: TimePoint) -> Tuple[TimePoint, TimePoint]:
    """Return a pair of datetime objects describing the  bounds for MIP
    Convert to run in this step.

    Parameters
    ----------
    start_point : str
        Starting point of this run.
    cycle_duration : str
        Duration of this cycle according to cylc.
    simulation_end : TimePoint
        Simulation end date for processing.

    Returns
    -------
    tuple
        of TimePoint represent the start and end for this step
    """

    job_start_dt = TimePointParser().parse(start_point, dump_format=CYLC_DATE_FORMAT)
    job_end_dt = TimePointParser().parse(start_point) + DurationParser().parse(cycle_duration)

    if job_end_dt > simulation_end:
        job_end_dt = simulation_end

    return job_start_dt, job_end_dt


def setup_cfg_file(input_dir, output_dir, mip_convert_config_dir, component,
                   start_time, end_time, timestamp, user_config_template_name,
                   cmor_log_file):
    """Construct the mip_convert.cfg file from the templates. The
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
    start_time : TimePoint
        Start date for this job step.
    end_time: TimePoint
        End date for this job step.
    timestamp : str
        Time stamp string to use in output file names.
    user_config_template_name: str
        The template for the name of the |user configuration file|.
    cmor_log_file: str
        The cmor log file.
    Returns
    -------
    bool
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
        'cmor_log': cmor_log_file}
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
