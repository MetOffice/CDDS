# (C) British Crown Copyright 2015-2021, Met Office.
# Please see LICENSE.rst for license details.

from configparser import ConfigParser
from nose.plugins.attrib import attr
import unittest
from mip_convert import model_date
from mip_convert.control_manager import GeneralProject


class TestConfigOptions(unittest.TestCase):

    def add(self, section, option, value):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, option, value)

    def setUp(self):
        self.config = ConfigParser()
        self.general = GeneralProject(self.config, model_date)

    @attr('integration')
    def testSimpleOptionsPath(self):
        examples = list(map(self.str_opt, [('_outpath', 'outdir', 'outdir'),
                                           ('_tablepath', 'inpath', 'tablepath'),
                                           ('_orogpath',
                                            'orography_path', 'orogpath'),
                                           ('_mappingpath', 'mappings', 'mappingpath')]))
        examples.append(('_timestep', 'atm_timestep_in_seconds', '1800', 'data_source', float))

        for (attribute, option, expect, section, to_type) in examples:
            self.add(section, option, expect)
            self.assertEqual(getattr(self.general, attribute), to_type(expect))

    @attr('integration')
    def testBaseTime(self):
        reference_date = '1869-12-01'
        self.add('general', 'base_date', reference_date + '-00-00-00')
        self.add('data_source', 'calendar', '360_day')
        self.assertEqual(self.general._baseTime, model_date.CdDate(1869, 12, 1, 0, 0, 0, '360_day'))

    @attr('integration')
    def testProlepticBaseTime(self):
        reference_date = '1869-12-31'
        self.add('general', 'base_date', reference_date + '-00-00-00')
        self.add('data_source', 'calendar', 'proleptic_gregorian')
        self.assertEqual(self.general._baseTime, model_date.CdDate(1869, 12, 31, 0, 0, 0, 'proleptic_gregorian'))

    def str_opt(self, opts):
        return opts[0], opts[1], opts[2], 'general', str


if __name__ == '__main__':
    unittest.main()
