# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
import unittest

from mip_convert.tests.test_functional.test_command_line import AbstractFunctionalTests


class TestMe(AbstractFunctionalTests):

    # def get_test_keys(self):
    #     test_keys = list(specific_info().keys())
    #     # If any of the tests contain the 'devel' attribute, run only those tests.
    #     devel = [test_key for test_key, test_info in specific_info().items()
    #              if 'other' in test_info if 'devel' in test_info['other']]
    #     if devel:
    #         test_keys = devel
    #     return test_keys

    def test_main(self):
        test_key = ('CMIP6', 'AERmon', 'rlutaf')
        self.check_main(test_key)


if __name__ == '__main__':
    unittest.main()
