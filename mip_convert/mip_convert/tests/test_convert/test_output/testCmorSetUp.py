# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.

import unittest

from mip_convert.save.cmor.cmor_lite import CmorSetupCall
from mip_convert.save.cmor.config_file import CmorSetupConf


class TestCmorSetupConf(unittest.TestCase):
    def get(self, section, option):
        """
        stub ConfigParser
        """
        return self.sections[section][option]

    def getint(self, section, option):
        return int(self.get(section, option))

    def has_option(self, section, option):
        """
        stub ConfigParser
        """
        return option in self.sections[section]

    def test_attributes(self):
        self.sections = {
            'general': {
                'inpath': 'an-in-path',
                'logfile': 'a-log-file',
                'netcdf_file_action': 'CMOR_PRESERVE',
                'set_verbosity': 'CMOR_QUIET',
                'exit_control': 'CMOR_EXIT_ON_MAJOR',
                'create_subdirectories': '0',
            },
        }
        setup_cmor = CmorSetupConf(self)
        self.assertEqual('an-in-path', setup_cmor.inpath)
        self.assertEqual('a-log-file', setup_cmor.logfile)
        self.assertEqual('CMOR_PRESERVE', setup_cmor.netcdf_file_action)
        self.assertEqual('CMOR_QUIET', setup_cmor.set_verbosity)
        self.assertEqual('CMOR_EXIT_ON_MAJOR', setup_cmor.exit_control)
        self.assertEqual('0', setup_cmor.create_subdirectories)

    def test_no_attributes(self):
        self.sections = {'general': {}}
        setup_cmor = CmorSetupConf(self)
        try:
            setup_cmor.inpath
            self.fail('no Exception raised')
        except AttributeError as e:
            self.assertEqual("type object 'CmorSetupConf' has no attribute 'inpath'", str(e))


class TestCmorSetup(unittest.TestCase):
    CMOR_PRESERVE = 10
    CMOR_QUIET = 21
    CMOR_EXIT_ON_MAJOR = 32

    def get(self, section, option):
        """
        stub ConfigParser
        """
        return self.sections[section][option]

    def getint(self, section, option):
        return int(self.get(section, option))

    def has_option(self, section, option):
        """
        stub ConfigParser
        """
        return option in self.sections[section]

    def setup(self, **kwargs):
        """
        cmor stub behaviour
        """
        self.kwargs = kwargs

    def test_reads_inpath(self):
        # left as an integration test for now
        self.sections = {'general': {'inpath': 'an-in-path', }}
        setup_cmor = CmorSetupConf(self)
        CmorSetupCall(self)(setup_cmor)
        self.assertEqual({'inpath': 'an-in-path'}, self.kwargs)


if __name__ == '__main__':
    unittest.main()
