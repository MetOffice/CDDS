# (C) British Crown Copyright 2019-2021, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = missing-docstring
"""
Items common to multiple test modules.
"""

RV_ACTIVE = [
    {'active': True, 'miptable': 'Amon', 'label': 'tas', 'frequency': 'mon', 'stream': 'ap5'},
    {'active': True, 'miptable': 'day', 'label': 'ua', 'frequency': 'day', 'stream': 'ap6'},
    {'active': True, 'miptable': 'Omon', 'label': 'tos', 'frequency': 'mon', 'stream': 'onm/grid-T'}]

DUMMY_VAR_OUT_DIR = '/path/to/dummy/data/outdir/'
APPROVED_VARIABLES_FILE_REFERENCE = [
    {'mip_table_id': 'Amon', 'variable_id': 'tas',
     'output_dir': DUMMY_VAR_OUT_DIR + 'stream1/Amon/tas',
     'out_var_name': 'tas'},
    {'mip_table_id': 'day', 'variable_id': 'ua',
     'output_dir': DUMMY_VAR_OUT_DIR + 'stream1/day/ua',
     'out_var_name': 'ua'},
    {'mip_table_id': 'Omon', 'variable_id': 'tos',
     'output_dir': DUMMY_VAR_OUT_DIR + 'stream1/Omon/tos',
     'out_var_name': 'tos'},
    {'mip_table_id': 'Emon', 'variable_id': 'hus27',
     'output_dir': DUMMY_VAR_OUT_DIR + 'stream1/Emon/hus',
     'out_var_name': 'hus'},
]

ACTIVE_VARS_REFERENCE = [
    {'mip_table_id': 'Amon', 'variable_id': 'tas', 'frequency': 'mon', 'stream': 'ap5'},
    {'mip_table_id': 'day', 'variable_id': 'ua', 'frequency': 'day', 'stream': 'ap6'},
    {'mip_table_id': 'Omon', 'variable_id': 'tos', 'frequency': 'mon', 'stream': 'onm/grid-T'}]

APPROVED_REF_WITH_STREAM = [
    {'mip_table_id': 'Amon', 'variable_id': 'tas', 'stream_id': 'ap5',
     'frequency': 'mon', 'output_dir': DUMMY_VAR_OUT_DIR + 'ap5/Amon/tas',
     'out_var_name': 'tas'},
    {'mip_table_id': 'day', 'variable_id': 'ua', 'stream_id': 'ap6',
     'frequency': 'day', 'output_dir': DUMMY_VAR_OUT_DIR + 'ap6/day/ua',
     'out_var_name': 'ua'},
    {'mip_table_id': 'Omon', 'variable_id': 'tos', 'stream_id': 'onm',
     'frequency': 'mon', 'output_dir': DUMMY_VAR_OUT_DIR + 'onm/Omon/tos',
     'out_var_name': 'tos'},
    {'mip_table_id': 'Emon', 'variable_id': 'hus27', 'stream_id': 'ap5',
     'frequency': 'mon', 'output_dir': DUMMY_VAR_OUT_DIR + 'ap5/Emon/hus',
     'out_var_name': 'hus'},
]

APPROVED_REF_WITH_FILES = [
    {'stream_id': 'ap5',
     'variable_id': 'tas',
     'mip_table_id': 'Amon',
     'frequency': 'mon',
     'mip_output_files': ['/path/to/output/data/ap5/Amon/tas/tas_Amon_'
                          'dummymodel_dummyexp_dummyvariant_dummygrid_'
                          '20010101-20491230.nc']
     },
    {'stream_id': 'ap6',
     'variable_id': 'ua',
     'mip_table_id': 'day',
     'frequency': 'day',
     'mip_output_files':
         ['/path/to/output/data/ap6/day/ua/ua_day_dummymodel_'
          'dummyexp_dummyvariant_dummygrid_20010101-20491230.nc']
     },
    {'stream_id': 'onm',
     'variable_id': 'tos',
     'mip_table_id': 'Omon',
     'frequency': 'mon',
     'mip_output_files': ['/path/to/output/data/onm/Omon/tos/tos_Omon_'
                          'dummymodel_dummyexp_dummyvariant_dummygrid_'
                          '20010101-20491230.nc']
     }]

OLD_DATESTAMP = 'v20100308'
APPROVED_NEW_DATESTAMP = 'v20100613'
APPROVED_REF_WITH_MASS = [
    {'variable_id': 'tas',
     'stream_id': 'ap5',
     'mass_path': 'moose://root/mass/location/tas',
     'mip_table_id': 'Amon',
     'mass_status': 'FIRST_PUBLICATION',
     'frequency': 'mon',
     'new_datestamp': APPROVED_NEW_DATESTAMP,
     'mass_status_suffix': 'embargoed/' + APPROVED_NEW_DATESTAMP,
     'mip_output_files': [
         '/path/to/output/data/ap5/Amon/tas/tas_Amon_dummymodel_dummyexp_'
         'dummyvariant_dummygrid_200101-201912.nc',
         '/path/to/output/data/ap5/Amon/tas/tas_Amon_dummymodel_dummyexp_'
         'dummyvariant_dummygrid_202001-203912.nc',
         '/path/to/output/data/ap5/Amon/tas/tas_Amon_dummymodel_dummyexp_'
         'dummyvariant_dummygrid_204001-205912.nc',
     ]},
    {'variable_id': 'ua',
     'stream_id': 'ap6',
     'mass_path': 'moose://root/mass/location/ua',
     'mip_table_id': 'day',
     'mass_status': 'FIRST_PUBLICATION',
     'frequency': 'day',
     'new_datestamp': APPROVED_NEW_DATESTAMP,
     'mass_status_suffix': 'embargoed/' + APPROVED_NEW_DATESTAMP,
     'mip_output_files': [
         '/path/to/output/data/ap6/day/ua/ua_day_dummymodel_dummyexp_'
         'dummyvariant_dummygrid_20010101-20091230.nc',
         '/path/to/output/data/ap6/day/ua/ua_day_dummymodel_dummyexp_'
         'dummyvariant_dummygrid_20110101-20191230.nc',
         '/path/to/output/data/ap6/day/ua/ua_day_dummymodel_dummyexp_'
         'dummyvariant_dummygrid_20200101-20291230.nc',
         '/path/to/output/data/ap6/day/ua/ua_day_dummymodel_dummyexp_'
         'dummyvariant_dummygrid_20300101-20391230.nc',
         '/path/to/output/data/ap6/day/ua/ua_day_dummymodel_dummyexp_'
         'dummyvariant_dummygrid_20400101-20491230.nc',
         '/path/to/output/data/ap6/day/ua/ua_day_dummymodel_dummyexp_'
         'dummyvariant_dummygrid_20500101-20591230.nc',
     ]},
    {'variable_id': 'tos',
     'stream_id': 'onm',
     'mass_path': 'moose://root/mass/location/tos',
     'mass_status': 'FIRST_PUBLICATION',
     'mip_table_id': 'Omon',
     'frequency': 'mon',
     'new_datestamp': APPROVED_NEW_DATESTAMP,
     'mass_status_suffix': 'embargoed/' + APPROVED_NEW_DATESTAMP,
     'mip_output_files': [
         '/path/to/output/data/onm/Omon/tos/tos_Omon_dummymodel_dummyexp_'
         'dummyvariant_dummygrid_200101-201912.nc',
         '/path/to/output/data/onm/Omon/tos/tos_Omon_dummymodel_dummyexp_'
         'dummyvariant_dummygrid_202001-203912.nc',
         '/path/to/output/data/onm/Omon/tos/tos_Omon_dummymodel_dummyexp_'
         'dummyvariant_dummygrid_204001-205912.nc',
     ]},
]
