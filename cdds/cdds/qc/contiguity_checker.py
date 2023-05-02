# (C) British Crown Copyright 2018-2022, Met Office.
# Please see LICENSE.rst for license details.


"""
Contiguity checker.
"""
from cdds.qc.plugins.cmip6.dataset import Cmip6Dataset
from cdds.qc.common import datepoint_from_date, equal_with_tolerance, strip_zeros
from cdds.qc.constants import (FREQ_DICT, HOURLY_OFFSET, MONTHLY_OFFSET, RADIATION_TIMESTEP, SECONDS_IN_DAY,
                               TIME_TOLERANCE)


class CollectionsCheck(object):
    """Time contiguity checker for a set of ncdf files."""

    name = "collections"
    supported_ds = [Cmip6Dataset]

    def __init__(self):
        """
        A constructor.
        """
        self.results = {}

    def perform_checks(self, ds):
        """
        Runs tests on a provided dataset.

        Parameters
        ----------
        ds: StructuredDataset
            A collection of netCDF files associated with a request.

        Returns
        -------
        : tuple
            Result of the tests.
        """
        if type(ds) not in self.supported_ds:
            raise Exception("Dataset {} is not of supported type.".format(ds))

        self.results = {}
        return self.check_time_contiguity(ds)

    def check_time_contiguity(self, ds):
        """
        Runs internal and external time contiguity checks.

        Parameters
        ----------
        ds: StructuredDataset
            A collection of netCDF files.

        Returns
        -------
        : tuple
            Result of the tests.
        """
        aggregated = ds.get_aggregated_files(False)

        # checks only if more than one file in the aggregated dict
        for var_key, filepaths in list(aggregated.items()):
            metadatas = self.check_variable(ds, var_key, filepaths)

            metadatas.sort(key=lambda x: x["time_dim"][0])

            run_bounds_check = self.check_run_bounds(
                ds.request, metadatas)
            self.add_message(filepaths[0], var_key, run_bounds_check)

            if len(metadatas) == 1:
                continue
            self.check_external_contiguity(metadatas, var_key)

        return "Time contiguity check", self.results

    def get_meta(self, ds, filepath):
        """
        Loads netCDF file and extracts metadata into dictionary.

        Parameters
        ----------
        ds: StructuredDataset
            A collection of netCDF files.
        filepath: string
            Path to a particular netCDF file.

        Returns
        -------
        : dict
            Dictionary containing metadata.
        """
        with ds._loader_class(filepath) as nc_file:
            time_dim = nc_file.variables["time"][:]
            frequency_code = nc_file.getncattr("frequency")
            diurnal_climatology = frequency_code == '1hrCM'
            frequency = self._get_frequency(ds, frequency_code, nc_file.getncattr("variable_id"))
            if "time_bnds" in nc_file.variables:
                time_bnds = nc_file.variables["time_bnds"][:]
            elif diurnal_climatology:
                time_bnds = nc_file.variables["climatology_bnds"][:]
            else:
                time_bnds = None
            if len(time_dim) == 1:
                # time dimension has length 1, so skipping the
                # internal time contiguity check
                # and temporal offset is calculated from frequency
                ds._logger.warning(
                    "Time dimension of {} appears to have length 1,"
                    " temporal offset calculations might not be"
                    " reliable. Calculating offset from "
                    "frequency.".format(filepath)
                )
                offset = frequency
            else:
                offset = time_dim[1] - time_dim[0]
            return {
                "filename": filepath,
                "time_dim": time_dim,
                "time_bnds": time_bnds,
                "offset": offset,
                "frequency": frequency,
                "diurnal_climatology": diurnal_climatology,
                "units": nc_file.variables["time"].units,
                "calendar": nc_file.variables["time"].calendar,
            }

    def check_variable(self, ds, var_key, filepaths):
        """
        Tests one variable from the dataset and returns a metadata
        dictionary.

        Parameters
        ----------
        ds: StructuredDataset
            A collection of netCDF files.
        var_key: str
            Facet index corresponding to one variable.
        filepaths: list
            List of paths to netCDF files containing the variable.

        Returns
        -------
        : dict
            Dictionary containing metadata.
        """
        metadatas = []
        for filepath in filepaths:
            metadata = self.get_meta(ds, filepath)
            metadatas.append(metadata)
            if metadata["calendar"] != "360_day":
                self.add_message(
                    filepath, var_key, "{} calendar is not supported yet".format(metadata["calendar"]))
                continue
            if metadata["diurnal_climatology"]:
                internal_check = self.check_diurnal_climatology(metadata["time_dim"], metadata["time_bnds"])
            else:
                internal_check = self.check_internal_contiguity(metadata["time_dim"])
            self.add_message(filepath, var_key, internal_check)
        return metadatas

    def check_external_contiguity(self, metadatas, var_key):
        """
        Tests time contiguity between different files from the dataset.

        Parameters
        ----------
        metadatas: dict
            Metadata dictionary.
        var_key: str
            Facet index corresponding to one variable.

        Returns
        -------
        : bool
            If False, dataset is not valid.
        """
        prev = None
        external_contiguity = True
        for md in metadatas:
            current_offset = self._get_offset(md)
            if md["units"][0:4] == "days" and not md["diurnal_climatology"]:
                try:
                    if not equal_with_tolerance(current_offset, FREQ_DICT[md["frequency"]], TIME_TOLERANCE):
                        self.add_message(md["filename"], var_key,
                                         "Time variable does not appear to be consistent with the frequency attribute")
                        external_contiguity = False
                except KeyError:
                    pass
            if prev is not None:
                previous_offset = self._get_offset(prev)
                if not equal_with_tolerance(previous_offset, current_offset, TIME_TOLERANCE):
                    self.add_message(md["filename"], var_key,
                                     "Inconsistent temporal offsets ({} and {})".format(
                                         previous_offset, current_offset))
                    external_contiguity = False
                elif not equal_with_tolerance(
                        prev["time_dim"][-1] + previous_offset,
                        md["time_dim"][0], TIME_TOLERANCE):
                    gap = md["time_dim"][0] - (
                        prev["time_dim"][-1] + previous_offset)
                    self.add_message(
                        md["filename"], var_key, (
                            "There is an inconsistency between {} "
                            "and {} (a gap of {} days)".format(
                                prev["filename"],
                                md["filename"],
                                strip_zeros(round(gap, 3))
                            )
                        )
                    )
                    external_contiguity = False
            prev = md
        return external_contiguity

    @staticmethod
    def check_internal_contiguity(time_dim):
        """
        Tests if the time coordinate of the file is in correct order
        and does not have any gaps.

        Parameters
        ----------
        time_dim: list
            Time coordinate.

        Returns
        -------
        : None|string
            Error message.
        """
        first = time_dim[0]
        offset = time_dim[1] - time_dim[0]
        msg = None
        if offset < 0:
            msg = "Time coordinate appears to be reversed"
        curr_ind = first
        for time in time_dim[1:]:
            if not equal_with_tolerance(curr_ind + offset, time, TIME_TOLERANCE):
                msg = "Time coordinate is not continuous"
            else:
                curr_ind = time
        return msg

    def check_diurnal_climatology(self, time_dim, time_bnds):
        """
        1-hourly climatologies are calculated in 24-hourly cycles, with one value per month.
        Time coordinate corresponds to the hour (fractional day) of the 15th day of the month.
        Time bounds correspond to the beginning and end of each month, shifted by N hours.

        Therefore, this checker need to test that the time coordinate of the file is in correct order,
        has gaps in the right places (every 24 hours), and that time bounds overlap in a correct way.

        Parameters
        ----------
        time_dim: list
            Time coordinate.
        time_bnds: list
            Time bounds coordinate.
        Returns
        -------
        : None|string
            Error message.
        """
        msg = None
        for index, time in enumerate(time_dim):
            # calculate the middle of the time bound
            midpoint = time_bnds[index][0] + 15.0 + HOURLY_OFFSET * 0.5
            # check if the corresponding time bounds are right:
            if not equal_with_tolerance(midpoint, time, TIME_TOLERANCE):
                msg = 'Time points are not in the middle of time bounds'
                break
            if index == 0:
                continue
            # check the offset
            if index % 24:
                offset = HOURLY_OFFSET
            else:
                offset = MONTHLY_OFFSET
            if not equal_with_tolerance(time - time_dim[index - 1], offset, TIME_TOLERANCE):
                msg = 'Time coordinate is not continuous'
                break
        return msg

    def check_run_bounds(self, request, metadatas):
        """
        Tests datetime bounds from the request.json are consistent with
        the netCDF dataset.

        Parameters
        ----------
        request: :class:`cdds.common.request.Request`
            The |Request| json file.

        metadatas: dict
            Metadata dictionary.

        Returns
        -------
        : None|string
            Error message.
        """
        msg = None
        tolerance = TIME_TOLERANCE
        if metadatas[0]["time_bnds"] is not None:
            date_start = metadatas[0]["time_bnds"][0][0]
            date_end = metadatas[-1]["time_bnds"][-1][1]
        else:
            date_start = metadatas[0]["time_dim"][0]
            date_end = metadatas[-1]["time_dim"][-1]
            tolerance += metadatas[0]["time_dim"][1] - metadatas[0]["time_dim"][0]
        run_start, run_end = request.run_bounds.split(" ")
        run_start_datepoint = datepoint_from_date(run_start)
        run_end_datepoint = datepoint_from_date(run_end)
        if not equal_with_tolerance(date_start, run_start_datepoint, tolerance):
            msg = (
                "Start of the dataset ({} days since {}) do not match"
                " the request date range ({})".format(
                    date_start, request.child_base_date, run_start)
            )
        if not equal_with_tolerance(date_end, run_end_datepoint, tolerance):
            msg = (
                "End of the dataset ({} days since {}) do not match"
                " the request date range ({})".format(
                    date_end, request.child_base_date, run_end)
            )
        return msg

    def add_message(self, filepath, var_key, message):
        """
        Helper function populating internal error message dictionary.
        Parameters
        ----------
        filepath: str
            A filepath.
        var_key: str
            Variable facet index.
        message: str
            Error message.
        """
        if message is not None:
            if filepath not in self.results:
                self.results[filepath] = []
            self.results[filepath].append(
                {
                    "index": var_key,
                    "message": message
                }
            )

    def _get_frequency(self, ds, frequency_code, variable_id):
        if frequency_code == "subhrPt":
            if variable_id.startswith("rs") or variable_id.startswith("rl"):
                # despite the frequency code, radiation variables are on hourly timepoints
                frequency = RADIATION_TIMESTEP
            else:
                # the rest are reported once per timestep
                frequency = float(ds.request.atmos_timestep) / SECONDS_IN_DAY
        else:
            # as defined in frequency dictionary: monthlies are once per month,
            # dailies once per day, etc.
            frequency = FREQ_DICT[frequency_code]
        return frequency

    def _get_offset(self, meta):
        if meta["diurnal_climatology"]:
            # we are making a bold assumption here that files will be split by the diurnal cycles
            return MONTHLY_OFFSET
        else:
            return meta["offset"]
