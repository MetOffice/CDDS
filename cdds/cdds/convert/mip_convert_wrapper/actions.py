# (C) British Crown Copyright 2017-2025, Met Office.
# Please see LICENSE.md for license details.
"""
Routines to perform actions such as running mip_convert or managing the
log files
"""
import glob
import logging
import os
import shutil
import subprocess

from cdds.common.constants import CDDS_DEFAULT_DIRECTORY_PERMISSIONS
from cdds.convert.exceptions import MipConvertWrapperDiskUsageError
from cdds.convert.mip_convert_wrapper.common import print_env


def copy_logs(mip_convert_log, cmor_log_file, target_dir):
    """
    Copy MIP convert and CMOR log files to given target directory.

    :param mip_convert_log: Path to MIP convert log file
    :type mip_convert_log: str
    :param cmor_log_file: Path to CMOR log file
    :type cmor_log_file: str
    :param target_dir: Path to target directory
    :type target_dir: str
    """
    target_mip_convert_log = os.path.join(target_dir, os.path.basename(mip_convert_log))
    target_cmor_log = os.path.join(target_dir, os.path.basename(cmor_log_file))
    shutil.copyfile(mip_convert_log, target_mip_convert_log)
    shutil.copyfile(cmor_log_file, target_cmor_log)


def manage_logs(stream, component, mip_convert_config_dir,
                cylc_task_cycle_point):
    """
    Create the logs directories under
    mip_convert_config_dir/log/stream_component/date/ and move logs to
    them.

    Parameters
    ----------
    stream : str
        Stream to manage logs for.
    component : str
        Component to manage logs for.
    mip_convert_config_dir : str
        Directory containing MIP Convert config files to be managed.
    cylc_task_cycle_point : str
        Cylc task cycle point (format YYYYMMDDTHHMMZ) to use as date
        component of log directory structure.
    """
    logger = logging.getLogger(__name__)
    logger.info('Managing logs')
    # suffix is a variable used in the suite.rc that is a useful shorthand.
    suffix = '_'.join([stream, component])
    dir_stem = os.path.join(mip_convert_config_dir, 'log',
                            suffix, cylc_task_cycle_point)
    work = [('cmor_logs', 'cmor*.log'),
            ('mip_convert_cfgs', 'mip_convert.*.cfg'),
            ('mip_convert_logs', 'mip_convert*.log')]
    for dir_name, file_pattern in work:
        destination = os.path.join(dir_stem, dir_name)
        if os.path.exists(destination):
            if os.path.isdir(destination):
                logger.info('Log directory "{}" already exists.'
                            ''.format(destination))
            else:
                raise RuntimeError('Expected "{}" to be a directory.'
                                   ''.format(destination))
        else:
            logger.info('Making log directory "{}"'.format(destination))
            os.makedirs(destination, CDDS_DEFAULT_DIRECTORY_PERMISSIONS)
            os.chmod(destination, CDDS_DEFAULT_DIRECTORY_PERMISSIONS)
        # Note that we are already in the working directory where MIP Convert
        # is run and as such all the log files are in the current working
        # directory.
        files_to_archive = glob.glob(file_pattern)
        for file_to_archive in files_to_archive:
            return_code = subprocess.call(['gzip', file_to_archive])
            if return_code > 0:
                logger.warning('Failed to gzip "{}".'.format(file_to_archive))
            else:
                file_to_archive = '{}.gz'.format(file_to_archive)
            dest_file_name = os.path.join(destination, file_to_archive)
            if os.path.exists(dest_file_name):
                continue
            logger.info('Archiving "{}" to "{}.gz"'.format(files_to_archive,
                                                           dest_file_name))
            shutil.copy(file_to_archive, dest_file_name)


def run_mip_convert(stream, dummy_run, timestamp, user_config_template_name,
                    mip_convert_log, plugin_id, external_plugin, external_plugin_path, relaxed_cmor):
    """
    Run MIP Convert, or perform dummy_run if specified, and update logs.

    Parameters
    ----------
    stream : str
        Stream to be processed
    dummy_run : bool
        Print environment rather than run MIP Convert. Useful for
        development and debugging.
    timestamp : str
        timestamp to use in log and config file names.
    user_config_template_name: str
        The template for the name of the |user configuration file|.
    mip_convert_log: str
        The file name of the mip convert log for this task.
    plugin_id: str
        Plugin id that will be considered during MIP convert.
    external_plugin: str
        Module path to the external plugin if some is provided.
    external_plugin_path: str
        Path to the external plugin location if some is provided.

    Returns
    -------
    int
        Return code of the mip_convert process.
    """
    mip_convert_cfg = user_config_template_name.format(timestamp)

    logger = logging.getLogger(__name__)
    logger.info('Running mip_convert')
    logger.info('Working directory: {}'.format(os.getcwd()))
    logger.info('Writing to mip_convert log file: {}'.format(mip_convert_log))

    plugin_option = '--external_plugin {}'.format(external_plugin) if external_plugin else ''
    plugin_path_option = '--external_plugin_location {}'.format(external_plugin_path) if external_plugin_path else ''
    relaxed_cmor_option = '--relaxed_cmor' if relaxed_cmor else ''

    cmd = ('/usr/bin/time -v mip_convert {cfg_file} -a -s {stream} '
           '-l {log_name} --datestamp {datestamp} --plugin_id {plugin_id} {plugin_option} {plugin_path_option} '
           '{relaxed_cmor_option}'
           ''.format(cfg_file=mip_convert_cfg, stream=stream,
                     log_name=mip_convert_log, datestamp=timestamp,
                     plugin_id=plugin_id, plugin_option=plugin_option,
                     plugin_path_option=plugin_path_option, relaxed_cmor_option=relaxed_cmor_option))
    logger.info('Command to execute: {}'.format(cmd))
    if dummy_run:
        logger.info('Performing dummy run')
        logger.info(print_env())
        return 0

    logger.info('Launching subprocess')
    mip_convert_proc = subprocess.Popen(cmd.split(), env=os.environ.copy(),
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        universal_newlines=True)
    output, error = mip_convert_proc.communicate()
    return_code = mip_convert_proc.returncode
    logger.info('============ STDOUT ============')
    logger.info(output)
    logger.info('========== STDOUT END ==========')
    logger.info('============ STDERR ============')
    logger.info(error)
    logger.info('========== STDERR END ==========')
    if return_code != 0:
        logger.critical('Command failed with return code {}'
                        ''.format(return_code))
    return return_code


def get_disk_usage_in_mb(staging_dir):
    """
    Get the disk usage in MB of the specified directory.
    Parameters
    ----------
    staging_dir: str
        The path to the directory to get the disk usage for.

    Returns
    -------
    : int
        The disk usage in MB.
    """
    du_cmd = 'du -s --block-size=1M {staging_dir}'.format(
        staging_dir=staging_dir)
    du_output = subprocess.check_output(du_cmd, shell=True, universal_newlines=True)
    du_in_mb = int(du_output.split('\t')[0])
    return du_in_mb


def check_disk_usage(staging_dir, max_space_in_mb):
    """
    Check the current disk usage of the data in staging_dir, and raises an
    exception if exceeds the allocated space specified by max_space.

    Parameters
    ----------
    staging_dir: str
        The path to the directory to get the disk usage for.
    max_space_in_mb: int
        The space allocated to the staging_dir directory in MB.

    Raises
    ------
    MipConvertWrapperDiskUsageError
        Raised if the current amount of data stored in staging_dir exceeds
        max space.
    """
    logger = logging.getLogger(__name__)
    du_in_mb = get_disk_usage_in_mb(staging_dir)
    if du_in_mb > max_space_in_mb:
        msg1 = ('Usage of $TMPDIR measured at {0}MB, which exceeds '
                'allocation of {1}MB'.format(du_in_mb, max_space_in_mb))
        logger.error(msg1)
        raise MipConvertWrapperDiskUsageError(msg1)
    logger.info('mip_convert resource - {0} usage within allocation'.format(
        staging_dir))


def report_disk_usage(staging_dir):
    """
    Report current disk usage of the data in staging_dir to the log.

    Parameters
    ----------
    staging_dir: str
        The path to the directory to get the disk usage for.
    """
    logger = logging.getLogger(__name__)
    logger.info('mip_convert resource reporting:')
    du_in_mb = get_disk_usage_in_mb(staging_dir)
    du_msg = (
        'du command shows the following $TMPDIR usage at '
        '{0:.2f}MB'.format(du_in_mb))
    logger.info(du_msg)


def manage_critical_issues(mip_convert_config_dir, mip_convert_log,
                           fields_to_log=None):
    """
    Identify critical issues logged by MIP Convert and copy them to a
    central log file so that users can keep an eye on them.

    Parameters
    ----------
    mip_convert_config_dir : str
        Name of directory containing MIP Convert config files.
    mip_convert_log: str
        The file name of the mip convert log for this task.
    fields_to_log : list, optional
        Information to insert into the critical issues file along
        with the CRITICAL log messages.

    Returns
    -------
    : int
        Exit code to be ultimately returned by sys.exit.
    """
    if fields_to_log is None:
        fields_to_log = []
    logger = logging.getLogger(__name__)
    critical_issues_file = os.path.join(mip_convert_config_dir, 'log',
                                        'critical_issues.log')
    logger.debug('Searching "{}" for CRITICAL messages'
                 ''.format(mip_convert_log))
    critical_issues_list = []
    with open(mip_convert_log) as log_file_handle:
        for line in log_file_handle.readlines():
            if 'CRITICAL' in line:
                critical_issues_list.append(line.strip())
    # Just in case an error code is raised for a separate reason;
    if not critical_issues_list:
        logger.debug('No CRITICAL messages found')
    else:

        with open(critical_issues_file, 'a') as critical_issues_log:
            for issue in critical_issues_list:
                line = '|'.join(fields_to_log + [mip_convert_log, issue])
                critical_issues_log.write(line + '\n')
        logger.info('Wrote "{}" critical issues to log file "{}"'.format(
            len(critical_issues_list), critical_issues_file))
