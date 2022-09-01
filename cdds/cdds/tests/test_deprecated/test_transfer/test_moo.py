# (C) British Crown Copyright 2018-2021, Met Office.
# Please see LICENSE.rst for license details.
import logging
from nose.plugins.attrib import attr
import unittest

from cdds.deprecated.transfer.moo import run_moo_cmd, MassError
from cdds.common.mass import mass_available


class TestRunMooCmd(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        available = mass_available(simulation=False)
        if not available:
            raise RuntimeError('MASS not available. Cannot run integration tests.')

    @attr("slow")
    def test_raise_mass_error(self):
        logging.disable(logging.CRITICAL)
        self.assertRaises(MassError, run_moo_cmd, "ls", ["moose:nosuchdir"])


if __name__ == "__main__":
    unittest.main()
