# (C) British Crown Copyright 2019-2024, Met Office.
# Please see LICENSE.rst for license details.
"""
Module for the main function for the mip convert wrapper run in the suite.
"""
import logging
import os
import shutil
import sys
from datetime import datetime

from metomi.isodatetime.data import Calendar
from metomi.isodatetime.parsers import TimePointParser

from cdds.common import configure_logger
from cdds.common.constants import LOG_TIMESTAMP_FORMAT
from cdds.convert.constants import FILEPATH_METOFFICE
from cdds.convert.exceptions import WrapperEnvironmentError, WrapperMissingFilesError
from cdds.convert.mip_convert_wrapper.actions import (check_disk_usage, manage_critical_issues, manage_logs,
                                                      report_disk_usage, run_mip_convert)
from cdds.convert.mip_convert_wrapper.common import print_env
from cdds.convert.mip_convert_wrapper.constants import (USER_CONFIG_TEMPLATE_NAME, CMOR_LOG_FILENAME_TEMPLATE,
                                                        MIP_CONVERT_LOG_BASE_NAME, RUN_MIP_CONVERT_LOG_NAME)
from cdds.convert.mip_convert_wrapper.config_updater import calculate_mip_convert_run_bounds, setup_cfg_file
from cdds.convert.mip_convert_wrapper.file_management import copy_to_staging_dir, get_paths, link_data


def run_mip_convert_wrapper(arguments):
    """
    Retrieve the required parameters from environment variables, set up
    the mip_convert.cfg config file and run mip_convert.
    """
    exit_code = 0
    configure_logger(RUN_MIP_CONVERT_LOG_NAME, 0, append_log=False)
    logger = logging.getLogger(__name__)
    logger.info('Starting MIP Convert Wrapper.')

    # Log basic info
    logger.info('MIP convert wrapper starting')
    timestamp = datetime.now().strftime(LOG_TIMESTAMP_FORMAT)
    logger.info('Using timestamp "{}"'.format(timestamp))
    logger.info('Python executable: {}'.format(sys.executable))

    try:
        # Collect required environment variables
        max_temp_space_in_mb = int(os.environ['ALLOCATED_TMPDIR_SPACE_IN_MB'])
        component = os.environ['COMPONENT']
        cycle_duration = os.environ['CYCLE_DURATION']
        cylc_task_name = os.environ['CYLC_TASK_NAME']
        cylc_task_try = os.environ['CYLC_TASK_TRY_NUMBER']
        cylc_task_work_dir = os.environ['CYLC_TASK_WORK_DIR']
        cylc_task_cycle_point = os.environ['CYLC_TASK_CYCLE_POINT']
        dummy_run = os.environ['DUMMY_RUN'] == 'TRUE'
        simulation_end_date = os.environ['END_DATE']
        input_dir = os.environ['INPUT_DIR']
        mip_convert_config_dir = os.environ['MIP_CONVERT_CONFIG_DIR']
        cdds_convert_proc_dir = os.environ['CDDS_CONVERT_PROC_DIR']
        output_dir = os.environ['OUTPUT_DIR']
        stream = os.environ['STREAM']
        substream = os.environ['SUBSTREAM']
        suite_name = os.environ['SUITE_NAME']
        staging_dir = os.environ.get('STAGING_DIR', '')
        model_id = os.environ['MODEL_ID']
        calendar = os.environ['CALENDAR']
    except KeyError as ke1:
        err_msg = 'Expected environment variable {var} not found.'
        err_msg = err_msg.format(var=ke1)
        raise WrapperEnvironmentError(err_msg)

    logger.info('Setting Calendar: {}'.format(calendar))
    Calendar.default().set_mode(calendar)

    # Calculate start and end dates for this step
    # Final date is the 1st of January in the year after final_year (the final
    # year to be processed).
    simulation_end = TimePointParser().parse(simulation_end_date)
    start_date, end_date = calculate_mip_convert_run_bounds(cylc_task_cycle_point, cycle_duration, simulation_end)

    # Identify whether there is any work to be done in this job step.
    job_days = (end_date - start_date).days
    if job_days < 0:
        logger.warning('Job end date before start date\n'
                       'start date: {}\n'
                       'end date: {}\n'.format(start_date, end_date))
    if job_days <= 0:
        logger.info('No work for this job step. Exiting with code 0')
        return exit_code

    if staging_dir:
        input_staging_dir = os.path.join(staging_dir, 'input')
        work_dir = input_staging_dir
        output_staging_dir = os.path.join(staging_dir, 'output')
        mip_convert_output_dir = output_staging_dir
        logger.info('Running mip convert using staging directory:\n{0}\n'
                    ''.format(staging_dir))
    else:
        work_dir = cylc_task_work_dir
        mip_convert_output_dir = output_dir
        logger.info('Running mip convert using symlinking in work '
                    'directory:\n{0}\n'.format(work_dir))

    try:
        filepath_type = os.environ['FILEPATHSTYPE']   # ARCHER or METOFFICE
    except KeyError:
        filepath_type = FILEPATH_METOFFICE

    (expected_files,
     old_input_dir,
     new_input_dir) = get_paths(suite_name,
                                model_id,
                                stream,
                                substream,
                                start_date,
                                end_date,
                                input_dir,
                                work_dir,
                                filepath_type=filepath_type
                                )
    if staging_dir:
        num_files_processed = copy_to_staging_dir(expected_files,
                                                  old_input_dir,
                                                  new_input_dir,
                                                  )
        # Check the current disk usage of $TMPDIR and throw an exception if
        # usage is already exceeding the $TMPDIR allocation.
        check_disk_usage(staging_dir, max_temp_space_in_mb)
    else:
        # Set up symlinks to the data
        try:
            num_files_processed, new_input_dir = link_data(expected_files,
                                                           old_input_dir,
                                                           new_input_dir,
                                                           )
        except Exception as error:
            logger.critical('link_data failed with error: "{}"'.format(error))
            logger.info(print_env())
            raise error

    # If nothing linked then log a critical failure and exit
    if num_files_processed == 0:
        err_msg = 'No files processed for this job step, but work is expected.'
        raise WrapperMissingFilesError(err_msg)

    # Write out config file
    try:
        setup_cfg_file(work_dir,
                       mip_convert_output_dir,
                       mip_convert_config_dir,
                       component,
                       start_date,
                       end_date,
                       timestamp,
                       USER_CONFIG_TEMPLATE_NAME,
                       CMOR_LOG_FILENAME_TEMPLATE,
                       )
    except Exception as error:
        logger.critical('Setup_cfg_file failed with error: "{}"'.format(error))
        logger.info(print_env())
        raise error

    mip_convert_log = '{0}_{1}.log'.format(MIP_CONVERT_LOG_BASE_NAME,
                                           timestamp)
    # Run mip convert
    exit_code = run_mip_convert(stream, dummy_run, timestamp,
                                USER_CONFIG_TEMPLATE_NAME,
                                MIP_CONVERT_LOG_BASE_NAME,
                                arguments.mip_era,
                                arguments.external_plugin,
                                arguments.external_plugin_location,
                                arguments.relaxed_cmor)

    # If exit code is 2 then MIP Convert has run, but hasn't been able to do
    # everything asked of it. The CDDS approach to this is to continue on
    # but log the failure in a critical issues log.
    if exit_code == 2:
        exit_code = manage_critical_issues(
            exit_code, cdds_convert_proc_dir, mip_convert_log,
            fields_to_log=[cylc_task_name, cylc_task_cycle_point,
                           cylc_task_try])

    # move file from staging directory to output directory
    if staging_dir:
        # report the amount of space used in the staging directory
        report_disk_usage(staging_dir)
        check_disk_usage(staging_dir, max_temp_space_in_mb)
        component_dir_list = os.listdir(output_staging_dir)
        for dir1 in component_dir_list:
            full_comp_dir_path = os.path.join(output_staging_dir, dir1)
            out_comp_dir_path = os.path.join(output_dir, dir1)
            if os.path.isdir(out_comp_dir_path):
                logger.info('deleting old directory output directory: {0}'
                            ''.format(out_comp_dir_path))
                shutil.rmtree(out_comp_dir_path)
            logger.info('copying component directory from {src} to {dest}'
                        ''.format(src=full_comp_dir_path,
                                  dest=out_comp_dir_path))
            shutil.copytree(full_comp_dir_path,
                            out_comp_dir_path)

    # Tidy up the log files even if this task fails.
    manage_logs(stream, component, cdds_convert_proc_dir,
                cylc_task_cycle_point)
    return exit_code
