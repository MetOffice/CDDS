# (C) British Crown Copyright 2017-2025, Met Office.
# Please see LICENSE.md for license details.
import os

MIP_TABLES_DIR = os.path.join(os.environ['CDDS_ETC'], 'mip_tables', 'CMIP6')
CORDEX_MIP_TABLES_DIR = os.path.join(os.environ['CDDS_ETC'], 'mip_tables', 'CORDEX', 'for_unit_tests')

CV_REPO = os.path.join(os.environ['CDDS_ETC'], 'mip_tables', 'CMIP6', '01.00.29', 'CMIP6_CV.json')
CORDEX_CV_REPO = os.path.join(os.environ['CDDS_ETC'], 'mip_tables', 'CORDEX', 'for_unit_tests', 'CORDEX_CV.json')

TMP_DIR_FOR_NETCDF_TESTS = '/var/tmp'

MINIMAL_CDL = """
netcdf filename {
dimensions:
    lat = 1 ;
    lon = 1 ;
    time = UNLIMITED ; // (1 currently)
variables:
    double lat(lat) ;
    double lon(lon) ;
    float rsut(time, lat, lon) ;
    double time(time) ;

// global attributes:
    :Conventions = "CF-1.7 CMIP-6.2" ;
data:
 lat = -89.375 ;
 lon = 0.9375 ;
 rsut = 213.0 ;
 time = 45 ;
}
"""

CORRECT_VARIABLE_METADATA_CDL = """
netcdf filename {
dimensions:
    lat = 1 ;
    lon = 1 ;
    time = UNLIMITED ; // (1 currently)
variables:
    double lat(lat) ;
    double lon(lon) ;
    float rsut(time, lat, lon) ;
            rsut:frequency = "mon" ;
            rsut:modeling_realm = "atmos" ;
            rsut:standard_name = "toa_outgoing_shortwave_flux" ;
            rsut:units = "W m-2" ;
            rsut:cell_methods = "area: time: mean" ;
            rsut:cell_measures = "area: areacella" ;
            rsut:long_name = "TOA Outgoing Shortwave Radiation" ;
            rsut:comment = "at the top of the atmosphere" ;
            rsut:dimensions = "longitude latitude time" ;
            rsut:out_name = "rsut" ;
            rsut:type = "real" ;
            rsut:positive = "up" ;
            rsut:missing_value = 1.e+20 ;
            rsut:_FillValue = 1.e+20 ;
            rsut:original_name = "foo" ;
    double time(time) ;

// global attributes:
    :Conventions = "CF-1.7 CMIP-6.2" ;
    :external_variables = "areacella" ;
data:
 lat = -89.375 ;
 lon = 0.9375 ;
 rsut = 213.0 ;
 time = 45 ;
}
"""

MISSING_VARIABLE_METADATA_CDL = """
netcdf filename {
dimensions:
    lat = 1 ;
    lon = 1 ;
    time = UNLIMITED ; // (1 currently)
variables:
    double lat(lat) ;
    double lon(lon) ;
    float rsut(time, lat, lon) ;
            rsut:frequency = "mon" ;
            rsut:modeling_realm = "atmos" ;
            rsut:units = "W m-2" ;
            rsut:cell_methods = "area: time: mean" ;
            rsut:cell_measures = "area: areacella" ;
            rsut:long_name = "TOA Outgoing Shortwave Radiation" ;
            rsut:comment = "at the top of the atmosphere" ;
            rsut:dimensions = "longitude latitude time" ;
            rsut:out_name = "rsut" ;
            rsut:type = "real" ;
            rsut:positive = "up" ;
            rsut:missing_value = 1.e+20 ;
            rsut:_FillValue = 1.e+20 ;
            rsut:original_name = "foo" ;
    double time(time) ;

// global attributes:
    :Conventions = "CF-1.7 CMIP-6.2" ;
    :external_variables = "areacella" ;
data:
 lat = -89.375 ;
 lon = 0.9375 ;
 rsut = 213.0 ;
 time = 45 ;
}
"""

INCONSISTENT_VARIABLE_METADATA_CDL = """
netcdf filename {
dimensions:
    lat = 1 ;
    lon = 1 ;
    time = UNLIMITED ; // (1 currently)
variables:
    double lat(lat) ;
    double lon(lon) ;
    float rsut(time, lat, lon) ;
            rsut:frequency = "mon" ;
            rsut:modeling_realm = "atmos" ;
            rsut:standard_name = "toa_outgoing_shortwave_flux" ;
            rsut:units = "K" ;
            rsut:cell_methods = "area: time: mean" ;
            rsut:cell_measures = "area: areacella" ;
            rsut:long_name = "TOA Outgoing Shortwave Radiation" ;
            rsut:comment = "at the top of the atmosphere" ;
            rsut:dimensions = "longitude latitude time" ;
            rsut:out_name = "rsut" ;
            rsut:type = "real" ;
            rsut:positive = "up" ;
            rsut:missing_value = 1.e+20 ;
            rsut:_FillValue = 1.e+20 ;
            rsut:original_name = "foo" ;
    double time(time) ;

// global attributes:
    :Conventions = "CF-1.7 CMIP-6.2" ;
    :external_variables = "areacella" ;
data:
 lat = -89.375 ;
 lon = 0.9375 ;
 rsut = 213.0 ;
 time = 45 ;
}
"""

GLOBAL_ATTRIBUTES_CDL = """
netcdf filename {
dimensions:
    lat = 1 ;
    lon = 1 ;
    time = UNLIMITED ; // (1 currently)
variables:
    double lat(lat) ;
    double lon(lon) ;
    float rsut(time, lat, lon) ;
            rsut:frequency = "mon" ;
            rsut:modeling_realm = "atmos" ;
            rsut:standard_name = "toa_outgoing_shortwave_flux" ;
            rsut:units = "W m-2" ;
            rsut:cell_methods = "area: time: mean" ;
            rsut:cell_measures = "area: areacella" ;
            rsut:long_name = "TOA Outgoing Shortwave Radiation" ;
            rsut:comment = "at the top of the atmosphere" ;
            rsut:dimensions = "longitude latitude time" ;
            rsut:out_name = "rsut" ;
            rsut:type = "real" ;
            rsut:positive = "up" ;
            rsut:missing_value = 1.e+20 ;
            rsut:_FillValue = 1.e+20 ;
            rsut:original_name = "foo" ;
    double time(time) ;

// global attributes:
    :Conventions = "CF-1.7 CMIP-6.2" ;
    :activity_id = "CMIP" ;
    :branch_method = "standard" ;
    :branch_time_in_child = 0. ;
    :branch_time_in_parent = 72000. ;
    :creation_date = "2022-02-31T21:16:47Z" ;
    :cv_version = "6.2.37.5" ;
    :data_specs_version = "01.00.29" ;
    :experiment = "all-forcing simulation of the recent past" ;
    :experiment_id = "historical" ;
    :external_variables = "areacella" ;
    :forcing_index = 3 ;
    :frequency = "day" ;
    :further_info_url = "https://furtherinfo.es-doc.org/CMIP6.MOHC.UKESM1-0-LL.historical.none.r6i1p1f3" ;
    :grid = "Native N96 grid; 192 x 144 longitude/latitude" ;
    :grid_label = "gn" ;
    :history = "" ;
    :initialization_index = 1 ;
    :institution = "Met Office Hadley Centre, Fitzroy Road, Exeter, Devon, EX1 3PB, UK" ;
    :institution_id = "MOHC" ;
    :mip_era = "CMIP6" ;
    :mo_runid = "u-az515" ;
    :nominal_resolution = "250 km" ;
    :parent_activity_id = "CMIP" ;
    :parent_experiment_id = "piControl" ;
    :parent_mip_era = "CMIP6" ;
    :parent_source_id = "UKESM1-0-LL" ;
    :parent_time_units = "days since 1850-01-01" ;
    :parent_variant_label = "r1i1p1f2" ;
    :physics_index = 1 ;
    :product = "model-output" ;
    :realization_index = 6 ;
    :realm = "atmos" ;
    :source = "UKESM1.0-LL (2018)" ;
    :source_id = "UKESM1-0-LL" ;
    :source_type = "AOGCM AER BGC CHEM" ;
    :sub_experiment = "none" ;
    :sub_experiment_id = "none" ;
    :table_id = "day" ;
    :table_info = "Creation Date:(13 December 2018) MD5:f0588f7f55b5732b17302f8d9d0d7b8c" ;
    :title = "UKESM1-0-LL output prepared for CMIP6" ;
    :variable_id = "rsut" ;
    :variable_name = "rsut" ;
    :variant_label = "r6i1p1f3" ;
    :license = "CMIP6 model data produced by the Met Office Hadley Centre." ;
    :cmor_version = "3.4.0" ;
    :tracking_id = "hdl:21.14100/60dc0e7f-c2d2-4d50-b578-5c93bca6ff51" ;

data:
 lat = -89.375 ;
 lon = 0.9375 ;
 rsut = 213.0 ;
 time = 45 ;
}
"""
