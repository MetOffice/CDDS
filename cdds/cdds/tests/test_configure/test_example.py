# (C) British Crown Copyright 2017-2022, Met Office.
# Please see LICENSE.rst for license details.
from unittest import TestCase
from cdds.configure.command_line import main


class TestExample(TestCase):

    def test_me(self):
        requested_variables_list = {
            'experiment_id': 'amip',
            'mip': 'CMIP',
            'model_id': 'HadGEM3-GC31-MM',
            'model_type': 'AGCM AER',
            'requested_variables': [
                {'active': 'true',
                 'label': 'tas',
                 'miptable': 'day',
                 'stream': 'apa'}],
            'suite_id': 'mi-ba488'}

        request_variable_path = '/home/h04/kschmatz/test-data/proc_dir/CMIP6/CMIP/HadGEM3-GC31-MM_amip_r1i1p1f3/round-1/prepare/CMIP6_CMIP_amip_HadGEM3-GC31-MM.json'
        request_json = '/home/h04/kschmatz/request.json'

        arguments = [
            request_json,
            '--requested_variables_list_file', request_variable_path,
            '--output_dir', '/home/h04/kschmatz/test-data/output_dir',
            '--root_proc_dir', '/home/h04/kschmatz/test-data/proc_dir',
            '--root_data_dir', '/home/h04/kschmatz/test-data/data_dir'
        ]
        main(arguments)
