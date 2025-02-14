# (C) British Crown Copyright 2024-2025, Met Office.
# Please see LICENSE.md for license details.
from unittest import TestCase

from configparser import ConfigParser
from cdds.common.request.validations.pre_validations import do_pre_validations
from cdds.common.request.metadata_section import MetadataSection
from cdds.common.request.conversion_section import ConversionSection
from cdds.common.request.misc_section import MiscSection


class TestPreValidations(TestCase):

    def test_unknown_property(self):
        config = ConfigParser()
        config.add_section(MetadataSection.name())
        config.set(MetadataSection.name(), 'foo', 'bar')

        self.assertRaisesRegex(
            ValueError,
            'Section "metadata" contains unrecognised entry "foo" defined',
            do_pre_validations,
            config,
            MetadataSection
        )

    def test_wrong_timepoint(self):
        config = ConfigParser()
        config.add_section('metadata')
        config.set('metadata', 'branch_date_in_child', '1999_01_01')

        self.assertRaisesRegex(
            ValueError,
            ('The value of "branch_date_in_child" in section "metadata" must be a date with the format of '
             '"yyyy-mm-ddTHH:MM:SSZ" and not "1999_01_01", e.g. "1850-01-01T00:00:00Z"'),
            do_pre_validations,
            config,
            MetadataSection
        )

    def test_no_bool(self):
        config = ConfigParser()
        config.add_section(ConversionSection.name())
        config.set(ConversionSection.name(), 'skip_extract', 'boo')

        self.assertRaisesRegex(
            ValueError,
            'The value of "skip_extract" in section "conversion" must be False or True',
            do_pre_validations,
            config,
            ConversionSection
        )

    def test_no_number(self):
        config = ConfigParser()
        config.add_section(MiscSection.name())
        config.set(MiscSection.name(), 'atmos_timestep', 'boo')

        self.assertRaisesRegex(
            ValueError,
            'The value of "atmos_timestep" in section "misc" must be a number',
            do_pre_validations,
            config,
            MiscSection
        )

    def test_no_float(self):
        config = ConfigParser()
        config.add_section(ConversionSection.name())
        config.set(ConversionSection.name(), 'scale_memory_limits', 'boo')

        self.assertRaisesRegex(
            ValueError,
            'The value of "scale_memory_limits" in section "conversion" must be a number',
            do_pre_validations,
            config,
            ConversionSection
        )
