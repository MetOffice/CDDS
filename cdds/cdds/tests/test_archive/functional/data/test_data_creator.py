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


def create_use_case_various_data(proc_dir_name, data_dir_name):
    test_dir = tempfile.mkdtemp(suffix='use_case_various')

    # data dir
    data_dir = os.path.join(test_dir, data_dir_name)
    os.makedirs(data_dir)
    tas_dir = os.path.join(data_dir,
                           AMON_TAS_DIR_PATH)
    os.makedirs(tas_dir, exist_ok=True)
    touch_file(tas_dir, 'tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_196001-204912.nc')
    touch_file(tas_dir, 'tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_205001-214912.nc')
    touch_file(tas_dir, 'tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_215001-216912.nc')

    create_proc_dir(proc_dir_name, tas_dir, test_dir)
    return test_dir


def create_use_case10_data(proc_dir_name, data_dir_name):
    test_dir = tempfile.mkdtemp(suffix='use_case10')

    # data dir
    data_dir = os.path.join(test_dir, data_dir_name)
    os.makedirs(data_dir)
    tas_dir = os.path.join(data_dir,
                           AMON_TAS_DIR_PATH)
    os.makedirs(tas_dir, exist_ok=True)
    touch_file(tas_dir, 'tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_190001-195912.nc')

    create_proc_dir(proc_dir_name, tas_dir, test_dir)
    return test_dir


def create_use_case9_data(proc_dir_name, data_dir_name):
    test_dir = tempfile.mkdtemp(suffix='use_case9')

    # data dir
    data_dir = os.path.join(test_dir, data_dir_name)
    os.makedirs(data_dir)
    tas_dir = os.path.join(data_dir,
                           AMON_TAS_DIR_PATH)
    os.makedirs(tas_dir, exist_ok=True)
    touch_file(tas_dir, 'tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_190001-195912.nc')

    # proc dir
    create_proc_dir(proc_dir_name, tas_dir, test_dir)
    return test_dir


def create_proc_dir(proc_dir_name, tas_dir, test_dir):
    proc_dir = os.path.join(test_dir, proc_dir_name)
    os.makedirs(proc_dir)
    prepare_dir = os.path.join(proc_dir,
                               PREPARE_DIR_PATH)
    os.makedirs(prepare_dir)
    qc_dir = os.path.join(proc_dir,
                          QC_DIR_PATH)
    os.makedirs(qc_dir)
    archive_dir = os.path.join(proc_dir,
                               ARCHIVE_DIR_PATH)
    os.makedirs(archive_dir)
    current_dir = os.path.dirname(os.path.realpath(__file__))
    source_dir = os.path.join(current_dir, 'use_case_various')
    # copy request-file
    shutil.copy(
        os.path.join(source_dir, REQUEST_JSON_FILENAME),
        test_dir)
    shutil.copy(
        os.path.join(source_dir, PREPARE_JSON_FILENAME),
        prepare_dir)
    create_approved_variables_file(qc_dir, APPROVED_VARIABLES_FILENAME, 'Amon', 'tas', tas_dir)


def create_use_case3_data(proc_dir_name, data_dir_name):
    test_dir = tempfile.mkdtemp(suffix='use_case3')
    data_dir = os.path.join(test_dir, data_dir_name)
    os.makedirs(data_dir)

    tas_dir = os.path.join(data_dir,
                           AMON_TAS_DIR_PATH)
    os.makedirs(tas_dir, exist_ok=True)
    nc_file_name = 'tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_215001-216912.nc'
    touch_file(tas_dir, nc_file_name)

    create_proc_dir(proc_dir_name, tas_dir, test_dir)
    return test_dir


def touch_file(directory, filename):
    new_file = os.path.join(directory, filename)
    with open(new_file, 'w') as fh:
        pass


def create_approved_variables_file(directory, filename, mip_table, variable, output_dir):
    content = '{}/{};{}'.format(mip_table, variable, output_dir)
    approved_variables_file = os.path.join(directory, filename)
    with open(approved_variables_file, 'w') as fh:
        fh.writelines([content])
