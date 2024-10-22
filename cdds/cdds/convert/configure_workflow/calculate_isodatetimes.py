# (C) British Crown Copyright 2024, Met Office.
# Please see LICENSE.rst for license details.
from dataclasses import dataclass

from metomi.isodatetime.data import TimeRecurrence, TimePoint, Duration
from metomi.isodatetime.parsers import DurationParser, TimeRecurrenceParser


@dataclass
class CalculateISODatetimes:
    start_date: TimePoint
    end_date: TimePoint
    cycling_frequency: Duration
    concatenation_window: Duration
    base_date: TimePoint

    @property
    def cycling_recurrence(self) -> TimeRecurrence:
        return TimeRecurrence(start_point=self.base_date, duration=self.cycling_frequency)

    @property
    def concat_recurrence(self) -> TimeRecurrence:
        return TimeRecurrence(start_point=self.base_date, duration=self.concatenation_window)

    @property
    def smaller_than_cycling_frequency(self) -> bool:
        return self.start_date + self.cycling_frequency <= self.end_date

    @property
    def single_concatenation_window(self) -> bool:
        return self.start_date + self.concatenation_window >= self.end_date

    @property
    def final_cycle_point(self) -> TimePoint:
        if self.cycling_recurrence.get_is_valid(self.end_date):
            final_cycle_point = self.cycling_recurrence.get_prev(self.end_date)
        else:
            point = self.cycling_recurrence.get_first_after(self.end_date)
            final_cycle_point = self.cycling_recurrence.get_prev(point)
        return final_cycle_point

    @property
    def alignment_cycle_offset(self) -> Duration:
        if not self.cycling_recurrence.get_is_valid(self.start_date):
            offset = (self.cycling_recurrence.get_first_after(self.start_date) - self.start_date)
        else:
            offset = DurationParser().parse("P0D")
        return offset

    @property
    def alignment_cycle_needed(self) -> bool:
        return DurationParser().parse("P0D") != self.alignment_cycle_offset

    @property
    def first_concat_cycle_offset(self) -> Duration:
        if self.single_concatenation_window:
            offset = self.final_cycle_point - self.start_date
        else:
            concat_window_date = self.concat_recurrence.get_first_after(self.start_date)
            first_cycle = concat_window_date - self.cycling_frequency
            offset = first_cycle - self.start_date
        return offset

    @property
    def final_concatenation_needed(self) -> bool:
        if self.single_concatenation_window:
            return False

        final_concatenation_cycle = (self.start_date + self.final_concatenation_window_offset)
        first_concat_cycle = self.start_date + DurationParser().parse(f"{self.first_concat_cycle_offset}")
        recurrence = TimeRecurrenceParser().parse(f"R/{first_concat_cycle}/{self.concatenation_window}")
        return not recurrence.get_is_valid(final_concatenation_cycle)

    @property
    def final_concatenation_window_offset(self) -> Duration:
        return self.final_cycle_point - self.start_date

    @property
    def final_concatenation_window_point(self) -> TimePoint:
        if self.single_concatenation_window:
            return 0

        if self.concat_recurrence.get_is_valid(self.end_date):
            point = self.concat_recurrence.get_prev(self.end_date)
        else:
            point = self.concat_recurrence.get_prev(self.concat_recurrence.get_first_after(self.end_date))
        return point

    def as_dict(self):
        return {
            "CONCATENATION_FIRST_CYCLE_OFFSET": str(self.first_concat_cycle_offset),
            "CONCATENATION_WINDOW": str(self.concatenation_window),
            "CONVERT_ALIGNMENT_OFFSET": str(self.alignment_cycle_offset),
            "CYCLING_FREQUENCY": str(self.cycling_frequency),
            "DO_CONVERT_ALIGNMENT_CYCLE": self.alignment_cycle_needed,
            "DO_FINAL_CONCATENATE": self.final_concatenation_needed,
            "FINAL_CONCATENATION_CYCLE": str(self.final_concatenation_window_offset),
            "FINAL_CONCATENATION_WINDOW_START": str(self.final_concatenation_window_point),
            "FINAL_CYCLE_POINT": str(self.final_cycle_point),
            "SINGLE_CONCATENATION_CYCLE": self.single_concatenation_window,
        }
