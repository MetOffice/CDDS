# (C) British Crown Copyright 2018-2021, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
"""
Functional test for CDDS Transfer send_to_mass script
"""

import pytest
import os
import shutil
import sys
from unittest import mock
import unittest

from cdds.deprecated.transfer.command_line import main_send_to_mass

CONFIG = (
    """
[locations]
dataroot = .
procroot = /tmp/cdds/proc

[facetmaps]
# facet structure for root data directory
datamap = programme|project|model|experiment|realisation|package
# facet structure for root proc directory
procmap = programme|project|request|package

[transfer_facetmaps]
valid = date|experiment_id|grid|institution_id|mip|mip_era|variant_label|"""
    """model_id|table_id|variable|stream|package|output
atomic = mip|date|experiment_id|grid|institution_id|mip_era|variant_label"""
    """|model_id|table_id|variable|package
name = variable|table_id|model_id|experiment_id|variant_label|grid|[date]
dataset_id = mip_era|institution_id|model_id|experiment_id|table_id|"""
    """variant_label
local = mip_era|mip|model_id|experiment_id|variant_label|package
sublocal = stream|table_id|variable
mass = mip_era|institution_id|model_id|experiment_id|variant_label|table_id|"""
    """grid
pattern = variable|table_id

[transfer_mass]
top_dir = moose:/adhoc/projects/cdds/ETE5

[transfer_local]
base_dir = output
""")
REQUEST = """
{{
  "config_version": "0.5.1",
  "mip_era": "CMIP6",
  "institution_id": "MOHC",
  "mip": "{mip}",
  "model_id": "HadGEM3-GC31-LL",
  "experiment_id": "{experiment_id}",
  "package": "ETE5",
  "variant_label": "r3i1p1f1"
}}
"""
# TOPDIR = 'CMIP6/CMIP/HadGEM3-GC31-LL/piControl/r3i1p1f1/ETE5/output'
DUMMYDIR = ('CMIP6/{mip}/HadGEM3-GC31-LL/{experiment_id}/r3i1p1f1/ETE5/output/'
            'inm/SImon/siconc')
DUMMYFILES = [
    'siconc_SImon_HadGEM3-GC31-LL_{experiment_id}_r3i1p1f1_gn_189001-190012.nc',
    'siconc_SImon_HadGEM3-GC31-LL_{experiment_id}_r3i1p1f1_gn_185001-186912.nc',
    'siconc_SImon_HadGEM3-GC31-LL_{experiment_id}_r3i1p1f1_gn_187001-188912.nc']


class TestSendToMassFunctional(unittest.TestCase):

    def setUp(self):
        # Command line arguments
        self.request_file = 'request.json'
        config_dir = 'CMIP6/v0.5.1/general'
        config_file = os.path.join(config_dir, 'CMIP6.cfg')
        self.log_name_base = 'send_to_mass'
        self.log_datestamp = '2019-11-23T1432Z'
        self.log_filename = (
            '{0}_{1}.log'.format(self.log_name_base, self.log_datestamp))
        command = ('send_to_mass --simulate -l {log_name} -q {request}'
                   ' -c .'.format(request=self.request_file,
                                  log_name=self.log_name_base))
        sys.argv = command.split()

        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        with open(config_file, 'w') as config_handle:
            config_handle.write(CONFIG)
        # Set up files to be cleared out
        self.files_to_delete = [self.request_file, self.log_filename, config_file]
        self.directories_to_delete = [config_dir]

    def setup_for_experiment(self, mip, experiment_id):

        with open(self.request_file, 'w') as request_handle:
            request_handle.write(REQUEST.format(mip=mip, experiment_id=experiment_id))

        if ' ' in mip:
            dummydir = DUMMYDIR.format(mip=mip.split(' ')[0],
                                       experiment_id=experiment_id)
        else:
            dummydir = DUMMYDIR.format(mip=mip,
                                       experiment_id=experiment_id)
        dummyfiles = [i.format(experiment_id=experiment_id) for i in DUMMYFILES]

        topdir_elements = dummydir.split('/')
        for i in range(1, len(topdir_elements) + 1):
            self.directories_to_delete.insert(
                0, os.path.join(*topdir_elements[:i]))

        # create dummy directories and files
        if not os.path.isdir(dummydir):
            os.makedirs(dummydir)
        for filename in dummyfiles:
            full_path = os.path.join(dummydir, filename)
            with open(full_path, 'w') as _:
                pass
            self.files_to_delete.append(full_path)

    def tearDown(self):
        for filename in self.files_to_delete:
            if os.path.exists(filename):
                os.unlink(filename)
        for directory in self.directories_to_delete:
            if os.path.exists(directory):
                shutil.rmtree(directory)

    @pytest.mark.slow
    @mock.patch('cdds.common.get_log_datestamp')
    def test_simple_run_through(self, mock_log_datestamp):
        experiment_id = 'piControl'
        mip = 'CMIP'
        self.setup_for_experiment(mip, experiment_id)
        mock_log_datestamp.return_value = self.log_datestamp
        result = main_send_to_mass()
        self.assertEqual(result, 0)

    @pytest.mark.slow
    @mock.patch('cdds.common.get_log_datestamp')
    def test_simple_run_through_multi_activity_id(self, mock_log_datestamp):
        experiment_id = 'ssp370'
        mip = 'ScenarioMIP AerChemMIP'
        self.setup_for_experiment(mip, experiment_id)
        mock_log_datestamp.return_value = self.log_datestamp
        result = main_send_to_mass()
        self.assertEqual(result, 0)
