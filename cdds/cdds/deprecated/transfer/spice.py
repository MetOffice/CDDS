# (C) British Crown Copyright 2019-2021, Met Office.
# Please see LICENSE.rst for license details.
"""
Code to set up a batch script to run CDDS Transfer on SPICE
"""
import os

from cdds.common.spice import submit_spice_job_script, write_spice_job_script
from hadsdk.config import CDDSConfigGeneral
from hadsdk.constants import REQUIRED_KEYS_FOR_PROC_DIRECTORY
from hadsdk.request import read_request

QUEUE = 'long'
TRANSFER_COMMAND = 'send_to_mass {arguments}'
WALLTIME = '2-00:00:00'  # Should be good enough for ~20TB.
MEMORY = '2G'


def run_transfer_spice_batch_job(request_path, root_config, arguments,
                                 log_dir):
    """
    Transfer processed data to MASS on SPICE via a batch job.

    Parameters
    ----------
    request_path : str
        The full path to the JSON file containing the information from
        the request.
    root_config : str
        The root path to the directory containing the CDDS
        configuration files.
    arguments: list of str
        Command line arguments used (all to be passed through to the
        batch job.
    log_dir: str
        The location to write logs to if specified at the command line,
        otherwise None.
    """
    request = read_request(request_path, REQUIRED_KEYS_FOR_PROC_DIRECTORY)
    general_config = CDDSConfigGeneral(root_config, request)

    job_script_filename = 'cdds_transfer_spice.sh'
    job_script = os.path.join(general_config.component_directory('archive'),
                              job_script_filename)

    # Ensure that the script knows the absolute path of the request file as
    # the working directory of the spice job may be different to the spice
    # wrapper.
    full_request_path = os.path.abspath(request_path)

    # Update correct argument as cannot rely on order.
    for i, argument in enumerate(arguments):
        if argument == request_path:
            arguments[i] = full_request_path

    substitutions = {
        'log_directory': log_dir,
        'component': 'transfer',
        'wall_time': WALLTIME,
        'queue': QUEUE,
        'memory': MEMORY,
        'env_setup': os.environ['CDDS_ENV_COMMAND'],
        'command': TRANSFER_COMMAND.format(arguments=' '.join(arguments))
    }
    write_spice_job_script(job_script, substitutions)
    submit_spice_job_script(job_script)
