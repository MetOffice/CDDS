# (C) British Crown Copyright 2018-2022, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
# pylint: disable = no-member
"""
Tests for :mod:`command_line.py`.
"""
import logging
import os
import tempfile
import unittest.mock

from nose.plugins.attrib import attr

from common.io import write_json
from common.plugins.plugins import PluginStore
from common.plugins.plugin_loader import load_plugin
from common.plugins.grid import GridType
from common.plugins.cmip6.cmip6_grid import Cmip6GridLabel

from hadsdk.common import set_checksum
from hadsdk.constants import TIME_UNIT_DESCRIPTION, COMMENT_FORMAT
from cdds_configure import __version__
from cdds_configure.arguments import read_configure_arguments
from cdds_configure.command_line import main
from cdds_configure.constants import HEADER_TEMPLATE


@attr('slow')
class TestMain(unittest.TestCase):
    """
    Tests for :func:`main` in :mod:`command_line.py`.
    """

    def setUp(self):
        load_plugin()
        self.arguments = read_configure_arguments('generate_user_config_files')
        self.user_config_template_name = (
            self.arguments.user_config_template_name)
        self.user_config_file_header = COMMENT_FORMAT.format(
            HEADER_TEMPLATE.format(__version__))
        self.mip_era = 'CMIP6'
        self.temp_dir = tempfile.mkdtemp()
        self.requested_variables_list_path = os.path.join(self.temp_dir, 'CMIP6_list.json')
        self.request_path = os.path.join(self.temp_dir, 'request.json')
        self.root_proc_directory = os.path.join(self.temp_dir, 'proc_dir')
        self.output_dir_for_ucf = os.path.join(self.temp_dir, 'random_directory_name')
        self.log_dir = os.path.join(self.output_dir_for_ucf, 'log')
        self.log_name = 'test_main'
        self.log_datestamp = '2019-11-23T1432Z'
        self.log_path = ''  # to be constructed later
        # Request:
        self.branch_date_in_child = '1850-01-01-00-00-00'
        self.branch_date_in_parent = '1850-01-01-00-00-00'
        self.branch_method = 'continuation'
        self.calendar = '360_day'
        self.child_base_date = '1850-01-01-00-00-00'
        self.create_subdirectories = self.arguments.create_subdirectories
        self.deflate_level = self.arguments.deflate_level
        self.experiment_id = 'piControl'
        self.institution_id = 'MOHC_test'
        self.CMOR_license = self.arguments.license
        self.mip = 'CMIP'
        self.mip_era = 'CMIP6'
        self.mip_table_dir = '/path/to/MIP/tables/'
        self.model_id = 'UKESM1-0-LL'
        # Add ancil files and replacement coordinates file:
        self.arguments.add_ancil_files(self.model_id)
        self.arguments.add_replacement_coordinates_file(self.model_id)
        self.arguments.add_hybrid_heights_files(self.model_id)
        self.model_output_dir = '/path/to/model/output/files/'
        self.model_type = 'AOGCM'
        self.netcdf_file_action = self.arguments.netcdf_file_action
        self.output_dir = '/path/to/output/directory/'
        self.package = 'configure_functional_test'
        self.parent_base_date = '1850-01-01-00-00-00'
        self.parent_experiment_id = 'piControl-spinup'
        self.parent_mip_era = 'CMIP6'
        self.parent_model_id = 'HadGEM3-GC31-LL'
        self.parent_time_units = TIME_UNIT_DESCRIPTION
        self.parent_variant_label = 'r1i1p1f1'
        self.run_bounds = '2021-01-01-00-00-00 2021-02-01-00-00-00'
        self.shuffle = self.arguments.shuffle
        self.sub_experiment_id = 'none'
        self.suite_id = 'u-abcde'
        self.variant_label = 'VariantLabel'
        self.request_id = '{0}_{1}_{2}'.format(
            self.model_id, self.experiment_id, self.variant_label)
        self.request = {
            'branch_date_in_child': self.branch_date_in_child,
            'branch_date_in_parent': self.branch_date_in_parent,
            'branch_method': self.branch_method,
            'calendar': self.calendar, 'child_base_date': self.child_base_date,
            'experiment_id': self.experiment_id,
            'institution_id': self.institution_id,
            'license': self.CMOR_license, 'mip': self.mip,
            'mip_era': self.mip_era, 'mip_table_dir': self.mip_table_dir,
            'model_id': self.model_id,
            'model_output_dir': self.model_output_dir,
            'model_type': self.model_type,
            'output_dir': self.output_dir,
            'package': self.package,
            'parent_base_date': self.parent_base_date,
            'parent_experiment_id': self.parent_experiment_id,
            'parent_mip_era': self.parent_mip_era,
            'parent_model_id': self.parent_model_id,
            'parent_time_units': self.parent_time_units,
            'parent_variant_label': self.parent_variant_label,
            'request_id': self.request_id,
            'run_bounds': self.run_bounds,
            'sub_experiment_id': self.sub_experiment_id,
            'suite_id': self.suite_id, 'variant_label': self.variant_label}
        # User config:
        self.ancil_files = self.arguments.ancil_files
        self.grid_id = 'atmos-native'
        self.grid = 'Native N96 grid; 192 x 144 longitude/latitude'
        self.grid_label = Cmip6GridLabel.from_name('native').label
        self.hybrid_heights_files = self.arguments.hybrid_heights_files
        plugin = PluginStore.instance().get_plugin()
        grid_info = plugin.grid_info(self.model_id, GridType.ATMOS)
        self.nominal_resolution = grid_info.nominal_resolution
        self.replacement_coordinates_file = (
            self.arguments.replacement_coordinates_file)
        self.sites_file = self.arguments.sites_file
        self.cmor_setup_format = (
            '[cmor_setup]\ncreate_subdirectories = {}\nmip_table_dir = {}\n'
            'netcdf_file_action = {}\n\n')
        self.cmor_setup_section = self.cmor_setup_format.format(
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
            '[request]\nancil_files = {}\nchild_base_date = {}\n'
            'deflate_level = {}\nhybrid_heights_files = {}\n'
            'model_output_dir = {}\nreplacement_coordinates_file = {}\n'
            'run_bounds = {}\nshuffle = {}\nsites_file = {}\n'
            'suite_id = {}\n\n')
        self.request_section = self.request_format.format(
            self.ancil_files, self.child_base_date, self.deflate_level,
            self.hybrid_heights_files, self.model_output_dir,
            self.replacement_coordinates_file, self.run_bounds, self.shuffle,
            self.sites_file, self.suite_id)
        self.stream_section = '[stream_ap5]\nCMIP6_Amon = tas\n\n'
        self.user_config = (
            self.user_config_file_header + self.cmor_setup_section
            + self.cmor_dataset_section + self.request_section
            + self.global_attributes_section + self.stream_section)
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

    def _main(self, use_proc_dir, template, data_request_version=None):
        # Use '--quiet' to ensure no log messages are printed to screen.
        args = [self.request_path, '--requested_variables_list_file',
                self.requested_variables_list_path, '--output_dir',
                self.output_dir_for_ucf, '--log_name', self.log_name,
                '--quiet']
        if use_proc_dir:
            args.append('--use_proc_dir')
        if template:
            args.append('--template')
        if data_request_version is not None:
            args.extend(['--data_request_version', data_request_version])
        self._construct_log_path()
        exit_code = main(args)
        return exit_code

    def _run(self, request, requested_variables_list, use_proc_dir, template,
             data_request_version=None):
        write_json(self.request_path, request)
        write_json(self.requested_variables_list_path,
                   requested_variables_list)
        exit_code = self._main(use_proc_dir, template, data_request_version)
        outputs = {
            filename: self._read_config(os.path.join(self.output_dir_for_ucf, filename))
            for filename in os.listdir(self.output_dir_for_ucf) if filename not in ['log']}
        return outputs, exit_code

    @unittest.mock.patch('hadsdk.common.get_log_datestamp')
    def test_produce_user_configuration_file(self, mock_log_datestamp):
        mock_log_datestamp.return_value = self.log_datestamp
        reference = {self.user_config_template_name.format(
            self.grid_id): self.user_config}
        # The output directory must exist before running 'main()'.
        use_proc_dir = False
        if not os.path.exists(self.output_dir_for_ucf):
            os.mkdir(self.output_dir_for_ucf)
        template = False
        output, exit_code = self._run(
            self.request, self.requested_variables_list, use_proc_dir,
            template)
        self.assertEqual(exit_code, 0)
        self.assertEqual(output, reference)

    @unittest.mock.patch('hadsdk.common.get_log_datestamp')
    def test_produce_user_configuration_file_template(self,
                                                      mock_log_datestamp):
        mock_log_datestamp.return_value = self.log_datestamp
        cmor_setup_format = (
            '[cmor_setup]\ncmor_log_file = {}\ncreate_subdirectories = {}\n'
            'mip_table_dir = {}\nnetcdf_file_action = {}\n\n')
        cmor_setup_section = cmor_setup_format.format(
            '{{ cmor_log }}', self.create_subdirectories, self.mip_table_dir,
            self.netcdf_file_action)
        cmor_dataset_section = self.cmor_dataset_format.format(
            self.branch_date_in_child, self.branch_date_in_parent,
            self.branch_method, self.calendar, self.experiment_id, self.grid,
            self.grid_label, self.institution_id, self.CMOR_license, self.mip,
            self.mip_era, self.model_id, self.model_type,
            self.nominal_resolution, '{{ output_dir }}', self.parent_base_date,
            self.parent_experiment_id, self.parent_mip_era,
            self.parent_model_id, self.parent_time_units,
            self.parent_variant_label, self.sub_experiment_id,
            self.variant_label)
        request_section = self.request_format.format(
            self.ancil_files, self.child_base_date, self.deflate_level,
            self.hybrid_heights_files, '{{ input_dir }}',
            self.replacement_coordinates_file,
            '{{ start_date }} {{ end_date }}', self.shuffle, self.sites_file,
            self.suite_id)
        user_config = (self.user_config_file_header + cmor_setup_section
                       + cmor_dataset_section + request_section
                       + self.global_attributes_section + self.stream_section)
        reference = {
            self.user_config_template_name.format(self.grid_id): user_config}
        # The output directory must exist before running 'main()'.
        use_proc_dir = False
        if not os.path.exists(self.output_dir_for_ucf):
            os.mkdir(self.output_dir_for_ucf)
        template = True
        output, exit_code = self._run(
            self.request, self.requested_variables_list, use_proc_dir,
            template)
        self.assertEqual(exit_code, 0)
        self.assertEqual(output, reference)

    @unittest.mock.patch('hadsdk.common.get_log_datestamp')
    def test_ensure_parent_options_are_validated(self, mock_log_datestamp):
        mock_log_datestamp.return_value = self.log_datestamp
        del self.request['parent_model_id']
        # The output directory must exist before running 'main()'.
        use_proc_dir = False
        if not os.path.exists(self.output_dir_for_ucf):
            os.mkdir(self.output_dir_for_ucf)
        template = False
        logging.disable(logging.CRITICAL)
        _, exit_code = self._run(
            self.request, self.requested_variables_list, use_proc_dir,
            template)
        self.assertEqual(exit_code, 1)

    @unittest.mock.patch('hadsdk.common.get_log_datestamp')
    def test_mip_table_dir_from_arguments(self, mock_log_datestamp):
        del self.request['mip_table_dir']
        mock_log_datestamp.return_value = self.log_datestamp
        cmor_setup_section = self.cmor_setup_format.format(
            self.create_subdirectories, self.arguments.mip_table_dir,
            self.netcdf_file_action)
        user_config = (self.user_config_file_header + cmor_setup_section
                       + self.cmor_dataset_section + self.request_section
                       + self.global_attributes_section + self.stream_section)
        reference = {
            self.user_config_template_name.format(self.grid_id): user_config}
        # The output directory must exist before running 'main()'.
        use_proc_dir = False
        if not os.path.exists(self.output_dir_for_ucf):
            os.mkdir(self.output_dir_for_ucf)
        template = False
        output, exit_code = self._run(
            self.request, self.requested_variables_list, use_proc_dir,
            template)
        self.assertEqual(exit_code, 0)
        self.assertEqual(output, reference)

    @unittest.mock.patch('hadsdk.common.get_log_datestamp')
    def test_mip_table_dir_from_command_line(self, mock_log_datestamp):
        del self.request['mip_table_dir']
        mock_log_datestamp.return_value = self.log_datestamp
        data_request_version = '01.00.31'
        mip_table_dir = os.path.join(
            self.arguments.root_mip_table_dir, data_request_version)
        cmor_setup_section = self.cmor_setup_format.format(
            self.create_subdirectories, mip_table_dir, self.netcdf_file_action)
        user_config = (self.user_config_file_header + cmor_setup_section
                       + self.cmor_dataset_section + self.request_section
                       + self.global_attributes_section + self.stream_section)
        reference = {
            self.user_config_template_name.format(self.grid_id): user_config}
        # The output directory must exist before running 'main()'.
        use_proc_dir = False
        if not os.path.exists(self.output_dir_for_ucf):
            os.mkdir(self.output_dir_for_ucf)
        template = False
        output, exit_code = self._run(
            self.request, self.requested_variables_list, use_proc_dir,
            template, data_request_version)
        self.assertEqual(exit_code, 0)
        self.assertEqual(output, reference)

    @unittest.mock.patch('hadsdk.common.get_log_datestamp')
    def test_ancil_files_from_request(self, mock_log_datestamp):
        ancil_files = '/ancil/file/one.pp /ancil/file/two.pp'
        mock_log_datestamp.return_value = self.log_datestamp
        self.request['ancil_files'] = ancil_files
        request_section = self.request_format.format(
            ancil_files, self.child_base_date, self.deflate_level,
            self.hybrid_heights_files, self.model_output_dir,
            self.replacement_coordinates_file, self.run_bounds, self.shuffle,
            self.sites_file, self.suite_id)
        user_config = (self.user_config_file_header + self.cmor_setup_section
                       + self.cmor_dataset_section + request_section
                       + self.global_attributes_section + self.stream_section)
        reference = {
            self.user_config_template_name.format(self.grid_id): user_config}
        # The output directory must exist before running 'main()'.
        use_proc_dir = False
        if not os.path.exists(self.output_dir_for_ucf):
            os.mkdir(self.output_dir_for_ucf)
        template = False
        output, exit_code = self._run(
            self.request, self.requested_variables_list, use_proc_dir,
            template)
        self.assertEqual(exit_code, 0)
        self.assertEqual(output, reference)


if __name__ == '__main__':
    unittest.main()
