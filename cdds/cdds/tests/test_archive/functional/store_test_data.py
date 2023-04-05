# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.
import os
import tempfile
import shutil

APPROVED_VARIABLES_FILENAME = 'approved_variables_2020-03-11T153255.txt'
PREPARE_JSON_FILENAME = 'CMIP6_CMIP_piControl_UKESM1-0-LL.json'
REQUEST_JSON_FILENAME = 'cdds_request_piControl_10096.json'
ARCHIVE_DIR_PATH = 'CMIP6/CMIP/UKESM1-0-LL_piControl_r1i1p1f2/cdds_nightly_test_piControl/archive'
QC_DIR_PATH = 'CMIP6/CMIP/UKESM1-0-LL_piControl_r1i1p1f2/cdds_nightly_test_piControl/qualitycheck'
PREPARE_DIR_PATH = 'CMIP6/CMIP/UKESM1-0-LL_piControl_r1i1p1f2/cdds_nightly_test_piControl/prepare'
AMON_TAS_DIR_PATH = 'CMIP6/CMIP/UKESM1-0-LL/piControl/r1i1p1f2/cdds_nightly_test_piControl/output/ap5/Amon/tas'


def setup_basic_test_data(proc_dir_name, data_dir_name):
    test_dir = tempfile.mkdtemp(suffix='use_case_various')

    # create nc files for tests in data directory
    output_dir = os.path.join(test_dir, data_dir_name, AMON_TAS_DIR_PATH)
    os.makedirs(output_dir, exist_ok=True)
    _touch_file(output_dir, 'tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_196001-204912.nc')
    _touch_file(output_dir, 'tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_205001-214912.nc')
    _touch_file(output_dir, 'tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_215001-216912.nc')

    # create proc directory
    _setup_proc_dir(test_dir, proc_dir_name, output_dir)
    return test_dir


def setup_prepending_to_embargoed_test_data(proc_dir_name, data_dir_name):
    test_dir = tempfile.mkdtemp(suffix='use_case10')

    # create nc file for test in data directory
    output_dir = os.path.join(test_dir, data_dir_name, AMON_TAS_DIR_PATH)
    os.makedirs(output_dir, exist_ok=True)
    _touch_file(output_dir, 'tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_190001-195912.nc')

    # create proc directory
    _setup_proc_dir(test_dir, proc_dir_name, output_dir)
    return test_dir


def setup_prepending_test_data(proc_dir_name, data_dir_name):
    test_dir = tempfile.mkdtemp(suffix='use_case9')

    # create nc file for test in data directory
    output_dir = os.path.join(test_dir, data_dir_name, AMON_TAS_DIR_PATH)
    os.makedirs(output_dir, exist_ok=True)
    _touch_file(output_dir, 'tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_190001-195912.nc')

    # create proc directory
    _setup_proc_dir(test_dir, proc_dir_name, output_dir)
    return test_dir


def setup_extend_submitted_test_data(proc_dir_name, data_dir_name):
    test_dir = tempfile.mkdtemp(suffix='use_case3')

    # create nc file for test in data directory
    output_dir = os.path.join(test_dir, data_dir_name, AMON_TAS_DIR_PATH)
    os.makedirs(output_dir, exist_ok=True)
    nc_file_name = 'tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_215001-216912.nc'
    _touch_file(output_dir, nc_file_name)

    # create proc directory
    _setup_proc_dir(test_dir, proc_dir_name, output_dir)
    return test_dir


def _setup_proc_dir(test_dir, proc_dir_name, variable_output_dir):
    proc_dir = os.path.join(test_dir, proc_dir_name)

    # setup necessary proc directory structure
    prepare_dir = os.path.join(proc_dir, PREPARE_DIR_PATH)
    os.makedirs(prepare_dir)
    qc_dir = os.path.join(proc_dir, QC_DIR_PATH)
    os.makedirs(qc_dir)
    archive_dir = os.path.join(proc_dir, ARCHIVE_DIR_PATH)
    os.makedirs(archive_dir)

    # copy request json and prepare output json into corresponding proc folders
    current_dir = os.path.dirname(os.path.realpath(__file__))
    source_dir = os.path.join(current_dir, 'data')
    shutil.copy(os.path.join(source_dir, REQUEST_JSON_FILENAME), test_dir)
    shutil.copy(os.path.join(source_dir, PREPARE_JSON_FILENAME), prepare_dir)

    # create approved variables file
    _create_approved_variables_file(qc_dir, APPROVED_VARIABLES_FILENAME, 'Amon', 'tas', variable_output_dir)


def _touch_file(directory, filename):
    new_file = os.path.join(directory, filename)
    with open(new_file, 'w') as fh:
        pass


def _create_approved_variables_file(directory, filename, mip_table, variable, output_path):
    content = '{}/{};{}'.format(mip_table, variable, output_path)
    approved_variables_file = os.path.join(directory, filename)
    with open(approved_variables_file, 'w') as fh:
        fh.writelines([content])
