# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.
import os
import tempfile
import shutil


def create_use_case_various_data(proc_dir_name, data_dir_name):
    test_dir = tempfile.mkdtemp(suffix='use_case_various')

    # data dir
    data_dir = os.path.join(test_dir, data_dir_name)
    os.makedirs(data_dir)
    tas_dir = os.path.join(data_dir,
                           'CMIP6/CMIP/UKESM1-0-LL/piControl/r1i1p1f2/cdds_nightly_test_piControl/output/ap5/Amon/tas')
    os.makedirs(tas_dir, exist_ok=True)
    touch_file(tas_dir, 'tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_196001-204912.nc')
    touch_file(tas_dir, 'tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_205001-214912.nc')
    touch_file(tas_dir, 'tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_215001-216912.nc')

    # proc dir
    proc_dir = os.path.join(test_dir, proc_dir_name)
    os.makedirs(proc_dir)

    prepare_dir = os.path.join(proc_dir,
                               'CMIP6/CMIP/UKESM1-0-LL_piControl_r1i1p1f2/cdds_nightly_test_piControl/prepare')
    os.makedirs(prepare_dir)

    qc_dir = os.path.join(proc_dir,
                          'CMIP6/CMIP/UKESM1-0-LL_piControl_r1i1p1f2/cdds_nightly_test_piControl/qualitycheck')
    os.makedirs(qc_dir)

    archive_dir = os.path.join(proc_dir,
                               'CMIP6/CMIP/UKESM1-0-LL_piControl_r1i1p1f2/cdds_nightly_test_piControl/archive')
    os.makedirs(archive_dir)

    current_dir = os.path.dirname(os.path.realpath(__file__))
    source_dir = os.path.join(current_dir, 'use_case_various')

    # copy request-file
    shutil.copy(
        os.path.join(source_dir, 'cdds_request_piControl_10096.json'),
        test_dir)

    shutil.copy(
        os.path.join(source_dir, 'CMIP6_CMIP_piControl_UKESM1-0-LL.json'),
        prepare_dir)

    shutil.copy(
        os.path.join(source_dir, 'approved_variables_2020-03-11T153255.txt'),
        qc_dir
    )
    return test_dir


def create_use_case10_data(proc_dir_name, data_dir_name):
    test_dir = tempfile.mkdtemp(suffix='use_case10')

    # data dir
    data_dir = os.path.join(test_dir, data_dir_name)
    os.makedirs(data_dir)
    tas_dir = os.path.join(data_dir,
                           'CMIP6/CMIP/UKESM1-0-LL/piControl/r1i1p1f2/cdds_nightly_test_piControl/output/ap5/Amon/tas')
    os.makedirs(tas_dir, exist_ok=True)
    touch_file(tas_dir, 'tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_190001-195912.nc')

    # proc dir
    proc_dir = os.path.join(test_dir, proc_dir_name)
    os.makedirs(proc_dir)

    prepare_dir = os.path.join(proc_dir,
                               'CMIP6/CMIP/UKESM1-0-LL_piControl_r1i1p1f2/cdds_nightly_test_piControl/prepare')
    os.makedirs(prepare_dir)

    qc_dir = os.path.join(proc_dir,
                          'CMIP6/CMIP/UKESM1-0-LL_piControl_r1i1p1f2/cdds_nightly_test_piControl/qualitycheck')
    os.makedirs(qc_dir)

    archive_dir = os.path.join(proc_dir,
                               'CMIP6/CMIP/UKESM1-0-LL_piControl_r1i1p1f2/cdds_nightly_test_piControl/archive')
    os.makedirs(archive_dir)

    current_dir = os.path.dirname(os.path.realpath(__file__))
    source_dir = os.path.join(current_dir, 'use_case_10')

    # copy request-file
    shutil.copy(
        os.path.join(source_dir, 'cdds_request_piControl_10096.json'),
        test_dir)

    shutil.copy(
        os.path.join(source_dir, 'CMIP6_CMIP_piControl_UKESM1-0-LL.json'),
        prepare_dir)

    shutil.copy(
        os.path.join(source_dir, 'approved_variables_2020-03-11T153255.txt'),
        qc_dir
    )
    return test_dir


def create_use_case9_data(proc_dir_name, data_dir_name):
    test_dir = tempfile.mkdtemp(suffix='use_case9')

    # data dir
    data_dir = os.path.join(test_dir, data_dir_name)
    os.makedirs(data_dir)
    tas_dir = os.path.join(data_dir,
                           'CMIP6/CMIP/UKESM1-0-LL/piControl/r1i1p1f2/cdds_nightly_test_piControl/output/ap5/Amon/tas')
    os.makedirs(tas_dir, exist_ok=True)
    touch_file(tas_dir, 'tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_190001-195912.nc')

    # proc dir
    proc_dir = os.path.join(test_dir, proc_dir_name)
    os.makedirs(proc_dir)

    prepare_dir = os.path.join(proc_dir,
                               'CMIP6/CMIP/UKESM1-0-LL_piControl_r1i1p1f2/cdds_nightly_test_piControl/prepare')
    os.makedirs(prepare_dir)

    qc_dir = os.path.join(proc_dir,
                          'CMIP6/CMIP/UKESM1-0-LL_piControl_r1i1p1f2/cdds_nightly_test_piControl/qualitycheck')
    os.makedirs(qc_dir)

    archive_dir = os.path.join(proc_dir,
                               'CMIP6/CMIP/UKESM1-0-LL_piControl_r1i1p1f2/cdds_nightly_test_piControl/archive')
    os.makedirs(archive_dir)

    current_dir = os.path.dirname(os.path.realpath(__file__))
    source_dir = os.path.join(current_dir, 'use_case_9')

    # copy request-file
    shutil.copy(
        os.path.join(source_dir, 'cdds_request_piControl_10096.json'),
        test_dir)

    shutil.copy(
        os.path.join(source_dir, 'CMIP6_CMIP_piControl_UKESM1-0-LL.json'),
        prepare_dir)

    shutil.copy(
        os.path.join(source_dir, 'approved_variables_2020-03-11T153255.txt'),
        qc_dir
    )
    return test_dir



def create_use_case3_data(proc_dir_name, data_dir_name):
    test_dir = tempfile.mkdtemp(suffix='use_case3')
    data_dir = os.path.join(test_dir, data_dir_name)
    os.makedirs(data_dir)

    tas_dir = os.path.join(data_dir,
                           'CMIP6/CMIP/UKESM1-0-LL/piControl/r1i1p1f2/cdds_nightly_test_piControl/output/ap5/Amon/tas')
    os.makedirs(tas_dir, exist_ok=True)
    nc_file_name = 'tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_215001-216912.nc'
    touch_file(tas_dir, nc_file_name)

    # proc_dir
    proc_dir = os.path.join(test_dir, proc_dir_name)
    os.makedirs(proc_dir)

    prepare_dir = os.path.join(proc_dir,
                               'CMIP6/CMIP/UKESM1-0-LL_piControl_r1i1p1f2/cdds_nightly_test_piControl/prepare')
    os.makedirs(prepare_dir)

    qc_dir = os.path.join(proc_dir,
                          'CMIP6/CMIP/UKESM1-0-LL_piControl_r1i1p1f2/cdds_nightly_test_piControl/qualitycheck')
    os.makedirs(qc_dir)

    archive_dir = os.path.join(proc_dir,
                               'CMIP6/CMIP/UKESM1-0-LL_piControl_r1i1p1f2/cdds_nightly_test_piControl/archive')
    os.makedirs(archive_dir)

    current_dir = os.path.dirname(os.path.realpath(__file__))
    source_dir = os.path.join(current_dir, 'use_case_3')

    # copy request-file
    shutil.copy(
        os.path.join(source_dir, 'cdds_request_piControl_10096.json'),
        test_dir)

    shutil.copy(
        os.path.join(source_dir, 'CMIP6_CMIP_piControl_UKESM1-0-LL.json'),
        prepare_dir)

    shutil.copy(
        os.path.join(source_dir, 'approved_variables_2020-03-11T153255.txt'),
        qc_dir
    )
    return test_dir


def create_use_case8_data(proc_dir_name, data_dir_name):
    test_dir = tempfile.mkdtemp(suffix='use_case8')

    # data dir
    data_dir = os.path.join(test_dir, data_dir_name)
    os.makedirs(data_dir)
    tas_dir = os.path.join(data_dir,
                           'CMIP6/CMIP/UKESM1-0-LL/piControl/r1i1p1f2/cdds_nightly_test_piControl/output/ap5/Amon/tas')
    os.makedirs(tas_dir, exist_ok=True)
    touch_file(tas_dir, 'tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_190001-195912.nc')

    # proc dir
    proc_dir = os.path.join(test_dir, proc_dir_name)
    os.makedirs(proc_dir)

    prepare_dir = os.path.join(proc_dir, 'CMIP6/CMIP/UKESM1-0-LL_piControl_r1i1p1f2/cdds_nightly_test_piControl/prepare')
    os.makedirs(prepare_dir)

    qc_dir = os.path.join(proc_dir, 'CMIP6/CMIP/UKESM1-0-LL_piControl_r1i1p1f2/cdds_nightly_test_piControl/qualitycheck')
    os.makedirs(qc_dir)

    archive_dir = os.path.join(proc_dir, 'CMIP6/CMIP/UKESM1-0-LL_piControl_r1i1p1f2/cdds_nightly_test_piControl/archive')
    os.makedirs(archive_dir)

    current_dir = os.path.dirname(os.path.realpath(__file__))
    source_dir = os.path.join(current_dir, 'use_case_8')

    # copy request-file
    shutil.copy(
        os.path.join(source_dir, 'cdds_request_piControl_10096.json'),
        test_dir)

    shutil.copy(
        os.path.join(source_dir, 'CMIP6_CMIP_piControl_UKESM1-0-LL.json'),
        prepare_dir)

    shutil.copy(
        os.path.join(source_dir, 'approved_variables_2020-03-11T153255.txt'),
        qc_dir
    )
    return test_dir


def touch_file(directory, filename):
    new_file = os.path.join(directory, filename)
    with open(new_file, 'w') as fh:
        pass
