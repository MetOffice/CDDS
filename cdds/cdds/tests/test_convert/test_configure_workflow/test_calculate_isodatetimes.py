# (C) British Crown Copyright 2024, Met Office.
# Please see LICENSE.rst for license details.
from metomi.isodatetime.data import Calendar
from metomi.isodatetime.parsers import DurationParser, TimePointParser

from cdds.convert.configure_workflow.calculate_isodatetimes import CalculateISODatetimes


class TestCalculateISODatetimes360Day:
    def setup_method(self):
        Calendar.default().set_mode("360_day")

    def test_piControl_ap4(self):
        isodatetimes = CalculateISODatetimes(
            TimePointParser().parse("1970-01-01T00:00:00Z"),
            TimePointParser().parse("2170-01-01T00:00:00Z"),
            DurationParser().parse("P5Y"),
            DurationParser().parse("P100Y"),
            TimePointParser().parse("1850-01-01T00:00:00Z"),
        )

        expected = {
            "CONCATENATION_FIRST_CYCLE_OFFSET": "P27000D",
            "CONCATENATION_WINDOW": "P100Y",
            "CONVERT_ALIGNMENT_OFFSET": "P0Y",
            "CYCLING_FREQUENCY": "P5Y",
            "DO_CONVERT_ALIGNMENT_CYCLE": False,
            "DO_FINAL_CONCATENATE": True,
            "FINAL_CONCATENATION_CYCLE": "P70200D",
            "FINAL_CONCATENATION_WINDOW_START": "2150-01-01T00:00:00Z",
            "FINAL_CYCLE_POINT": "2165-01-01T00:00:00Z",
            "SINGLE_CONCATENATION_CYCLE": False,
        }

        assert expected == isodatetimes.as_jinja2()

    def test_piControl_onm(self):
        isodatetimes = CalculateISODatetimes(
            TimePointParser().parse("1970-01-01T00:00:00Z"),
            TimePointParser().parse("2170-01-01T00:00:00Z"),
            DurationParser().parse("P2Y"),
            DurationParser().parse("P100Y"),
            TimePointParser().parse("1850-01-01T00:00:00Z"),
        )

        expected = {
            "CONCATENATION_FIRST_CYCLE_OFFSET": "P28080D",
            "CONCATENATION_WINDOW": "P100Y",
            "CONVERT_ALIGNMENT_OFFSET": "P0Y",
            "CYCLING_FREQUENCY": "P2Y",
            "DO_CONVERT_ALIGNMENT_CYCLE": False,
            "DO_FINAL_CONCATENATE": True,
            "FINAL_CONCATENATION_CYCLE": "P71280D",
            "FINAL_CONCATENATION_WINDOW_START": "2150-01-01T00:00:00Z",
            "FINAL_CYCLE_POINT": "2168-01-01T00:00:00Z",
            "SINGLE_CONCATENATION_CYCLE": False,
        }

        assert expected == isodatetimes.as_jinja2()

    def test_amip_ll_ap4(self):
        isodatetimes = CalculateISODatetimes(
            TimePointParser().parse("1979-01-01T00:00:00Z"),
            TimePointParser().parse("2015-01-01T00:00:00Z"),
            DurationParser().parse("P5Y"),
            DurationParser().parse("P100Y"),
            TimePointParser().parse("1850-01-01T00:00:00Z"),
        )

        expected = {
            "CONCATENATION_FIRST_CYCLE_OFFSET": "P11160D",
            "CONCATENATION_WINDOW": "P100Y",
            "CONVERT_ALIGNMENT_OFFSET": "P360D",
            "CYCLING_FREQUENCY": "P5Y",
            "DO_CONVERT_ALIGNMENT_CYCLE": True,
            "DO_FINAL_CONCATENATE": False,
            "FINAL_CONCATENATION_CYCLE": "P11160D",
            "FINAL_CONCATENATION_WINDOW_START": "0",
            "FINAL_CYCLE_POINT": "2010-01-01T00:00:00Z",
            "SINGLE_CONCATENATION_CYCLE": True,
        }

        assert expected == isodatetimes.as_jinja2()

    def test_amip_ll_ap6(self):
        isodatetimes = CalculateISODatetimes(
            TimePointParser().parse("1979-01-01T00:00:00Z"),
            TimePointParser().parse("2015-01-01T00:00:00Z"),
            DurationParser().parse("P1Y"),
            DurationParser().parse("P100Y"),
            TimePointParser().parse("1850-01-01T00:00:00Z"),
        )

        expected = {
            "CONCATENATION_FIRST_CYCLE_OFFSET": "P12600D",
            "CONCATENATION_WINDOW": "P100Y",
            "CONVERT_ALIGNMENT_OFFSET": "P0Y",
            "CYCLING_FREQUENCY": "P1Y",
            "DO_CONVERT_ALIGNMENT_CYCLE": False,
            "DO_FINAL_CONCATENATE": False,
            "FINAL_CONCATENATION_CYCLE": "P12600D",
            "FINAL_CONCATENATION_WINDOW_START": "0",
            "FINAL_CYCLE_POINT": "2014-01-01T00:00:00Z",
            "SINGLE_CONCATENATION_CYCLE": True,
        }

        assert expected == isodatetimes.as_jinja2()

    def test_ssp126_ap4(self):
        isodatetimes = CalculateISODatetimes(
            TimePointParser().parse("2015-01-01T00:00:00Z"),
            TimePointParser().parse("2101-01-01T00:00:00Z"),
            DurationParser().parse("P5Y"),
            DurationParser().parse("P100Y"),
            TimePointParser().parse("1850-01-01T00:00:00Z"),
        )

        expected = {
            "CONCATENATION_FIRST_CYCLE_OFFSET": "P30600D",
            "CONCATENATION_WINDOW": "P100Y",
            "CONVERT_ALIGNMENT_OFFSET": "P0Y",
            "CYCLING_FREQUENCY": "P5Y",
            "DO_CONVERT_ALIGNMENT_CYCLE": False,
            "DO_FINAL_CONCATENATE": False,
            "FINAL_CONCATENATION_CYCLE": "P30600D",
            "FINAL_CONCATENATION_WINDOW_START": "0",
            "FINAL_CYCLE_POINT": "2100-01-01T00:00:00Z",
            "SINGLE_CONCATENATION_CYCLE": True,
        }

        assert expected == isodatetimes.as_jinja2()

    def test_ssp126_ap6(self):
        isodatetimes = CalculateISODatetimes(
            TimePointParser().parse("2015-01-01T00:00:00Z"),
            TimePointParser().parse("2101-01-01T00:00:00Z"),
            DurationParser().parse("P1Y"),
            DurationParser().parse("P100Y"),
            TimePointParser().parse("1850-01-01T00:00:00Z"),
        )

        expected = {
            "CONCATENATION_FIRST_CYCLE_OFFSET": "P30600D",
            "CONCATENATION_WINDOW": "P100Y",
            "CONVERT_ALIGNMENT_OFFSET": "P0Y",
            "CYCLING_FREQUENCY": "P1Y",
            "DO_CONVERT_ALIGNMENT_CYCLE": False,
            "DO_FINAL_CONCATENATE": False,
            "FINAL_CONCATENATION_CYCLE": "P30600D",
            "FINAL_CONCATENATION_WINDOW_START": "0",
            "FINAL_CYCLE_POINT": "2100-01-01T00:00:00Z",
            "SINGLE_CONCATENATION_CYCLE": True,
        }

        assert expected == isodatetimes.as_jinja2()

    def test_ssp126_onm(self):
        isodatetimes = CalculateISODatetimes(
            TimePointParser().parse("2015-01-01T00:00:00Z"),
            TimePointParser().parse("2101-01-01T00:00:00Z"),
            DurationParser().parse("P2Y"),
            DurationParser().parse("P100Y"),
            TimePointParser().parse("1850-01-01T00:00:00Z"),
        )

        expected = {
            "CONCATENATION_FIRST_CYCLE_OFFSET": "P30600D",
            "CONCATENATION_WINDOW": "P100Y",
            "CONVERT_ALIGNMENT_OFFSET": "P360D",
            "CYCLING_FREQUENCY": "P2Y",
            "DO_CONVERT_ALIGNMENT_CYCLE": True,
            "DO_FINAL_CONCATENATE": False,
            "FINAL_CONCATENATION_CYCLE": "P30600D",
            "FINAL_CONCATENATION_WINDOW_START": "0",
            "FINAL_CYCLE_POINT": "2100-01-01T00:00:00Z",
            "SINGLE_CONCATENATION_CYCLE": True,
        }

        assert expected == isodatetimes.as_jinja2()

    def test_amip_mm_ap5(self):
        isodatetimes = CalculateISODatetimes(
            TimePointParser().parse("1979-01-01T00:00:00Z"),
            TimePointParser().parse("2015-01-01T00:00:00Z"),
            DurationParser().parse("P1Y"),
            DurationParser().parse("P20Y"),
            TimePointParser().parse("1850-01-01T00:00:00Z"),
        )

        expected = {
            "CONCATENATION_FIRST_CYCLE_OFFSET": "P3600D",
            "CONCATENATION_WINDOW": "P20Y",
            "CONVERT_ALIGNMENT_OFFSET": "P0Y",
            "CYCLING_FREQUENCY": "P1Y",
            "DO_CONVERT_ALIGNMENT_CYCLE": False,
            "DO_FINAL_CONCATENATE": True,
            "FINAL_CONCATENATION_CYCLE": "P12600D",
            "FINAL_CONCATENATION_WINDOW_START": "2010-01-01T00:00:00Z",
            "FINAL_CYCLE_POINT": "2014-01-01T00:00:00Z",
            "SINGLE_CONCATENATION_CYCLE": False,
        }

        assert expected == isodatetimes.as_jinja2()

    def test_amip_mm_ap6(self):
        isodatetimes = CalculateISODatetimes(
            TimePointParser().parse("1979-01-01T00:00:00Z"),
            TimePointParser().parse("2015-01-01T00:00:00Z"),
            DurationParser().parse("P3M"),
            DurationParser().parse("P20Y"),
            TimePointParser().parse("1850-01-01T00:00:00Z"),
        )

        expected = {
            "CONCATENATION_FIRST_CYCLE_OFFSET": "P3870D",
            "CONCATENATION_WINDOW": "P20Y",
            "CONVERT_ALIGNMENT_OFFSET": "P0Y",
            "CYCLING_FREQUENCY": "P3M",
            "DO_CONVERT_ALIGNMENT_CYCLE": False,
            "DO_FINAL_CONCATENATE": True,
            "FINAL_CONCATENATION_CYCLE": "P12870D",
            "FINAL_CONCATENATION_WINDOW_START": "2010-01-01T00:00:00Z",
            "FINAL_CYCLE_POINT": "2014-10-01T00:00:00Z",
            "SINGLE_CONCATENATION_CYCLE": False,
        }

        assert expected == isodatetimes.as_jinja2()


class TestCalculateISODatetimesGregorian:
    def setup_method(self):
        Calendar.default().set_mode("gregorian")

    def teardown_method(self):
        Calendar.default().set_mode("360_day")

    def test_piControl_ap4(self):
        isodatetimes = CalculateISODatetimes(
            TimePointParser().parse("1970-01-01T00:00:00Z"),
            TimePointParser().parse("2170-01-01T00:00:00Z"),
            DurationParser().parse("P5Y"),
            DurationParser().parse("P100Y"),
            TimePointParser().parse("1850-01-01T00:00:00Z"),
        )

        expected = {
            "CONCATENATION_FIRST_CYCLE_OFFSET": "P27394D",
            "CONCATENATION_WINDOW": "P100Y",
            "CONVERT_ALIGNMENT_OFFSET": "P0Y",
            "CYCLING_FREQUENCY": "P5Y",
            "DO_CONVERT_ALIGNMENT_CYCLE": False,
            "DO_FINAL_CONCATENATE": True,
            "FINAL_CONCATENATION_CYCLE": "P71223D",
            "FINAL_CONCATENATION_WINDOW_START": "2150-01-01T00:00:00Z",
            "FINAL_CYCLE_POINT": "2165-01-01T00:00:00Z",
            "SINGLE_CONCATENATION_CYCLE": False,
        }

        assert expected == isodatetimes.as_jinja2()
