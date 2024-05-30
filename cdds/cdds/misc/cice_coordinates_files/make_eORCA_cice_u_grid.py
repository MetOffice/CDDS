# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
"""
make_eORCA_cice_u_grid.py

Construct CICE ORCA U grids from the T grid bounds.
"""
import argparse

from netCDF4 import Dataset
import numpy as np


def build_u_coord_from_t(rootgrp, coord_name, bounds_name):
    """
    From the netCDF file construct the U coordinate.
    """
    tp = rootgrp[coord_name][:].copy()
    tb = rootgrp[bounds_name][:].copy()

    u_points = tb[:, :, 0].copy()

    u_bounds = np.zeros(tb.shape)

    u_bounds[:, :, 2] = tp.copy()
    u_bounds[:, :, 3] = np.roll(tp, 1, axis=1)
    pt_0_intermediate = np.roll(tp, 1, axis=0)
    u_bounds[:, :, 0] = np.roll(pt_0_intermediate, 1, axis=1)
    u_bounds[:, :, 1] = np.roll(tp, 1, axis=0)

    return u_points, u_bounds


def parse_args():
    """Collect the command line arguments"""
    parser = argparse.ArgumentParser(description="Construct ULAT and ULON values from the TLAT and TLON "
                                     "coordinates within the file supplied.")
    parser.add_argument(
        "coords_file", help=("The full path to the CICE coordinates file.")
    )
    args = parser.parse_args()
    return args


def main(args):
    """Main entry point"""
    rootgrp = Dataset(args.coords_file, "r+")

    # Create the points and bounds
    u_lat_points, u_lat_bounds = build_u_coord_from_t(rootgrp, "TLAT", "latt_bounds")
    u_lon_points, u_lon_bounds = build_u_coord_from_t(rootgrp, "TLON", "lont_bounds")

    # Add the variables to the file
    ulat = rootgrp.createVariable("ULAT", "f4", ("nj", "ni"))
    ulat.long_name = "U grid center latitude"
    ulat.standard_name = "latitude"
    ulat.units = "degrees_north"
    ulat.nav_model = "grid_U"
    ulat.bounds = "latu_bounds"
    ulat[:] = u_lat_points

    ulon = rootgrp.createVariable("ULON", "f4", ("nj", "ni"))
    ulon.long_name = "U grid center longitude"
    ulon.standard_name = "longitude"
    ulon.units = "degrees_east"
    ulon.nav_model = "grid_U"
    ulon.bounds = "lonu_bounds"
    ulon[:] = u_lon_points

    ulat_bnds = rootgrp.createVariable("latu_bounds", "f4", ("nj", "ni", "nvertices"))
    ulat_bnds[:] = u_lat_bounds

    ulon_bnds = rootgrp.createVariable("lonu_bounds", "f4", ("nj", "ni", "nvertices"))
    ulon_bnds[:] = u_lon_bounds

    rootgrp.close()


if __name__ == "__main__":
    args = parse_args()
    main(args)
