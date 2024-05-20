# (C) British Crown Copyright 2018-2023, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
# pylint: disable = no-member
"""
Tests for :mod:`command_line.py`.
"""
import os
import tempfile
import unittest.mock

import pytest

from cdds.common.io import write_json
from cdds.common.plugins.plugins import PluginStore
from cdds.common.plugins.plugin_loader import load_plugin
from cdds.common.plugins.grid import GridType
from cdds.common.plugins.cmip6.cmip6_grid import Cmip6GridLabel
from cdds.common.request.request import read_request
from cdds.common import set_checksum
from cdds import __version__
from cdds.common.constants import TIME_UNIT_DESCRIPTION, COMMENT_FORMAT
from cdds.configure.command_line import main
from cdds.configure.constants import HEADER_TEMPLATE


# @pytest.mark.slow
class TestMain(unittest.TestCase):
    """
    Tests for :func:`main` in :mod:`command_line.py`.
    """

    def setUp(self):
        self.maxDiff = None
        load_plugin()
        self.user_config_template_name = 'mip_convert.cfg.atmos-native'
        self.user_config_file_header = COMMENT_FORMAT.format(
            HEADER_TEMPLATE.format(__version__))
        self.mip_era = 'CMIP6'
        self.temp_dir = tempfile.mkdtemp()
        self.requested_variables_list_path = os.path.join(self.temp_dir, 'CMIP6_list.json')
        current_dir = os.path.dirname(os.path.realpath(__file__))
        test_request_path = os.path.join(current_dir, '..', 'test_common', 'test_request', 'data', 'test_request.cfg')
        self.request = read_request(test_request_path)
        self.request.misc.use_proc_dir = False
        _, self.request_path = tempfile.mkstemp(prefix='request')
        self.request.write(self.request_path)

        self.root_proc_directory = os.path.join(self.temp_dir, 'proc_dir')
        self.output_dir_for_ucf = os.path.join(self.temp_dir, 'random_directory_name')
        self.log_dir = os.path.join(self.output_dir_for_ucf, 'log')
        self.log_name = 'test_main'
        self.log_datestamp = '2019-11-23T1432'
        self.log_path = ''  # to be constructed later
        # Request:
        self.branch_date_in_child = '1960-01-01T00:00:00'
        self.branch_date_in_parent = '1960-01-01T00:00:00'
        self.branch_method = 'standard'
        self.calendar = '360_day'
        self.base_date = '1850-01-01T00:00:00'
        self.create_subdirectories = '0'
        self.deflate_level = '2'
        self.experiment_id = 'piControl'
        self.institution_id = 'MOHC'
        self.CMOR_license = ('CMIP6 model data produced by the Met Office Hadley Centre is licensed under a '
                             'Creative Commons Attribution-ShareAlike 4.0 '
                             'International License (https://creativecommons.org/licenses). '
                             'Consult https://pcmdi.llnl.gov/CMIP6/TermsOfUse for terms of use governing CMIP6 output, '
                             'including citation requirements and proper acknowledgment. Further information about '
                             'this data, including some limitations, can be found via the further_info_url (recorded '
                             'as a global attribute in this file) and at https://ukesm.ac.uk/cmip6. The data '
                             'producers and data providers make no warranty, either express or implied, '
                             'including, but not limited to, warranties of merchantability and fitness for a particular'
                             ' purpose. All liabilities arising from the supply of the information (including any '
                             'liability arising in negligence) are excluded to the fullest extent permitted by law.')
        self.mip = 'CMIP'
        self.mip_era = 'CMIP6'
        # MIP tables now needed by configure to confirm that tables used exist
        self.mip_table_dir = os.path.join(os.environ['CDDS_ETC'], 'mip_tables/CMIP6/01.00.29')
        self.model_id = 'UKESM1-0-LL'
        # Add ancil files and replacement coordinates file:
        self.model_output_dir = '{{ input_dir }}'
        self.netcdf_file_action = 'CMOR_REPLACE_4'
        self.cmor_log = '{{ cmor_log }}'
        self.model_type = 'AOGCM BGC AER CHEM'
        self.output_dir = '{{ output_dir }}'
        self.package = 'configure_functional_test'
        self.parent_base_date = '1850-01-01T00:00:00'
        self.parent_experiment_id = 'piControl-spinup'
        self.parent_mip_era = 'CMIP6'
        self.parent_model_id = 'UKESM1-0-LL'
        self.parent_time_units = TIME_UNIT_DESCRIPTION
        self.parent_variant_label = 'r1i1p1f2'
        self.run_bounds = '{{ start_date }} {{ end_date }}'
        self.shuffle = 'True'
        self.sites_file = '/home/h03/cdds/etc/cfmip2/cfmip2-sites-orog.txt'
        self.sub_experiment_id = 'none'
        self.suite_id = 'u-aw310'
        self.variant_label = 'r1i1p1f2'
        # User config:
        self.ancil_files = ('/project/cdds/ancil/UKESM1-0-LL/qrparm.landfrac.pp '
                            '/project/cdds/ancil/UKESM1-0-LL/qrparm.soil.pp '
                            '/project/cdds/ancil/UKESM1-0-LL/ocean_constants.nc '
                            '/project/cdds/ancil/UKESM1-0-LL/ocean_byte_masks.nc '
                            '/project/cdds/ancil/UKESM1-0-LL/ocean_basin.nc '
                            '/project/cdds/ancil/UKESM1-0-LL/diaptr_basin_masks.nc '
                            '/project/cdds/ancil/UKESM1-0-LL/ocean_zostoga.nc')

        self.grid_id = 'atmos-native'
        self.grid = 'Native N96 grid; 192 x 144 longitude/latitude'
        self.grid_label = Cmip6GridLabel.from_name('native').label
        self.hybrid_heights_files = ('/home/h03/cdds/etc/vertical_coordinates/atmosphere_theta_levels_85.txt '
                                     '/home/h03/cdds/etc/vertical_coordinates/atmosphere_rho_levels_86.txt')
        plugin = PluginStore.instance().get_plugin()
        grid_info = plugin.grid_info(self.model_id, GridType.ATMOS)
        self.nominal_resolution = grid_info.nominal_resolution
        self.replacement_coordinates_file = '/home/h03/cdds/etc/horizontal_coordinates/cice_eORCA1_coords.nc'
        self.cmor_setup_format = (
            '[cmor_setup]\ncmor_log_file = {}\ncreate_subdirectories = {}\nmip_table_dir = {}\n'
            'netcdf_file_action = {}\n\n')
        self.cmor_setup_section = self.cmor_setup_format.format(
            self.cmor_log,
            self.create_subdirectories, self.mip_table_dir,
            self.netcdf_file_action)
        self.cmor_dataset_format = (
            '[cmor_dataset]\nbranch_date_in_child = {}\n'
            'branch_date_in_parent = {}\nbranch_method = {}\n'
            'calendar = {}\nexperiment_id = {}\ngrid = {}\ngrid_label = {}\n'
            'institution_id = {}\nlicense = {}\nmip = {}\nmip_era = {}\n'
            'model_id = {}\nmodel_type = {}\nnominal_resolution = {}\n'
            'output_dir = {}\nparent_base_date = {}\n'
            'parent_experiment_id = {}\nparent_mip_era = {}\n'
            'parent_model_id = {}\nparent_time_units = {}\n'
            'parent_variant_label = {}\nsub_experiment_id = {}\n'
            'variant_label = {}\n\n')
        self.cmor_dataset_section = self.cmor_dataset_format.format(
            self.branch_date_in_child, self.branch_date_in_parent,
            self.branch_method, self.calendar, self.experiment_id, self.grid,
            self.grid_label, self.institution_id, self.CMOR_license, self.mip,
            self.mip_era, self.model_id, self.model_type,
            self.nominal_resolution, self.output_dir, self.parent_base_date,
            self.parent_experiment_id, self.parent_mip_era,
            self.parent_model_id, self.parent_time_units,
            self.parent_variant_label, self.sub_experiment_id,
            self.variant_label)
        self.global_attributes_format = (
            '[global_attributes]\nfurther_info_url = https://furtherinfo.es-doc.org/{}.{}.{}.{}.{}.{}\n\n'
        )
        self.global_attributes_section = self.global_attributes_format.format(
            self.mip_era, self.institution_id, self.model_id, self.experiment_id,
            self.sub_experiment_id, self.variant_label)
        self.request_format = (
            '[request]\nancil_files = {}\nbase_date = {}\n'
            'deflate_level = {}\nhybrid_heights_files = {}\n'
            'model_output_dir = {}\nreplacement_coordinates_file = {}\n'
            'run_bounds = {}\nshuffle = {}\nsites_file = {}\n'
            'suite_id = {}\n\n')
        self.request_section = self.request_format.format(
            self.ancil_files, self.base_date, self.deflate_level,
            self.hybrid_heights_files, self.model_output_dir,
            self.replacement_coordinates_file, self.run_bounds, self.shuffle,
            self.sites_file, self.suite_id)
        self.stream_section = '[stream_ap5]\nCMIP6_Amon = tas\n\n'
        self.masking_section = ('[masking]\n'
                                'stream_ap5_cice-U = -1:None:None,180:None:None\n'
                                'stream_ap5_grid-V = -1:None:None,180:None:None\n\n')
        self.user_config = (
            self.user_config_file_header + self.cmor_setup_section
            + self.cmor_dataset_section + self.request_section
            + self.global_attributes_section + self.masking_section
            + self.stream_section)
        self.requested_variables_list = {
            'experiment_id': self.experiment_id,
            'mip': self.mip,
            'model_id': self.model_id,
            'model_type': self.model_type,
            'requested_variables': [
                {'active': 'true',
                 'label': 'tas',
                 'miptable': 'Amon',
                 'stream': 'ap5'}],
            'suite_id': self.suite_id}
        set_checksum(self.requested_variables_list)

    def _read_config(self, filename):
        with open(filename, 'r') as file_handle:
            config = file_handle.read()
        return config

    def _construct_log_path(self):
        log_fname = '{0}_{1}.log'.format(self.log_name, self.log_datestamp)
        self.log_path = os.path.join(self.log_dir, log_fname)

    def _main(self):
        # Use '--quiet' to ensure no log messages are printed to screen.
        args = [self.request_path, '--requested_variables_list_file',
                self.requested_variables_list_path,  '--output_dir', self.output_dir_for_ucf,]
        self._construct_log_path()
        exit_code = main(args)
        return exit_code

    def _run(self, requested_variables_list):
        write_json(self.requested_variables_list_path, requested_variables_list)
        exit_code = self._main()
        outputs = {
            filename: self._read_config(os.path.join(self.output_dir_for_ucf, filename))
            for filename in os.listdir(self.output_dir_for_ucf) if filename not in ['log']}
        return outputs, exit_code

    @unittest.mock.patch('cdds.common.get_log_datestamp')
    def test_produce_user_configuration_file(self, mock_log_datestamp):
        mock_log_datestamp.return_value = self.log_datestamp
        reference = {self.user_config_template_name.format(
            self.grid_id): self.user_config}
        # The output directory must exist before running 'main()'.
        if not os.path.exists(self.output_dir_for_ucf):
            os.mkdir(self.output_dir_for_ucf)
        output, exit_code = self._run(self.requested_variables_list)
        self.assertEqual(exit_code, 0)
        self.assertEqual(output, reference)


if __name__ == '__main__':
    unittest.main()
