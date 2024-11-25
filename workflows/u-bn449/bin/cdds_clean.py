#!/usr/bin/env python

import argparse
import logging
import os
import shutil
import subprocess

from cdds.common import configure_logger
from cdds.common.plugins.plugins import PluginStore
from cdds.common.request.request import read_request


CDDS_CLEAN_LOG_NAME = 'cdds_clean'
CRITICAL_MASS_LOCATIONS = [':/adhoc/projects/cdds/production']


def parse_args():
    parser = argparse.ArgumentParser(description='Clean up previous run of this package.')
    help_msg = 'The path to the root directory for this run through.'
    parser.add_argument('test_dir', help=help_msg, type=str)

    help_msg = 'The path to the request cfg file for this package.'
    parser.add_argument('request_cfg_path', help=help_msg, type=str)

    help_msg = 'The base cylc run name for the processing suites for this package.'
    parser.add_argument('--run-name', help=help_msg, type=str)
    parser.add_argument('--package', help='The name of the package being cleaned.', type=str)

    input_args = parser.parse_args()
    return input_args


def check_critical_mass_location(mass_dir):
    """
    Raise a RuntimeError if the supplied directory is part of a
    critical location
    """
    for location in CRITICAL_MASS_LOCATIONS:
        if location in mass_dir:
            msg = ('MASS location "{}" is part of a critical location ("{}"). Aborting.'
                   '').format(mass_dir, repr(CRITICAL_MASS_LOCATIONS))
            raise RuntimeError(msg)


def main():
    arguments = parse_args()
    
    cdds_suite_svn_url = os.environ['CDDS_SUITE_SVN_URL']
    cdds_branch = cdds_suite_svn_url.split('/')[-1]

    request_cfg_path = arguments.request_cfg_path
    request = read_request(request_cfg_path)
    request.conversion.cdds_workflow_branch = cdds_branch
    
    # Write request resolved all environment variables
    request.write(request_cfg_path)
    
    package_name = arguments.package    
    plugin = PluginStore.instance().get_plugin()

    configure_logger(CDDS_CLEAN_LOG_NAME, logging.INFO, False)
    suite_clean_args = ['rose', 'suite-clean', '--yes', '--name']
    suites_to_clean = [
        d1 for d1 in
        os.listdir(os.path.join(os.path.expandvars('$HOME'), 'cylc-run'))
        if arguments.run_name in d1]
    for run_name in suites_to_clean:
        subprocess.call(suite_clean_args + [run_name])

    logging.info('Deleting test directory {0}'.format(arguments.test_dir))
    try:
        shutil.rmtree(arguments.test_dir)
    except OSError:
        logging.info('Directory {0} does not exist.'.format(arguments.test_dir))

    data_directory = plugin.data_directory(request)
    logging.info('Deleting data directory {0}'.format(data_directory))
    try:
        shutil.rmtree(data_directory)
    except OSError:
        logging.info('Directory {0} does not exist.'.format(data_directory))
        
    proc_directory = plugin.proc_directory(request)
    logging.info('Deleting proc directory {0}'.format(proc_directory))
    try:
        shutil.rmtree(proc_directory)
    except OSError:
        logging.info('Directory {0} does not exist.'.format(proc_directory))

    logging.info('Cleaning MASS test archive directories.')
    # clean up directory for this specific package
    
    mass_package_location = os.path.join(request.data.output_mass_root, request.data.output_mass_suffix)
    # first, check that we are not trying to clean a production / critical
    # MASS location. If we are, raise an error.
    check_critical_mass_location(mass_package_location)

    moo_rm_cmd = ['moo', 'rm', '-R', mass_package_location]
    logging.info('Running moo delete command:\n{cmd}'.format(cmd=' '.join(moo_rm_cmd)))
    subprocess.call(moo_rm_cmd)


if __name__ == '__main__':
    main()
