# (C) British Crown Copyright 2018-2022, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
"""
Tests for :mod:`request.py`.
"""
from collections import OrderedDict, defaultdict
import unittest
import os

from cdds.common.request.request import read_request
from cdds.configure.request import retrieve_request_metadata


class TestRetrieveRequestMetadata(unittest.TestCase):
    """
    Tests for :func:`retrieve_request_metadata` in :mod:`request.py`.
    """
    def setUp(self):
        self.maxDiff = None
        current_dir = os.path.dirname(os.path.realpath(__file__))
        self.data_dir = os.path.join(current_dir, '..', 'test_common', 'test_request', 'data')
        request_path = os.path.join(self.data_dir, 'test_request.cfg')
        self.request = read_request(request_path)

    def test_retrieve_request_metadata(self):
        expected_metadata = OrderedDict(
            [
                (
                    'cmor_setup', {
                        'mip_table_dir': '/gws/nopw/j04/mohc_shared/cdds/etc/mip_tables/CMIP6/01.00.29',
                        'cmor_log_file': '{{ cmor_log }}',
                        'netcdf_file_action': 'CMOR_REPLACE_4',
                        'create_subdirectories': 0
                    }
                ),
                (
                    'cmor_dataset', {
                        'branch_method': 'standard',
                        'calendar': '360_day',
                        'experiment_id': 'piControl',
                        'institution_id': 'MOHC',
                        'license': (
                            'CMIP6 model data produced by the Met Office Hadley Centre is licensed under a '
                            'Creative Commons Attribution-ShareAlike 4.0 International License '
                            '(https://creativecommons.org/licenses). Consult '
                            'https://pcmdi.llnl.gov/CMIP6/TermsOfUse for terms of use governing CMIP6 output, '
                            'including citation requirements and proper acknowledgment. Further information about '
                            'this data, including some limitations, can be found via the further_info_url '
                            '(recorded as a global attribute in this file) and at https://ukesm.ac.uk/cmip6. The '
                            'data producers and data providers make no warranty, either express or implied, '
                            'including, but not limited to, warranties of merchantability and fitness for a '
                            'particular purpose. All liabilities arising from the supply of the information '
                            '(including any liability arising in negligence) are excluded to the fullest extent '
                            'permitted by law.'
                        ),
                        'mip': 'CMIP',
                        'mip_era': 'CMIP6',
                        'model_id': 'UKESM1-0-LL',
                        'model_type': ['AOGCM', 'BGC', 'AER', 'CHEM'],
                        'sub_experiment_id': 'none',
                        'variant_label': 'r1i1p1f2',
                        'branch_date_in_child': '1960-01-01T00:00:00',
                        'branch_date_in_parent': '1960-01-01T00:00:00',
                        'parent_base_date': '1850-01-01T00:00:00',
                        'parent_experiment_id': 'piControl-spinup',
                        'parent_mip_era': 'CMIP6',
                        'parent_model_id': 'UKESM1-0-LL',
                        'parent_time_units': 'days since 1850-01-01',
                        'parent_variant_label': 'r1i1p1f2',
                        'output_dir': '{{ output_dir }}'
                    }
                ),
                (
                    'request', {
                        'model_output_dir': '{{ input_dir }}',
                        'run_bounds': '{{ start_date }} {{ end_date }}',
                        'base_date': '1850-01-01T00:00:00',
                        'deflate_level': '2',
                        'suite_id': 'u-aw310',
                        'ancil_files': ('/gws/nopw/j04/mohc_shared/cdds/etc/ancil/UKESM1-0-LL/qrparm.landfrac.pp '
                                        '/gws/nopw/j04/mohc_shared/cdds/etc/ancil/UKESM1-0-LL/qrparm.soil.pp '
                                        '/gws/nopw/j04/mohc_shared/cdds/etc/ancil/UKESM1-0-LL/ocean_constants.nc '
                                        '/gws/nopw/j04/mohc_shared/cdds/etc/ancil/UKESM1-0-LL/ocean_byte_masks.nc '
                                        '/gws/nopw/j04/mohc_shared/cdds/etc/ancil/UKESM1-0-LL/ocean_basin.nc '
                                        '/gws/nopw/j04/mohc_shared/cdds/etc/ancil/UKESM1-0-LL/diaptr_basin_masks.nc '
                                        '/gws/nopw/j04/mohc_shared/cdds/etc/ancil/UKESM1-0-LL/ocean_zostoga.nc'),
                        'hybrid_heights_files': (
                            '/gws/nopw/j04/mohc_shared/cdds/etc/vertical_coordinates/atmosphere_theta_levels_85.txt'
                            ' /gws/nopw/j04/mohc_shared/cdds/etc/vertical_coordinates/atmosphere_rho_levels_86.txt'),
                        'replacement_coordinates_file': (
                            '/gws/nopw/j04/mohc_shared/cdds/etc/horizontal_coordinates/cice_eORCA1_coords.nc'),
                        'shuffle': True,
                        'sites_file': '/gws/nopw/j04/mohc_shared/cdds/etc/cfmip2/cfmip2-sites-orog.txt'

                    }
                )
            ]
        )
        output = retrieve_request_metadata(self.request)
        self.assertDictEqual(output, expected_metadata)


if __name__ == '__main__':
    unittest.main()
