# (C) British Crown Copyright 2019-2021, Met Office.
# Please see LICENSE.rst for license details.
"""
Code to set up a batch script to run CDDS store on SPICE.
"""
import os
import sys

from hadsdk.config import FullPaths
from hadsdk.constants import (
    LOG_TIMESTAMP_FORMAT, REQUIRED_KEYS_FOR_PROC_DIRECTORY)
from hadsdk.request import read_request
from hadsdk.spice import submit_spice_job_script, write_spice_job_script

from transfer.constants import (
    SPICE_STORE_MEMORY, SPICE_STORE_QUEUE,
    SPICE_STORE_SCRIPT_NAME, SPICE_STORE_WALLTIME, STORE_COMMAND)


def run_store_spice_job(args):
    """
    Run script to store output netCDF files for this package
    in MASS on SPICE via a batch job.

    Parameters
    ----------
    args : :class:`argparse.Namespace` object
        The names of the command line arguments and their validated
        values.
    """
    request_path = args.request
    request = read_request(request_path, REQUIRED_KEYS_FOR_PROC_DIRECTORY)
    full_paths = FullPaths(args, request)
    job_script_filename = SPICE_STORE_SCRIPT_NAME
    job_script_path = os.path.join(
        full_paths.component_directory('archive'),
        job_script_filename)
    pass_through_args = ' '.join(sys.argv[1:])
    cmd_str = STORE_COMMAND.format(args=pass_through_args)

    substitutions = {
        'log_directory': full_paths.log_directory('archive'),
        'component': 'transfer',
        'wall_time': SPICE_STORE_WALLTIME,
        'queue': SPICE_STORE_QUEUE,
        'memory': SPICE_STORE_MEMORY,
        'env_setup': os.environ['CDDS_ENV_COMMAND'],
        'command': cmd_str,
    }
    write_spice_job_script(job_script_path, substitutions)
    submit_spice_job_script(job_script_path)
