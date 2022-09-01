# (C) British Crown Copyright 2018-2022, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
"""
Tests for :mod:`request.py`.
"""
from collections import OrderedDict
import unittest

from hadsdk.arguments import read_default_arguments

from cdds.common.request import Request
from cdds.configure.request import (
    retrieve_required_keys, validate_branch_options, retrieve_request_metadata)


class TestRetrieveRequiredKeys(unittest.TestCase):
    """
    Tests for :func:`retrieve_required_keys` in :mod:`request.py`.
    """
    def setUp(self):
        self.required_keys = [
            'branch_method', 'calendar', 'child_base_date', 'experiment_id',
            'institution_id', 'mip', 'mip_era', 'model_id', 'model_output_dir',
            'model_type', 'output_dir', 'run_bounds', 'sub_experiment_id',
            'suite_id', 'variant_label']
        self.template_keys = [
            'cmor_log_file', 'model_output_dir', 'output_dir', 'run_bounds']
        arguments = read_default_arguments('cdds.configure', 'cdds.configure')
        self.ignore_keys = arguments.args.keys()

    def test_retrieve_required_keys(self):
        template = False
        reference = self.required_keys
        output = retrieve_required_keys(template, self.ignore_keys)
        self.assertEqual(output, reference)

    def test_retrieve_required_keys_with_template(self):
        template = True
        reference = [key for key in self.required_keys
                     if key not in self.template_keys]
        output = retrieve_required_keys(template, self.ignore_keys)
        self.assertEqual(output, reference)


class TestValidateBranchOptions(unittest.TestCase):
    """
    Tests for :func:`validate_branch_options` in :mod:`request.py`.
    """
    def setUp(self):
        self.items = {
            'branch_method': 'continuation', 'branch_date_in_child': '',
            'branch_date_in_parent': '', 'parent_base_date': '',
            'parent_experiment_id': '', 'parent_mip_era': '',
            'parent_model_id': '', 'parent_time_units': '',
            'parent_variant_label': ''}
        self.request = Request(self.items)

    def test_validate_branch_options(self):
        self.assertIsNone(validate_branch_options(self.request))

    def test_validate_branch_options_with_one_missing(self):
        del self.items['parent_mip_era']
        request = Request(self.items)
        self.assertRaises(AttributeError, validate_branch_options, request)


class TestRetrieveRequestMetadata(unittest.TestCase):
    """
    Tests for :func:`retrieve_request_metadata` in :mod:`request.py`.
    """
    def setUp(self):
        self.branch_method = 'no parent'
        self.calendar = '360_day'
        self.child_base_date = '1999-12-01-00-00-00'
        self.experiment_id = 'amip'
        self.institution_id = 'MOHC'
        self.license = 'License'
        self.mip = 'CMIP'
        self.mip_era = 'CMIP6'
        self.mip_table_dir = '/path/to/MIP/tables/'
        self.model_id = 'UKESM1-0-LL'
        self.model_output_dir = '/path/to/model/output/files/'
        self.model_type = 'AOGCM'
        self.output_dir = '/path/to/output/directory/'
        self.run_bounds = '2021-01-01-00-00-00 2021-02-01-00-00-00'
        self.sub_experiment_id = 'none'
        self.suite_id = 'u-abcde'
        self.variant_label = 'Variant label'
        self.required_items = {
            'branch_method': self.branch_method, 'calendar': self.calendar,
            'child_base_date': self.child_base_date,
            'experiment_id': self.experiment_id,
            'institution_id': self.institution_id, 'license': self.license,
            'mip': self.mip, 'mip_era': self.mip_era,
            'mip_table_dir': self.mip_table_dir,
            'model_id': self.model_id,
            'model_output_dir': self.model_output_dir,
            'model_type': self.model_type,
            'output_dir': self.output_dir, 'run_bounds': self.run_bounds,
            'sub_experiment_id': self.sub_experiment_id,
            'suite_id': self.suite_id, 'variant_label': self.variant_label}
        self.branch_date_in_child = '2004-12-01-00-00-00'
        self.branch_date_in_parent = '2006-12-01-00-00-00'
        self.parent_base_date = '2005-12-01-00-00-00'
        self.parent_experiment_id = 'amip'
        self.parent_mip_era = 'CMIP6'
        self.parent_model_id = 'UKESM1-0-LL'
        self.parent_time_units = 'days since 1950-01-01'
        self.parent_variant_label = 'Parent variant label'
        self.branch_items = {
            'branch_date_in_child': self.branch_date_in_child,
            'branch_date_in_parent': self.branch_date_in_parent,
            'parent_base_date': self.parent_base_date,
            'parent_experiment_id': self.parent_experiment_id,
            'parent_mip_era': self.parent_mip_era,
            'parent_model_id': self.parent_model_id,
            'parent_time_units': self.parent_time_units,
            'parent_variant_label': self.parent_variant_label}
        self.ancil_files = '/path/to/ancil/file1 /path/to/ancil/file2'
        self.atmos_timestep = '600'
        self.cmor_log_file = '/path/to/cmor.log'
        self.netcdf_file_action = 'CMOR_REPLACE_4'
        self.optional_items = {
            'ancil_files': self.ancil_files,
            'atmos_timestep': self.atmos_timestep,
            'cmor_log_file': self.cmor_log_file,
            'netcdf_file_action': self.netcdf_file_action}

    def test_retrieve_request_metadata_just_required_options(self):
        request = Request(self.required_items)
        template = False
        output = retrieve_request_metadata(request, template)
        cmor_setup_items = {'mip_table_dir': self.mip_table_dir}
        cmor_dataset_items = {
            'branch_method': self.branch_method,
            'calendar': self.calendar, 'experiment_id': self.experiment_id,
            'institution_id': self.institution_id, 'license': self.license,
            'mip': self.mip, 'mip_era': self.mip_era,
            'model_id': self.model_id, 'model_type': self.model_type,
            'output_dir': self.output_dir,
            'sub_experiment_id': self.sub_experiment_id,
            'variant_label': self.variant_label}
        request_items = {
            'child_base_date': self.child_base_date,
            'model_output_dir': self.model_output_dir,
            'run_bounds': self.run_bounds,
            'suite_id': self.suite_id}
        reference = OrderedDict()
        reference['cmor_setup'] = OrderedDict(sorted(cmor_setup_items.items()))
        reference['cmor_dataset'] = OrderedDict(
            sorted(cmor_dataset_items.items()))
        reference['request'] = OrderedDict(sorted(request_items.items()))
        reference['global_attributes'] = OrderedDict()
        self.assertEqual(list(output.keys()), list(reference.keys()))
        self.assertEqual(list(output.values()), list(reference.values()))

    def test_retrieve_request_metadata_with_templating(self):
        request = Request(self.required_items)
        template = True
        output = retrieve_request_metadata(request, template)
        cmor_setup_items = {
            'cmor_log_file': '{{ cmor_log }}',
            'mip_table_dir': self.mip_table_dir}
        cmor_dataset_items = {
            'branch_method': self.branch_method,
            'calendar': self.calendar, 'experiment_id': self.experiment_id,
            'institution_id': self.institution_id, 'license': self.license,
            'mip': self.mip, 'mip_era': self.mip_era,
            'model_id': self.model_id, 'model_type': self.model_type,
            'output_dir': '{{ output_dir }}',
            'sub_experiment_id': self.sub_experiment_id,
            'variant_label': self.variant_label}
        request_items = {
            'child_base_date': self.child_base_date,
            'model_output_dir': '{{ input_dir }}',
            'run_bounds': '{{ start_date }} {{ end_date }}',
            'suite_id': self.suite_id}
        reference = OrderedDict()
        reference['cmor_setup'] = OrderedDict(sorted(cmor_setup_items.items()))
        reference['cmor_dataset'] = OrderedDict(
            sorted(cmor_dataset_items.items()))
        reference['request'] = OrderedDict(sorted(request_items.items()))
        reference['global_attributes'] = OrderedDict()
        self.assertEqual(list(output.keys()), list(reference.keys()))
        self.assertEqual(list(output.values()), list(reference.values()))

    def test_retrieve_request_metadata_required_and_parent_options(self):
        items = self.required_items
        branch_method = 'standard'
        items['branch_method'] = branch_method
        items.update(self.branch_items)
        request = Request(items)
        template = False
        output = retrieve_request_metadata(request, template)
        cmor_setup_items = {'mip_table_dir': self.mip_table_dir}
        cmor_dataset_items = {
            'branch_date_in_child': self.branch_date_in_child,
            'branch_date_in_parent': self.branch_date_in_parent,
            'branch_method': branch_method, 'calendar': self.calendar,
            'experiment_id': self.experiment_id,
            'institution_id': self.institution_id, 'license': self.license,
            'mip': self.mip, 'mip_era': self.mip_era,
            'model_id': self.model_id, 'model_type': self.model_type,
            'output_dir': self.output_dir,
            'parent_base_date': self.parent_base_date,
            'parent_experiment_id': self.parent_experiment_id,
            'parent_mip_era': self.parent_mip_era,
            'parent_model_id': self.parent_model_id,
            'parent_time_units': self.parent_time_units,
            'parent_variant_label': self.parent_variant_label,
            'sub_experiment_id': self.sub_experiment_id,
            'variant_label': self.variant_label}
        request_items = {
            'child_base_date': self.child_base_date,
            'model_output_dir': self.model_output_dir,
            'run_bounds': self.run_bounds,
            'suite_id': self.suite_id}
        reference = OrderedDict()
        reference['cmor_setup'] = OrderedDict(sorted(cmor_setup_items.items()))
        reference['cmor_dataset'] = OrderedDict(
            sorted(cmor_dataset_items.items()))
        reference['request'] = OrderedDict(sorted(request_items.items()))
        reference['global_attributes'] = OrderedDict()
        self.assertEqual(list(output.keys()), list(reference.keys()))
        self.assertEqual(list(output.values()), list(reference.values()))

    def test_retrieve_request_metadata_required_and_optional_options(self):
        items = {}
        items.update(self.required_items)
        items.update(self.optional_items)
        request = Request(items)
        template = False
        output = retrieve_request_metadata(request, template)
        cmor_setup_items = {
            'cmor_log_file': self.cmor_log_file,
            'mip_table_dir': self.mip_table_dir,
            'netcdf_file_action': self.netcdf_file_action}
        cmor_dataset_items = {
            'branch_method': self.branch_method,
            'calendar': self.calendar, 'experiment_id': self.experiment_id,
            'institution_id': self.institution_id, 'license': self.license,
            'mip': self.mip, 'mip_era': self.mip_era,
            'model_id': self.model_id, 'model_type': self.model_type,
            'output_dir': self.output_dir,
            'sub_experiment_id': self.sub_experiment_id,
            'variant_label': self.variant_label}
        request_items = {
            'ancil_files': self.ancil_files,
            'atmos_timestep': self.atmos_timestep,
            'child_base_date': self.child_base_date,
            'model_output_dir': self.model_output_dir,
            'run_bounds': self.run_bounds, 'suite_id': self.suite_id}
        reference = OrderedDict()
        reference['cmor_setup'] = OrderedDict(sorted(cmor_setup_items.items()))
        reference['cmor_dataset'] = OrderedDict(
            sorted(cmor_dataset_items.items()))
        reference['request'] = OrderedDict(sorted(request_items.items()))
        reference['global_attributes'] = OrderedDict()
        self.assertEqual(list(output.keys()), list(reference.keys()))
        self.assertEqual(list(output.values()), list(reference.values()))


if __name__ == '__main__':
    unittest.main()
