# (C) British Crown Copyright 2019-2024, Met Office.
# Please see LICENSE.rst for license details.
"""
Code to set up a batch script to run CDDS store on SPICE.
"""
import os
import sys

from cdds.archive.constants import (
    SPICE_STORE_MEMORY, SPICE_STORE_QUEUE,
    SPICE_STORE_SCRIPT_NAME, SPICE_STORE_WALLTIME, STORE_COMMAND)
from cdds.common.request.request import Request
from cdds.common.plugins.plugins import PluginStore
from cdds.common.cdds_files.cdds_directories import log_directory
from cdds.common.spice import submit_spice_job_script, write_spice_job_script


def run_store_spice_job(request: Request) -> None:
    """
    Run script to store output netCDF files for this package in MASS on SPICE via a batch job.

    :param request: Request configuration contains all necessary information to store netCDF files
    :type request: Request
    """
    plugin = PluginStore.instance().get_plugin()
    proc_directory = plugin.proc_directory(request)
    job_script_filename = SPICE_STORE_SCRIPT_NAME
    component_directory = os.path.join(proc_directory, 'archive')
    job_script_path = os.path.join(component_directory, job_script_filename)
    pass_through_args = ' '.join(sys.argv[1:])
    cmd_str = STORE_COMMAND.format(args=pass_through_args)

    substitutions = {
        'log_directory': log_directory(request, 'archive'),
        'component': 'transfer',
        'wall_time': SPICE_STORE_WALLTIME,
        'queue': SPICE_STORE_QUEUE,
        'memory': SPICE_STORE_MEMORY,
        'env_setup': os.environ['CDDS_ENV_COMMAND'],
        'command': cmd_str,
    }
    write_spice_job_script(job_script_path, substitutions)
    submit_spice_job_script(job_script_path)
