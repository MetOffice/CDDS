# (C) British Crown Copyright 2018-2021, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
"""
Tests for :mod:`model_config.py`.
"""
from copy import deepcopy
import unittest

from unittest.mock import patch
import unittest.mock
from io import StringIO
from textwrap import dedent

from hadsdk.tests.common import DummyMapping

from cdds_common.cdds_plugins.plugin_loader import load_plugin
from cdds_prepare.model_config import (
    retrieve_model_suite_variables, consolidate_atmos_enabled,
    create_ocean_enabled, _read_iodef_into_dict,
    _construct_enabled_var_from_iodef, export_file_from_suite,
    _read_field_def_xml_into_dict, _expand_field_groups,
    _get_iodef_filename_in_suite)
from cdds_prepare.tests.common import ATMOS_ENABLED, OCEAN_ENABLED


class TestRetreiveModelSuiteVariables(unittest.TestCase):
    """
    Tests for :func:`retrieve_model_suite_variables` in
    :mod:`model_config.py`.
    """
    def setUp(self):
        self.mappings = 'dummy_mappings'
        self.mip_era = 'CMIP6'
        self.model_type = 'AOGCM'
        self.suite_id = 'u-abcde'
        self.branch = 'branch'
        self.revision = 13579

    @patch('cdds_prepare.model_config.create_ocean_enabled')
    @patch('cdds_prepare.model_config.create_atmos_enabled')
    def test_all_variables_enabled(self, mcae, mcoe):
        mcae.return_value = ATMOS_ENABLED
        mcoe.return_value = OCEAN_ENABLED
        output = retrieve_model_suite_variables(
            self.mappings, self.mip_era, self.model_type, self.suite_id,
            self.branch, self.revision)
        mcae.assert_called_once_with(self.suite_id, self.branch, self.revision)
        mcoe.assert_called_once_with(self.mappings, self.mip_era,
                                     self.suite_id, self.branch, self.revision,
                                     'AOGCM')
        reference = {
            'enabled': ['Amon/tas', 'Eday/ua', 'Emon/rls', 'Oday/sos',
                        'Omon/tos', 'day/pr'],
            'disabled': []}
        self.assertEqual(output, reference)

    @patch('cdds_prepare.model_config.create_ocean_enabled')
    @patch('cdds_prepare.model_config.create_atmos_enabled')
    def test_single_variable_disabled(self, mcae, mcoe):
        atmos_enabled = deepcopy(ATMOS_ENABLED)
        atmos_enabled['day_pr_0_0']['enabled'] = False
        mcae.return_value = atmos_enabled
        mcoe.return_value = OCEAN_ENABLED
        output = retrieve_model_suite_variables(
            self.mappings, self.mip_era, self.model_type, self.suite_id,
            self.branch, self.revision)
        mcae.assert_called_once_with(self.suite_id, self.branch, self.revision)
        reference = {
            'enabled': ['Amon/tas', 'Eday/ua', 'Emon/rls', 'Oday/sos',
                        'Omon/tos'],
            'disabled': ['day/pr']}
        self.assertEqual(output, reference)

    @patch('cdds_prepare.model_config.create_ocean_enabled')
    @patch('cdds_prepare.model_config.create_atmos_enabled')
    def test_multiple_variables_disabled(self, mcae, mcoe):
        atmos_enabled = deepcopy(ATMOS_ENABLED)
        atmos_enabled['day_pr_0_0']['enabled'] = False
        mcae.return_value = atmos_enabled
        ocean_enabled = deepcopy(OCEAN_ENABLED)
        ocean_enabled['Oday/sos']['enabled'] = [False]
        mcoe.return_value = ocean_enabled
        output = retrieve_model_suite_variables(
            self.mappings, self.mip_era, self.model_type, self.suite_id,
            self.branch, self.revision)
        mcae.assert_called_once_with(self.suite_id, self.branch, self.revision)
        reference = {
            'enabled': ['Amon/tas', 'Eday/ua', 'Emon/rls', 'Omon/tos'],
            'disabled': ['Oday/sos', 'day/pr']}
        self.assertEqual(output, reference)

    @patch('cdds_prepare.model_config.create_ocean_enabled')
    @patch('cdds_prepare.model_config.create_atmos_enabled')
    def test_single_STASH_disabled(self, mcae, mcoe):
        atmos_enabled = deepcopy(ATMOS_ENABLED)
        atmos_enabled['Emon_rls_1_0']['enabled'] = False
        mcae.return_value = atmos_enabled
        mcoe.return_value = OCEAN_ENABLED
        output = retrieve_model_suite_variables(
            self.mappings, self.mip_era, self.model_type, self.suite_id,
            self.branch, self.revision)
        mcae.assert_called_once_with(self.suite_id, self.branch, self.revision)
        reference = {
            'enabled': ['Amon/tas', 'Eday/ua', 'Oday/sos', 'Omon/tos',
                        'day/pr'],
            'disabled': ['Emon/rls']}
        self.assertEqual(output, reference)


class TestConsolidateAtmosEnabled(unittest.TestCase):
    """
    Tests for :func:`consolidate_atmos_enabled` in
    :mod:`model_config.py`.
    """
    def setUp(self):
        self.maxDiff = None

    def test_consolidate_atmos_enabled(self):
        output = consolidate_atmos_enabled(ATMOS_ENABLED)
        reference = {
            'Amon/tas': {
                'cmor': ['tas'],
                'dom_name': ['DIAG'],
                'enabled': [True],
                'item': ['236'],
                'package': ['CMIP6-core'],
                'present': [True],
                'priority': ['dr1.0'],
                'section': ['03'],
                'sheet_name': ['Amon'],
                'stash': ['m01s03i236'],
                'tim_name': ['TMONMN'],
                'use_name': ['UP5']},
            'Eday/ua': {
                'cmor': ['ua'],
                'dom_name': ['PLEV19'],
                'enabled': [True],
                'item': ['301', '201', '202'],
                'package': ['CMIP6-core'],
                'present': [True],
                'priority': ['dr1.0'],
                'section': ['30'],
                'sheet_name': ['Eday'],
                'stash': ['m01s30i301', 'm01s30i201', 'm01s30i202'],
                'tim_name': ['TDAYMN'],
                'use_name': ['UP6']},
            'Emon/rls': {
                'cmor': ['rls'],
                'dom_name': ['DIAG'],
                'enabled': [True],
                'item': ['205', '201', '332'],
                'package': ['CMIP6-core'],
                'present': [True],
                'priority': ['dr1.0'],
                'section': ['02', '03'],
                'sheet_name': ['Emon'],
                'stash': ['m01s02i205', 'm01s02i201', 'm01s03i332'],
                'tim_name': ['TMONMN'],
                'use_name': ['UP5']},
            'day/pr': {
                'cmor': ['pr'],
                'dom_name': ['DIAG'],
                'enabled': [True],
                'item': ['216'],
                'package': ['CMIP6-core'],
                'present': [True],
                'priority': ['dr1.0'],
                'section': ['05'],
                'sheet_name': ['day'],
                'stash': ['m01s05i216'],
                'tim_name': ['TDAYMN'],
                'use_name': ['UP6']}}
        self.assertCountEqual(list(output.keys()), list(reference.keys()))
        for output_key, output_value in output.items():
            self.assertCountEqual(list(output_value.keys()), list(reference[output_key].keys()))
            for output_sub_key, output_sub_value in output_value.items():
                self.assertCountEqual(list(output_sub_value), list(reference[output_key][output_sub_key]))


IODEF_XML_CONTENTS = '''<!-- GO5.0 version of the XIOS namelist -->

<?xml version="1.0"?>

<simulation>

 <context id="nemo" >

    <!-- $id$ -->

    <!--
===============================================================================
                   definition of all existing variables                       =
                             DO NOT CHANGE                                    =
===============================================================================
    -->
    <field_definition src="./field_def_bgc.xml"/>
    <field_definition src="./field_def.xml"/>
    <!--
============================================================================
                      output files definition                              =
                       Define your own files                               =
                    put the variables you want...                          =
============================================================================
    -->

    <file_definition type="multiple_file"
    name="@expname@_@freq@_@startdate@_@enddate@" sync_freq="10d"
    min_digits="4" time_counter="record">

      <file_group id="1ts" output_freq="1ts"  output_level="10"
      enabled=".TRUE."/> <!-- 1 time step files -->

      <file_group id="1h" output_freq="1h"  output_level="10"
      enabled=".TRUE."/> <!-- 1h files -->
      <file_group id="2h" output_freq="2h"  output_level="10"
      enabled=".TRUE."/> <!-- 2h files -->
      <file_group id="3h" output_freq="3h"  output_level="10"
      enabled=".TRUE."/> <!-- 3h files -->
      <file_group id="4h" output_freq="4h"  output_level="10"
      enabled=".TRUE."/> <!-- 4h files -->
      <file_group id="6h" output_freq="6h"  output_level="10"
      enabled=".TRUE."/> <!-- 6h files -->

      <file_group id="1d" output_freq="1d" output_level="10"
      enabled=".TRUE."> <!-- 1d files -->

    <file id="file1" name_suffix="_grid_T"
    description="ocean T grid variables" >
    <field field_ref="sst" name="tos"
          standard_name="sea_surface_temperature"     />
          <field field_ref="sstmin" name="sstmin"
          standard_name="Potential_temp_min" />
          <field field_ref="sstmax" name="sstmax"
          standard_name="Potential_temp_max" />
    </file>

    <file id="file2" name_suffix="_grid_U"
    description="ocean U grid variables" enabled=".FALSE." >
          <field field_ref="ssu" name="sozocrtx"
          standard_name="sea_surface_eastward_sea_water_velocity"/>
      <field field_ref="utau"  name="sozotaux"
      standard_name="surface_downward_x_stress" />
    </file>

      </file_group>


      <file_group id="1m" output_freq="1mo"  output_level="10"
      enabled=".TRUE." split_freq="1mo" >  <!-- 1mo files -->

    <file id="file4" name_suffix="_grid_T"
    description="ocean T grid variables" >
          <field field_ref="e3t" name="thkcello"
          standard_name="cell_thickness" />
          <field field_ref="e3t" name="masscello"
          standard_name="sea_water_mass_per_unit_area" unit="kg/m2"
          long_name="Ocean Grid-Cell Mass per area" > @e3t * 1026.0 </field>
    </file>

        <file id="file8" name_suffix="_scalar" description="scalar variables"
        type="one_file" enabled=".true." >
          <field field_ref="voltot"       name="scvoltot"   />
          <field field_ref="temptot"      name="thetaoga"   />
          <field field_ref="saltot"       name="soga"   />
        </file>

        {MEDUSA_FIELD_GROUPS}

      </file_group>

      <file_group id="2m" output_freq="2mo" output_level="10"
      enabled=".TRUE."/> <!-- real 2m files -->
      <file_group id="3m" output_freq="3mo" output_level="10"
      enabled=".TRUE."/> <!-- real 3m files -->
      <file_group id="4m" output_freq="4mo" output_level="10"
      enabled=".TRUE."/> <!-- real 4m files -->
      <file_group id="6m" output_freq="6mo" output_level="10"
      enabled=".TRUE."/> <!-- real 6m files -->

      <file_group id="1y"  output_freq="1y" output_level="10"
      enabled=".TRUE."/> <!-- real yearly files -->
      <file_group id="2y"  output_freq="2y" output_level="10"
      enabled=".TRUE."/> <!-- real 2y files -->
      <file_group id="5y"  output_freq="5y" output_level="10"
      enabled=".TRUE."/> <!-- real 5y files -->
      <file_group id="10y" output_freq="10y" output_level="10"
      enabled=".TRUE."/> <!-- real 10y files -->

   </file_definition>

    <!--
============================================================================================================
= grid definition = = DO NOT CHANGE =
============================================================================================================
    -->

   <axis_definition>
      <axis id="deptht" standard_name="depth"
      long_name="Vertical T levels" unit="m" positive="down" />
      <axis id="deptht300" axis_ref="deptht" >
         <zoom_axis begin="0" n="35" />
      </axis>
      <axis id="depthu" standard_name="depth"
      long_name="Vertical U levels" unit="m" positive="down" />
      <axis id="depthv" standard_name="depth"
      long_name="Vertical V levels" unit="m" positive="down" />
      <axis id="depthw" standard_name="depth"
      long_name="Vertical W levels" unit="m" positive="down" />
      <axis id="nfloat" long_name="Float number"      unit="-"  />
      <axis id="icbcla" long_name="Iceberg class"     unit="-"  />
      <axis id="deptht_surface" axis_ref="deptht" >
         <zoom_axis begin=" 0 " n=" 1 " />
      </axis>
   </axis_definition>

   <domain_definition src="./domain_def.xml"/>

    <grid_definition>
        <!--  -->
       <grid id="grid_T_2D" >
         <domain id="grid_T" />
       </grid>
        <!--  -->
       <grid id="grid_T_3D" >
         <domain id="grid_T" />
         <axis axis_ref="deptht" />
       </grid>
        <!--  -->
       <grid id="grid_U_2D" >
         <domain id="grid_U" />
       </grid>
        <!--  -->
       <grid id="grid_U_3D" >
         <domain id="grid_U" />
         <axis axis_ref="depthu" />
       </grid>
        <!--  -->
       <grid id="grid_V_2D" >
         <domain id="grid_V" />
       </grid>
        <!--  -->
       <grid id="grid_V_3D" >
         <domain id="grid_V" />
         <axis axis_ref="depthv" />
       </grid>
        <!--  -->
       <grid id="grid_W_2D" >
         <domain id="grid_W" />
       </grid>
        <!--  -->
       <grid id="grid_W_3D" >
         <domain id="grid_W" />
         <axis axis_ref="depthw" />
       </grid>
        <!--  -->
       <grid id="grid_1point" >
         <domain domain_ref="1point"/>
       </grid>
        <!--  -->
       <grid id="scalar" >
       <!--A blank grid to represent a 0D scalar variable -->
       </grid>
        <!--  -->
       <grid id="grid_T_nfloat" >
         <domain id="grid_T" />
         <axis axis_ref="nfloat" />
       </grid>
        <!--  -->
       <grid id="grid_EqT" >
         <domain id="EqT" />
       </grid>
        <!--  -->
       <grid id="gznl_T_2D">
         <domain id="ptr" />
       </grid>
        <!--  -->
       <grid id="gznl_T_3D">
         <domain id="ptr" />
         <axis axis_ref="deptht" />
       </grid>
        <!--  -->
       <grid id="gznl_W_2D">
         <domain id="ptr" />
       </grid>
        <!--  -->
       <grid id="gznl_W_3D">
         <domain id="ptr" />
         <axis axis_ref="depthw" />
       </grid>
       <grid id="vert_sum">
         <domain id="grid_T"/>
         <scalar>
            <reduce_axis operation="sum" />
         </scalar>
       </grid>
       <grid id="zoom_300">
         <domain id="grid_T" />
         <axis axis_ref="deptht300"/>
       </grid>
       <grid id="zoom_300_sum">
         <domain id="grid_T" />
         <scalar>
            <reduce_axis operation="sum" />
         </scalar>
       </grid>
       <grid id="grid_T_surface_extract">
         <domain id="grid_T" />
         <axis   axis_ref="deptht_surface" />
       </grid>
    </grid_definition>
  </context>


  <context id="xios">

      <variable_definition>

      <variable id="info_level" type="int">0</variable>
      <variable id="using_server" type="bool">true</variable>
      <variable id="using_oasis" type="bool">true</variable>
      <variable id="oasis_codes_id" type="string" >toyoce</variable>

      </variable_definition>

  </context>

</simulation>
'''

IODEF_TEST_DICT = {
    '10y': {'enabled': '.TRUE.',
            'files': {},
            'id': '10y',
            'output_freq': '10y',
            'output_level': '10'},
    '1d': {'enabled': '.TRUE.',
           'files': {'file1': {
               'description': 'ocean T grid variables',
               'field_groups': {},
               'fields': {'sstmax': {'field_ref': 'sstmax',
                                     'name': 'sstmax',
                                     'standard_name': 'Potential_temp_max'},
                          'sstmin': {'field_ref': 'sstmin',
                                     'name': 'sstmin',
                                     'standard_name': 'Potential_temp_min'},
                          'tos': {'field_ref': 'sst',
                                  'name': 'tos',
                                  'standard_name': 'sea_surface_temperature'}},
               'id': 'file1',
               'name_suffix': '_grid_T'},
               'file2': {
                   'description': 'ocean U grid variables',
                   'enabled': '.FALSE.',
                   'field_groups': {},
                   'fields': {
                       'sozocrtx': {
                           'field_ref': 'ssu',
                           'name': 'sozocrtx',
                           'standard_name':
                               'sea_surface_eastward_sea_water_velocity'},
                       'sozotaux': {'field_ref': 'utau',
                                    'name': 'sozotaux',
                                    'standard_name':
                                        'surface_downward_x_stress'}},
                   'id': 'file2',
                   'name_suffix': '_grid_U'}},
           'id': '1d',
           'output_freq': '1d',
           'output_level': '10'},
    '1h': {'enabled': '.TRUE.',
           'files': {},
           'id': '1h',
           'output_freq': '1h',
           'output_level': '10'},
    '1m': {'enabled': '.TRUE.',
           'files': {'file4': {
               'description': 'ocean T grid variables',
               'field_groups': {},
               'fields': {
                   'masscello':
                       {'field_ref': 'e3t',
                        'long_name': 'Ocean Grid-Cell Mass per area',
                        'name': 'masscello',
                        'standard_name': 'sea_water_mass_per_unit_area',
                        'unit': 'kg/m2'},
                   'thkcello': {'field_ref': 'e3t',
                                'name': 'thkcello',
                                'standard_name': 'cell_thickness'}},
               'id': 'file4',
               'name_suffix': '_grid_T'},
               'file8':
                   {'description': 'scalar variables',
                    'enabled': '.true.',
                    'field_groups': {},
                    'fields': {'scvoltot': {'field_ref': 'voltot',
                                            'name': 'scvoltot'},
                               'soga': {'field_ref': 'saltot',
                                        'name': 'soga'},
                               'thetaoga': {'field_ref': 'temptot',
                                            'name': 'thetaoga'}},
                    'id': 'file8',
                    'name_suffix': '_scalar',
                    'type': 'one_file'},
           },
           'id': '1m',
           'output_freq': '1mo',
           'output_level': '10',
           'split_freq': '1mo'},
    '1ts': {'enabled': '.TRUE.',
            'files': {},
            'id': '1ts',
            'output_freq': '1ts',
            'output_level': '10'},
    '1y': {'enabled': '.TRUE.',
           'files': {},
           'id': '1y',
           'output_freq': '1y',
           'output_level': '10'},
    '2h': {'enabled': '.TRUE.',
           'files': {},
           'id': '2h',
           'output_freq': '2h',
           'output_level': '10'},
    '2m': {'enabled': '.TRUE.',
           'files': {},
           'id': '2m',
           'output_freq': '2mo',
           'output_level': '10'},
    '2y': {'enabled': '.TRUE.',
           'files': {},
           'id': '2y',
           'output_freq': '2y',
           'output_level': '10'},
    '3h': {'enabled': '.TRUE.',
           'files': {},
           'id': '3h',
           'output_freq': '3h',
           'output_level': '10'},
    '3m': {'enabled': '.TRUE.',
           'files': {},
           'id': '3m',
           'output_freq': '3mo',
           'output_level': '10'},
    '4h': {'enabled': '.TRUE.',
           'files': {},
           'id': '4h',
           'output_freq': '4h',
           'output_level': '10'},
    '4m': {'enabled': '.TRUE.',
           'files': {},
           'id': '4m',
           'output_freq': '4mo',
           'output_level': '10'},
    '5y': {'enabled': '.TRUE.',
           'files': {},
           'id': '5y',
           'output_freq': '5y',
           'output_level': '10'},
    '6h': {'enabled': '.TRUE.',
           'files': {},
           'id': '6h',
           'output_freq': '6h',
           'output_level': '10'},
    '6m': {'enabled': '.TRUE.',
           'files': {},
           'id': '6m',
           'output_freq': '6mo',
           'output_level': '10'}
}
MEDUSA_FIELD_GROUPS_XML = '''
        <file id="file11" name_suffix="_ptrc_T"
        description="Medusa sms variables" >
          <field field_ref="e3t" name="thkcello"
          standard_name="cell_thickness" />
          <field_group group_ref="groupMEDUSA" enabled=".TRUE."  />
        </file>

        <file id="file12" name_suffix="_diad_T"
        description="Medusa diagnostic variables" >
          <field field_ref="e3t" name="thkcello"
          standard_name="cell_thickness" />
          <field_group group_ref="groupMEDUSA_dia"   enabled=".TRUE."  />
        </file>
'''

MEDUSA_FG_FILE_KEY = '1m'
MEDUSA_FIELD_GROUPS_DICT = {
    'file11': {'description': 'Medusa sms variables',
               'field_groups':
                   {'groupMEDUSA': {'group_ref': 'groupMEDUSA',
                                    'enabled': True}},
               'fields': {'thkcello': {'field_ref': 'e3t',
                                       'name': 'thkcello',
                                       'standard_name': 'cell_thickness'}},
               'id': 'file11',
               'name_suffix': '_ptrc_T', },
    'file12': {'description': 'Medusa diagnostic variables',
               'field_groups': {
                   'groupMEDUSA_dia': {'group_ref': 'groupMEDUSA_dia',
                                       'enabled': True}},
               'fields': {'thkcello': {'field_ref': 'e3t',
                                       'name': 'thkcello',
                                       'standard_name': 'cell_thickness'}},
               'id': 'file12',
               'name_suffix': '_diad_T'},
}

ENABLED_VARS_TEST = {
    'ond/sozocrtx': {'enabled': True},
    'ond/sozotaux': {'enabled': True},
    'ond/sstmax': {'enabled': True},
    'ond/sstmin': {'enabled': True},
    'ond/tos': {'enabled': True},
    'onm/masscello': {'enabled': True},
    'onm/scvoltot': {'enabled': True},
    'onm/soga': {'enabled': True},
    'onm/thetaoga': {'enabled': True},
    'onm/thkcello': {'enabled': True}
}


FIELD_DEF_XML = '''<?xml version="1.0"?>
   <field_definition level="1" prec="8" operation="average"
   enabled=".TRUE." default_value="1.e20" >

    <field_group id="groupMEDUSA" >
      <field field_ref="CHN"      name="CHN"      />
      <field field_ref="CHN_E3T"  name="CHN_E3T"      />
      <field field_ref="CHD"      name="CHD"      />
      <field field_ref="CHD_E3T"  name="CHD_E3T"      />
      <field field_ref="PHN"      name="PHN"      />
      <field field_ref="PHN_E3T"  name="PHN_E3T"      />
   </field_group>

    <field_group id="groupMEDUSA_surf" >
      <field field_ref="SURF_CHN" name="SURF_CHN"  />
      <field field_ref="SURF_OXY" name="SURF_OXY"  />
    </field_group>


    <field_group id="groupMEDUSA_dia" >
      <field field_ref= "INVTN"      name="INVTN"      />
      <field field_ref= "INVTSI"     name="INVTSI"     />
      <field field_ref= "INVTFE"     name="INVTFE"     />
      <field field_ref= "PRN"        name="PRN"        />
      <field field_ref= "MPN"        name="MPN"        />
      <field field_ref= "PRD"        name="PRD"        />
      <field field_ref= "MPD"        name="MPD"        />
      <field field_ref= "OPAL"       name="OPAL"       />
      <field field_ref= "CHL_MLD"    name="CHL_MLD"    />
    </field_group>

    <field_group id="groupMEDUSA_cpl" >
      <field field_ref= "CHL_CPL"    name="CHL_CPL"    />
      <field field_ref= "FGCO2"      name="FGCO2_CPL"  />
      <field field_ref= "DMS_SURF"   name="DMS_CPL"    />
      <field field_ref= "ATM_XCO2"   name="AXCO2_CPL"  />
      <field field_ref= "AEOLIAN"    name="DUST_CPL"   />
    </field_group>

    <field_group id="groupMEDUSA_cmip6" >
      <field field_ref= "epC100"     name="epC100"     />
      <field field_ref= "epN100"     name="epN100"     />
      <field field_ref= "epSI100"    name="epSI100"    />
      <field field_ref= "O2min"      name="O2min"      />
      <field field_ref= "ZO2min"     name="ZO2min"     />
    </field_group>

</field_definition>

'''
FIELD_DEF_CFG = {
    'groupMEDUSA': {'fields': {'CHD': {'field_ref': 'CHD', 'name': 'CHD'},
                               'CHD_E3T': {'field_ref': 'CHD_E3T',
                                           'name': 'CHD_E3T'},
                               'CHN': {'field_ref': 'CHN', 'name': 'CHN'},
                               'CHN_E3T': {'field_ref': 'CHN_E3T',
                                           'name': 'CHN_E3T'},
                               'PHN': {'field_ref': 'PHN', 'name': 'PHN'},
                               'PHN_E3T': {'field_ref': 'PHN_E3T',
                                           'name': 'PHN_E3T'}},
                    'id': 'groupMEDUSA'},
    'groupMEDUSA_cmip6': {'fields': {'O2min': {'field_ref': 'O2min',
                                               'name': 'O2min'},
                                     'ZO2min': {'field_ref': 'ZO2min',
                                                'name': 'ZO2min'},
                                     'epC100': {'field_ref': 'epC100',
                                                'name': 'epC100'},
                                     'epN100': {'field_ref': 'epN100',
                                                'name': 'epN100'},
                                     'epSI100': {'field_ref': 'epSI100',
                                                 'name': 'epSI100'}},
                          'id': 'groupMEDUSA_cmip6'},
    'groupMEDUSA_cpl': {'fields': {'AEOLIAN': {'field_ref': 'AEOLIAN',
                                               'name': 'DUST_CPL'},
                                   'ATM_XCO2': {'field_ref': 'ATM_XCO2',
                                                'name': 'AXCO2_CPL'},
                                   'CHL_CPL': {'field_ref': 'CHL_CPL',
                                               'name': 'CHL_CPL'},
                                   'DMS_SURF': {'field_ref': 'DMS_SURF',
                                                'name': 'DMS_CPL'},
                                   'FGCO2': {'field_ref': 'FGCO2',
                                             'name': 'FGCO2_CPL'}},
                        'id': 'groupMEDUSA_cpl'},
    'groupMEDUSA_dia': {'fields': {'CHL_MLD': {'field_ref': 'CHL_MLD',
                                               'name': 'CHL_MLD'},
                                   'INVTFE': {'field_ref': 'INVTFE',
                                              'name': 'INVTFE'},
                                   'INVTN': {'field_ref': 'INVTN',
                                             'name': 'INVTN'},
                                   'INVTSI': {'field_ref': 'INVTSI',
                                              'name': 'INVTSI'},
                                   'MPD': {'field_ref': 'MPD', 'name': 'MPD'},
                                   'MPN': {'field_ref': 'MPN', 'name': 'MPN'},
                                   'OPAL': {'field_ref': 'OPAL',
                                            'name': 'OPAL'},
                                   'PRD': {'field_ref': 'PRD', 'name': 'PRD'},
                                   'PRN': {'field_ref': 'PRN', 'name': 'PRN'}},
                        'id': 'groupMEDUSA_dia'},
    'groupMEDUSA_surf': {'fields': {'SURF_CHN': {'field_ref': 'SURF_CHN',
                                                 'name': 'SURF_CHN'},
                                    'SURF_OXY': {'field_ref': 'SURF_OXY',
                                                 'name': 'SURF_OXY'}},
                         'id': 'groupMEDUSA_surf'}
}

ROSE_APP_CONF_NEMO_CICE_TXT = '''meta=ocean_ice/GO6/nemo36_gsi8_v3

[command]
default=run_nemo_cice

[env]
CICE_START=/path/to/start_dumps/aw310i.restart.1960-01-01-00000.nc
NEMO_ICEBERGS_START=/path/to/start_dump/aw310o_icebergs_19600101_restart.nc
NEMO_NL=namelist_cfg
NEMO_RESTART_DATE=true
NEMO_SEPARATE_MEANS=true
NEMO_START=$OCEANDIR/hadgem3/initial/dumps/u-aw310/aw310o_19600101_restart.nc
NEMO_VERSION=306
OCEAN_EXEC=$CYLC_SUITE_SHARE_DIR/fcm_make_ocean/build-ocean/bin/nemo-cice.exe

[file:$DATAM]
mode=mkdir
source=

[file:domain_def.xml]
mode=symlink
source=$CYLC_SUITE_SHARE_DIR/fcm_make_ocean/build-ocean/etc/domain_def.xml

[file:field_def.xml]
mode=symlink
source=$CYLC_SUITE_SHARE_DIR/fcm_make_ocean/build-ocean/etc/field_def.xml

[file:ice_in]
source=namelist:domain_nml namelist:dynamics_nml

[file:iodef.xml]
mode=symlink
source={iodef_source_file}

[file:namelist_cfg]
mode=auto
source=namelist:namrun

[file:namelist_ref]
mode=auto
source=$CYLC_SUITE_SHARE_DIR/fcm_make_ocean/build-ocean/etc/namelist_ref

[file:subbasins.nc]
mode=symlink
source=$SUBBASINS

[namelist:domain_nml]
distribution_type='nemo'
distribution_wght='block'
ew_boundary_type='cyclic'
maskhalo_bound=.false.
maskhalo_dyn=.false.
maskhalo_remap=.false.
nprocs='set_by_system'
ns_boundary_type='tripole'
processor_shape='square-pop'

[namelist:dynamics_nml]
advection='remap'
kdyn=1
krdg_partic=1
krdg_redist=1
kstrength=1
mu_rdg=3.0
ndte=120
revised_evp=.false.

[namelist:namrun]
cn_exp='set_by_system'
cn_ocerst_in='restart'
cn_ocerst_indir='./'
cn_ocerst_out='restart'
cn_ocerst_outdir='$DATAM/NEMOhist/'
ln_cfmeta=.true.
ln_clobber=.true.
ln_dimgnnn=.false.
ln_mskland=.true.
ln_rstart=.true.
ln_rstdate=.true.
nn_chunksz=2097152
nn_date0='set_by_system'
nn_istate=0
nn_it000=1
nn_itend='set_by_system'
nn_leapy='set_by_system'
nn_no=0
nn_rstctl=0
nn_stock=2880
nn_write=320
'''


class TestCreateOceanEnabled(unittest.TestCase):
    """
    Tests for :func:`create_ocean_enabled` in
    :mod:`model_config.py`.
    """
    def setUp(self):
        load_plugin()
        # self.cice_variables and self.nemo_variables provide the
        # input variables specified in the model.
        self.cice_variables = {
            'ind/aice': {'enabled': True},  # for SIday/siconc
            'inm/aice': {'enabled': True},  # for SImon/siconc
            'inm/flat_ai': {'enabled': True},  # for SImon/sifllatstop
            'inm/vsnon': {'enabled': True},  # for SImon/siitdsnconc
        }
        self.nemo_variables = {
            'ond/tos': {'enabled': True},  # for Oday/tos
            'onm/berg_calve': {'enabled': True},  # for Emon/flandice
            'onm/ficeberg': {'enabled': True},  # for Omon/ficeberg
            'onm/obvfsq': {'enabled': True},  # for Omon/obvfsq
            'onm/sowflisf': {'enabled': True},  # for Emon/flandice
            'onm/thetao': {'enabled': True},  # for Omon/thetao
            'onm/tos': {'enabled': True},
            'onm/vowflisf': {'enabled': True},  # for Omon/ficeberg
        }
        self.medusa_variables = {
            'onm/phycos': {'enabled': True},
            'onm/zoocos': {'enabled': True},
            'onm/baccos': {'enabled': True},
            'onm/detocos': {'enabled': True},
            'onm/calcos': {'enabled': True},
            'onm/DIN_E3T': {'enabled': True},  # for Omon/no3os
            'onm/thkcello': {'enabled': True},  # for Omon/no3os
        }
        self.nemo_and_medusa_variables = {}
        self.nemo_and_medusa_variables.update(self.nemo_variables)
        self.nemo_and_medusa_variables.update(self.medusa_variables)

        self.mappings = {
            'Amon': {
                # Should be ignored.
                'tas': DummyMapping(
                    expression='m01s03i236[lbproc=128]',
                    mip_table_id=['Amon', 'day'])},
            'Eday': {
                # Input variable doesn't exist in model.
                'mlotst': DummyMapping(
                    expression='mlotst', mip_table_id=['Eday', 'Omon'])},
            'Emon': {
                # Input variables exist in model.
                'flandice': DummyMapping(
                    expression='sowflisf + berg_calve',
                    mip_table_id=['Emon'])},
            'Oday': {
                # Input variable exists in model.
                'tos': DummyMapping(
                    expression='tos', mip_table_id=['Oday', 'Omon'])},
            'Omon': {
                # Input variables exist in model.
                'ficeberg': DummyMapping(
                    expression='sum_2d_and_3d(ficeberg, -1*vowflisf)',
                    mip_table_id=['Eday', 'Omon']),
                # Input variables exist in model, expression has constraints.
                'no3os': DummyMapping(
                    expression='DIN_E3T[depth=0] / thkcello[depth=0]',
                    mip_table_id=['Omon']),
                # One input variable doesn't exist in model (mask_3D_T).
                # Note this is an ancillary; the check for this will be
                # added in ticket 642.
                'obvfsq': DummyMapping(
                    expression='mask_copy(obvfsq, mask_3D_T)',
                    mip_table_id=['Eday', 'Omon']),
                # Input variable doesn't exist in model, no
                # 'model to MIP mapping'.
                'thetao': Exception()},
            'SIday': {
                # Input variable exists in model, no 'model to MIP mapping'.
                'siconc': Exception()},
            'SImon': {
                # Input variable exists in model.
                'siconc': DummyMapping(
                    expression='aice', mip_table_id=['SImon']),
                # Should be ignored.
                'siconca': DummyMapping(
                    expression='m01s00i031[lbproc=128]',
                    mip_table_id=['SIday SImon']),
                # Input variables exist in model.
                'sifllatstop': DummyMapping(
                    expression='-1. * flat_ai / aice', mip_table_id=['SImon']),
                # One input variable doesn't exist in model (aicen).
                'siitdsnconc': DummyMapping(
                    expression='vsnon + aicen', mip_table_id=['SImon'])},
        }
        self.mip_era = 'CMIP6'
        self.suite_id = 'dummy'
        self.branch = 'dummy_branch'
        self.revision = -1
        self.expected = {
            'Eday/mlotst': {'enabled': [False]},  # doesn't exist in model
            'Emon/flandice': {'enabled': [True]},
            'Oday/tos': {'enabled': [True]},
            'Omon/ficeberg': {'enabled': [True]},
            'Omon/no3os': {'enabled': [True]},
            'Omon/obvfsq': {'enabled': [False]},  # missing mask_3D_t
            'Omon/thetao': {'enabled': [False]},  # no model to MIP mapping
            'SIday/siconc': {'enabled': [False]},  # no model to MIP mapping
            'SImon/siconc': {'enabled': [True]},
            'SImon/sifllatstop': {'enabled': [True]},
            'SImon/siitdsnconc': {'enabled': [False]},  # missing aicen
        }

    @patch('cdds_prepare.model_config._nemo_and_medusa_enabled')
    @patch('cdds_prepare.model_config._cice_enabled')
    def test_create_ocean_enabled(self, mock_cice_enabled,
                                  mock_nemo_and_medusa_enabled):
        mock_cice_enabled.return_value = self.cice_variables
        mock_nemo_and_medusa_enabled.return_value = (
            self.nemo_and_medusa_variables)
        dummy_model_type = 'AOGCM AER BGC CHEM'
        obgc_enabled = True
        result = create_ocean_enabled(
            self.mappings, self.mip_era, self.suite_id, self.branch,
            self.revision, dummy_model_type)

        mock_cice_enabled.assert_called_once_with(
            self.suite_id, self.branch, self.revision)
        mock_nemo_and_medusa_enabled.assert_called_once_with(
            self.suite_id, self.branch, self.revision, obgc_enabled)
        self.assertDictEqual(result, self.expected)

    def test_read_iodef_into_dict(self):
        dummy_path = '/path/to/iodef.xml'
        test_xml_str = IODEF_XML_CONTENTS.format(
            MEDUSA_FIELD_GROUPS='')
        with patch('builtins.open') as mock_open:
            mock_open.return_value = StringIO(dedent(test_xml_str))
            output_iodef_dict, groups_present = _read_iodef_into_dict(
                dummy_path, 2)
        expected_iodef_dict = deepcopy(IODEF_TEST_DICT)
        self.assertFalse(groups_present)
        self.assertEqual(expected_iodef_dict, output_iodef_dict)

    def test_read_iodef_into_dict_with_medusa(self):
        dummy_path = '/path/to/iodef.xml'
        test_xml_str = IODEF_XML_CONTENTS.format(
            MEDUSA_FIELD_GROUPS=MEDUSA_FIELD_GROUPS_XML)
        with patch('builtins.open') as mock_open:
            mock_open.return_value = StringIO(dedent(test_xml_str))
            output_iodef_dict, groups_present = _read_iodef_into_dict(
                dummy_path, 2)
        expected_iodef_dict = deepcopy(IODEF_TEST_DICT)
        expected_iodef_dict[MEDUSA_FG_FILE_KEY]['files'].update(
            deepcopy(MEDUSA_FIELD_GROUPS_DICT))
        self.assertTrue(groups_present)
        self.assertEqual(expected_iodef_dict, output_iodef_dict)

    def test_read_field_def_xml_into_dict(self):
        dummy_path = '/dummy/path/to/field_def.xml'
        with patch('builtins.open') as mock_open:
            mock_open.return_value = StringIO(dedent(FIELD_DEF_XML))
            output_cfg = _read_field_def_xml_into_dict(dummy_path, 0)
        self.assertEqual(FIELD_DEF_CFG, output_cfg)

    @patch('cdds_prepare.model_config.export_file_from_suite')
    def test_get_iodef_filename_in_suite(self, mock_export_file):
        mock_export_file.return_value = '/path/to/temp/dir'
        dummy_path = '/dummy/path/to/field_def.xml'
        dummy_suite_id = 'u-zz000'
        dummy_branch = 'dummy_branch'
        dummy_rev = '0000'
        expected_iodef_fname = 'iodef_main.xml'
        with patch('builtins.open') as mock_open:
            conf_txt = ROSE_APP_CONF_NEMO_CICE_TXT.format(
                iodef_source_file=expected_iodef_fname)
            mock_open.return_value = StringIO(dedent(conf_txt))
            output_iodef_fname = _get_iodef_filename_in_suite(dummy_suite_id,
                                                              dummy_branch,
                                                              dummy_rev)
        self.assertEqual(expected_iodef_fname, output_iodef_fname)

    def test_construct_enabled_var_from_iodef(self):
        output_enabled_vars = \
            _construct_enabled_var_from_iodef(IODEF_TEST_DICT)
        expected = ENABLED_VARS_TEST
        self.assertEqual(expected, dict(output_enabled_vars))

    def test_expand_field_groups(self):
        test_iodef_dict = deepcopy(IODEF_TEST_DICT)
        test_iodef_dict[MEDUSA_FG_FILE_KEY]['files'].update(
            deepcopy(MEDUSA_FIELD_GROUPS_DICT))
        expected_iodef_dict = deepcopy(test_iodef_dict)

        expected_iodef_dict[MEDUSA_FG_FILE_KEY]['files']['file11'][
            'fields'].update(deepcopy(FIELD_DEF_CFG['groupMEDUSA']['fields']))
        expected_iodef_dict[MEDUSA_FG_FILE_KEY]['files']['file12'][
            'fields'].update(
            deepcopy(FIELD_DEF_CFG['groupMEDUSA_dia']['fields']))
        output_iodef_dict = _expand_field_groups(test_iodef_dict,
                                                 FIELD_DEF_CFG)

        self.assertEqual(expected_iodef_dict, output_iodef_dict)

    @patch('cdds_prepare.model_config.run_command')
    @patch('hadsdk.common.determine_rose_suite_url')
    @patch('tempfile.mkdtemp')
    def test_export_file_from_suite(self, patch_mkdtemp, mock_det_suite_url,
                                    mock_run_cmd):
        expected_path = '/dummy/path/'
        patch_mkdtemp.return_value = expected_path
        mock_det_suite_url.return_value = 'svn://fcm1/roses-u.xm_svn/z/z/1/2/3'
        suite_id = 'u-zz123'
        branch = 'dummy'
        filename = 'dummy.conf'
        rev_no = 1234
        output_path = export_file_from_suite(suite_id, branch, filename,
                                             rev_no)
        self.assertEqual(expected_path, output_path)


if __name__ == '__main__':
    unittest.main()
