# (C) British Crown Copyright 2017-2021, Met Office.
# Please see LICENSE.rst for license details.

MIP_TABLES_DIR = "/home/h03/cdds/etc/mip_tables/CMIP6"
CORDEX_MIP_TABLES_DIR = "/net/home/h04/kschmatz/workspace/cordex-cmip6-cmor-tables/Tables"

CV_REPO = "/home/h03/cdds/etc/mip_tables/CMIP6/01.00.29/CMIP6_CV.json"
CORDEX_CV_REPO = "/net/home/h04/kschmatz/workspace/cordex-cmip6-cmor-tables/Tables/CORDEX_CV.json"

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
