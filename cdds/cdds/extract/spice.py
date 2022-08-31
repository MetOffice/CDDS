# (C) British Crown Copyright 2018-2022, Met Office.
# Please see LICENSE.rst for license details.
"""
Code to set up a batch script to run CDDS Extract on SPICE
"""
from datetime import datetime
import os

from hadsdk.config import FullPaths
from hadsdk.constants import (
    LOG_TIMESTAMP_FORMAT, REQUIRED_KEYS_FOR_PROC_DIRECTORY)
from hadsdk.request import read_request
from cdds.common.spice import (submit_spice_job_script, write_spice_job_script)
from cdds.extract.constants import (QUEUE, EXTRACT_COMMAND, WALLTIME, MEMORY,
                                    LOGNAME, SPICE_SCRIPT_NAME)


def run_extract_spice_batch_job(args):
    """
    Extract the requested data from MASS on SPICE via a batch job.

    Parameters
    ----------
    args : :class:`argparse.Namespace` object
        The names of the command line arguments and their validated
        values.
    """
    request_path = args.request
    if args.streams is not None:
        streams = ' --streams {}'.format(" ".join(args.streams))
    else:
        streams = ''
    if args.simulation is True:
        simulation = ' --simulation '
    else:
        simulation = ''
    request = read_request(request_path, REQUIRED_KEYS_FOR_PROC_DIRECTORY)
    full_paths = FullPaths(args, request)

    job_script_filename = SPICE_SCRIPT_NAME
    job_script = os.path.join(full_paths.component_directory('extract'),
                              job_script_filename)
    substitutions = {
        'log_directory': full_paths.log_directory('extract'),
        'component': 'extract',
        'wall_time': WALLTIME,
        'queue': QUEUE,
        'memory': MEMORY,
        'env_setup': os.environ['CDDS_ENV_COMMAND'],
        'command': EXTRACT_COMMAND.format(
            request=request_path,
            log_name=args.log_name,
            root_proc_dir=args.root_proc_dir,
            root_data_dir=args.root_data_dir
        ) + streams + simulation
    }
    write_spice_job_script(job_script, substitutions)
    submit_spice_job_script(job_script)
