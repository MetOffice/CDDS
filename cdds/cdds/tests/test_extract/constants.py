# (C) British Crown Copyright 2018-2021, Met Office.
# Please see LICENSE.rst for license details.

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

MINIMAL_CDL_NEMO = """
netcdf filename {
dimensions:
    lat = 1 ;
    lon = 1 ;
    time_counter = UNLIMITED ; // (1 currently)
variables:
    double lat(lat) ;
    double lon(lon) ;
    float rsut(time_counter, lat, lon) ;
    double time_counter(time_counter) ;

// global attributes:
    :Conventions = "CF-1.7 CMIP-6.2" ;
data:
 lat = -89.375 ;
 lon = 0.9375 ;
 rsut = 213.0 ;
 time_counter = 45 ;
}
"""

MINIMAL_CDL_NO_DATA = """
netcdf filename {
dimensions:
    lat = 1 ;
    lon = 1 ;
    time = UNLIMITED ; // (0 currently)
variables:
    double lat(lat) ;
    double lon(lon) ;
    float rsut(time, lat, lon) ;
    double time(time) ;

// global attributes:
    :Conventions = "CF-1.7 CMIP-6.2" ;
}
"""

MINIMAL_CDL_NO_DATA_NEMO = """
netcdf filename {
dimensions:
    lat = 1 ;
    lon = 1 ;
    time_counter = UNLIMITED ; // (0 currently)
variables:
    double lat(lat) ;
    double lon(lon) ;
    float rsut(time_counter, lat, lon) ;
    double time_counter(time_counter) ;

// global attributes:
    :Conventions = "CF-1.7 CMIP-6.2" ;
}
"""


GRID_V_CDL = """
netcdf nemo_as371o_1m_19000101-19000201_grid-V {
dimensions:
    y = {{ Y }} ;
    x = {{ X }} ;
    time_counter = UNLIMITED ; // (1 currently)
    depthv = 2 ;
variables:
    float nav_lat(y, x) ;
        nav_lat:standard_name = "latitude" ;
        nav_lat:long_name = "Latitude" ;
        nav_lat:units = "degrees_north" ;
        nav_lat:nav_model = "grid_V" ;
        nav_lat:bounds = "bounds_lat" ;
    float nav_lon(y, x) ;
        nav_lon:standard_name = "longitude" ;
        nav_lon:long_name = "Longitude" ;
        nav_lon:units = "degrees_east" ;
        nav_lon:nav_model = "grid_V" ;
        nav_lon:bounds = "bounds_lon" ;
    float depthv(depthv) ;
        depthv:standard_name = "depth" ;
        depthv:long_name = "Vertical V levels" ;
        depthv:units = "m" ;
        depthv:axis = "Z" ;
        depthv:positive = "down" ;
        depthv:bounds = "depthv_bounds" ;
    double time_counter(time_counter) ;
        time_counter:axis = "T" ;
    float hfy(time_counter, y, x) ;
        hfy:standard_name = "ocean_heat_y_transport" ;
        hfy:long_name = "Ocean Heat X Transport" ;
        hfy:units = "W" ;
        hfy:online_operation = "average" ;
        hfy:interval_operation = "2700 s" ;
        hfy:interval_write = "1 month" ;
        hfy:cell_methods = "time: mean (interval: 2700 s)" ;
        hfy:cell_measures = "area: area" ;
        hfy:_FillValue = 1.e+20f ;
        hfy:missing_value = 1.e+20f ;
        hfy:coordinates = "time_centered nav_lat nav_lon";
    float vo(time_counter, depthv, y, x) ;
        vo:standard_name = "sea_water_y_velocity" ;
        vo:long_name = "Sea Water Y Velocity" ;
        vo:units = "m/s" ;
        vo:online_operation = "average" ;
        vo:interval_operation = "2700 s" ;
        vo:interval_write = "1 month" ;
        vo:cell_methods = "time: mean" ;
        vo:cell_measures = "area: area" ;
        vo:_FillValue = 1.e+20f ;
        vo:missing_value = 1.e+20f ;
        vo:coordinates = "time_centered depthv nav_lat nav_lon";

// global attributes:
        :name = "as371o_1m_19000101_19000330" ;
        :description = "ocean V grid variables" ;
        :title = "ocean V grid variables" ;
        :Conventions = "CF-1.5" ;
        :production = "An IPSL model" ;
        :timeStamp = "2017-Dec-11 22:05:37 GMT" ;
        :NCO = "4.3.2" ;
data:

    nav_lat =
        {{ data }} ;
    nav_lon =
        {{ data }} ;
    time_counter = 0 ;

    hfy =
        {{ data }} ;
    vo =
        {{ data }} ;
}
"""

GRID_U_CDL = """
netcdf nemo_as371o_1m_19000101-19000201_grid-U {
dimensions:
    y = {{ Y }} ;
    x = {{ X }} ;
    time_counter = UNLIMITED ; // (1 currently)
    depthu = 2 ;
variables:
    float nav_lat(y, x) ;
        nav_lat:standard_name = "latitude" ;
        nav_lat:long_name = "Latitude" ;
        nav_lat:units = "degrees_north" ;
        nav_lat:nav_model = "grid_U" ;
        nav_lat:bounds = "bounds_lat" ;
    float nav_lon(y, x) ;
        nav_lon:standard_name = "longitude" ;
        nav_lon:long_name = "Longitude" ;
        nav_lon:units = "degrees_east" ;
        nav_lon:nav_model = "grid_U" ;
        nav_lon:bounds = "bounds_lon" ;
    float depthu(depthu) ;
        depthu:standard_name = "depth" ;
        depthu:long_name = "Vertical U levels" ;
        depthu:units = "m" ;
        depthu:axis = "Z" ;
        depthu:positive = "down" ;
        depthu:bounds = "depthu_bounds" ;
    double time_counter(time_counter) ;
        time_counter:axis = "T" ;
    float hfx(time_counter, y, x) ;
        hfx:standard_name = "ocean_heat_x_transport" ;
        hfx:long_name = "Ocean Heat X Transport" ;
        hfx:units = "W" ;
        hfx:online_operation = "average" ;
        hfx:interval_operation = "2700 s" ;
        hfx:interval_write = "1 month" ;
        hfx:cell_methods = "time: mean (interval: 2700 s)" ;
        hfx:cell_measures = "area: area" ;
        hfx:_FillValue = 1.e+20f ;
        hfx:missing_value = 1.e+20f ;
        hfx:coordinates = "time_centered nav_lat nav_lon";
    float uo(time_counter, depthu, y, x) ;
        uo:standard_name = "sea_water_x_velocity" ;
        uo:long_name = "Sea Water X Velocity" ;
        uo:units = "m/s" ;
        uo:online_operation = "average" ;
        uo:interval_operation = "2700 s" ;
        uo:interval_write = "1 month" ;
        uo:cell_methods = "time: mean" ;
        uo:cell_measures = "area: area" ;
        uo:_FillValue = 1.e+20f ;
        uo:missing_value = 1.e+20f ;
        uo:coordinates = "time_centered depthu nav_lat nav_lon";

// global attributes:
        :name = "as371o_1m_19000101_19000330" ;
        :description = "ocean U grid variables" ;
        :title = "ocean U grid variables" ;
        :Conventions = "CF-1.5" ;
        :production = "An IPSL model" ;
        :timeStamp = "2017-Dec-11 22:05:37 GMT" ;
        :NCO = "4.3.2" ;
data:

    nav_lat =
        {{ data }} ;
    nav_lon =
        {{ data }} ;
    time_counter = 0 ;

    hfx =
        {{ data }} ;
    uo =
        {{ data }} ;
}
"""
