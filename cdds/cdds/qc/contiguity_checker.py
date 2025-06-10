# (C) British Crown Copyright 2018-2025, Met Office.
# Please see LICENSE.md for license details.


"""
Contiguity checker.
"""
from collections import defaultdict
from typing import DefaultDict, List, Dict

from cdds.common.request.request import Request
from cdds.qc.plugins.cmip6.dataset import Cmip6Dataset
from cdds.qc.plugins.cordex.dataset import CordexDataset
from cdds.qc.common import equal_with_tolerance, DatetimeCalculator
from cdds.qc.constants import DIURNAL_CLIMATOLOGY, HOURLY_OFFSET, DIURNAL_OFFSETS, TIME_TOLERANCE


class CollectionsCheck(object):
    """Time contiguity checker for a set of ncdf files."""

    name = "collections"
    supported_ds = [Cmip6Dataset, CordexDataset]

    def __init__(self, request: Request):
        """
        A constructor.
        """
        self.request = request
        self.calendar_calculator = DatetimeCalculator(
            self.request.metadata.calendar, self.request.metadata.base_date)
        self.results: DefaultDict[str, List[Dict[str, str]]] = defaultdict(list)

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
            time_axis, time_bounds, frequency = ds.variable_time_axis(var_key, self.request.misc.atmos_timestep)
            run_start = self.request.data.start_date
            run_end = self.request.data.end_date
            self.check_contiguity(var_key, time_axis, time_bounds, frequency, run_start, run_end)
        return "Time contiguity check", self.results

    def check_diurnal_climatology(self, time_dim, time_bnds):
        """
        1-hourly climatologies are calculated in 24-hourly cycles, with one value per month.
        Time coordinate corresponds to the hour (fractional day) of the 14th or 15th day of the month.
        Time bounds correspond to the beginning and end of each month, shifted by N hours, i.e.
        1st day of the month 00:00 - last day of the month 01:00.

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
            # in Gregorian calendar it's always centered on the first half hour of the 15th day of the month
            # regardless if the month has 30 or 31 days, the only exception being February

            starting_date = self.calendar_calculator.days_since_base_date_to_date(int(time_bnds[index][0]))
            month = starting_date.month_of_year
            if self.calendar_calculator.calendar == '360_day':
                half_month = 15.0
            else:
                if month == 2:
                    # but if it's Gregorian February, the midpoint is always on 14th, even if it's a leap year
                    # 14th
                    half_month = 13.0
                else:
                    # 15th
                    half_month = 14.0
            midpoint = time_bnds[index][0] + half_month + HOURLY_OFFSET * 0.5

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
                if self.calendar_calculator.calendar == 'Gregorian':
                    # this needs to be retested once we have actual data
                    offset = DIURNAL_OFFSETS[month - 1] + HOURLY_OFFSET
                    if month == 3 and self.calendar_calculator.date_in_leap_year(starting_date):
                        offset += 1
                else:
                    offset = 29.0 + HOURLY_OFFSET
            if not equal_with_tolerance(time - time_dim[index - 1], offset, TIME_TOLERANCE):
                msg = 'Time coordinate is not continuous'
                break
        return msg

    def check_contiguity(self, var_key, time_axis, time_bounds, frequency, run_start, run_end):
        """
        Consolidated time contiguity check.

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

        if frequency == DIURNAL_CLIMATOLOGY:
            prev_val = None
            for key, vals in time_axis.items():
                self.add_message(key, var_key, self.check_diurnal_climatology(vals, time_bounds[key]))
                if prev_val is not None and not equal_with_tolerance(
                        time_bounds[key][0][0], prev_val, TIME_TOLERANCE):
                    self.add_message(key, var_key,
                                     'Climatology time bounds in {} appear to be mismatched'.format(key))
                prev_val = time_bounds[key][-1][1]
            return
        point_sequence, bound_sequence = self.calendar_calculator.get_sequence(
            run_start, run_end, frequency, time_bounds is not None)
        reference_index = 0
        # before checking individual values we'll check run bounds first
        run_bounds_errors, offset_adjustment = self._test_time_bounds(
            var_key, time_axis, time_bounds, point_sequence, bound_sequence)
        # if they don't match then it doesn't make sense to validate individual points as all coordinate points will be
        # offset relative to reference
        if run_bounds_errors:
            return
        if offset_adjustment:
            # remove the first midnight from reference time axis of instantenous variable
            point_sequence.pop(0)
        # testing total length of the sequence
        total_length = sum([len(vals) for vals in time_axis.values()])
        if total_length != len(point_sequence):
            for key in time_axis.keys():
                self.add_message(key, var_key,
                                 ('Total length of time coordinate, {}, is different from {} implied by time bounds'
                                  ' (from {} to {}) and time frequency ({})').format(
                                     total_length, len(point_sequence), run_start, run_end, frequency))
            return
        for key, vals in time_axis.items():
            if len(vals) > 1 and vals[0] > vals[1]:
                # for the sake of consistency we retained the reverse coord check
                self.add_message(key, var_key, 'Time coordinate appears to be reversed')
                # need to advance index to the end of the sequence
                reference_index = reference_index + len(vals)
                continue
            if time_bounds is not None and len(vals) != len(time_bounds[key]):
                self.add_message(key, var_key, 'Number of time points is different from number of time bounds')
            for index, val in enumerate(vals):
                self.add_message(key, var_key, self._test_datetime_sequence(
                    point_sequence[reference_index], val, 'Time axis value '))
                if time_bounds is not None and len(vals) == len(time_bounds[key]):
                    # testing both bounds
                    self.add_message(key, var_key, self._test_datetime_sequence(
                        bound_sequence[reference_index][0], time_bounds[key][index][0], 'Time bounds value '))
                    self.add_message(key, var_key, self._test_datetime_sequence(
                        bound_sequence[reference_index][1], time_bounds[key][index][1], 'Time bounds value '))
                reference_index = reference_index + 1
        return

    def _test_datetime_sequence(self, reference_datetime, tested_value, msg_prefix, tolerance=TIME_TOLERANCE):
        msg = None
        reference_time_point = self.calendar_calculator.days_since_base_date(
            reference_datetime.strftime('%Y-%m-%dT%H:%MZ'))
        if not equal_with_tolerance(
                tested_value,
                reference_time_point,
                tolerance):
            msg = '{}{} does not correspond to reference value {} (difference {} days)'.format(
                msg_prefix, tested_value, reference_datetime, reference_time_point - tested_value)
        return msg

    def _test_time_bounds(self, var_key, time_axis, time_bounds, point_sequence, bound_sequence):
        tolerance = TIME_TOLERANCE
        offset_adjustment = False
        first_file = list(time_axis.keys())[0]
        last_file = list(time_axis.keys())[-1]
        if time_bounds is not None:
            start_bound_error = self.add_message(
                first_file, var_key, self._test_datetime_sequence(
                    bound_sequence[0][0], time_bounds[first_file][0][0],
                    'Run bounds mismatch: start of the simulation bounds '))
            end_bound_error = self.add_message(
                last_file, var_key, self._test_datetime_sequence(
                    bound_sequence[-1][1], time_bounds[last_file][-1][1],
                    'Run bounds mismatch: end of the simulation bounds '))
        else:
            start_bound_error = False
            end_bound_error = False
            # we need to check if the first point is present or missing for instantenous variables and
            # then adjust the sequence accordingly
            if (self._test_datetime_sequence(
                    point_sequence[0], time_axis[first_file][0], 'First point mismatch', tolerance) is not None and
                self._test_datetime_sequence(
                    point_sequence[1], time_axis[first_file][0], 'Second bounds mismatch', tolerance) is None):
                offset_adjustment = True
            tolerance += time_axis[first_file][1] - time_axis[first_file][0]
        start_error = self.add_message(
            first_file, var_key, self._test_datetime_sequence(
                point_sequence[0], time_axis[first_file][0], 'Run bounds mismatch: start of the simulation ',
                tolerance))
        end_error = self.add_message(
            last_file, var_key, self._test_datetime_sequence(
                point_sequence[-1], time_axis[last_file][-1], 'Run bounds mismatch: end of the simulation ',
                tolerance))
        return start_error or end_error or start_bound_error or end_bound_error, offset_adjustment

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
            self.results[filepath].append(
                {
                    "index": var_key,
                    "message": message
                }
            )
            return True
        return False
