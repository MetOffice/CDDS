# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
import logging
import pytest
import unittest

from cdds.deprecated.transfer.moo import run_moo_cmd, MassError
from cdds.common.mass import mass_available


class TestRunMooCmd(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        available = mass_available(simulation=False)
        if not available:
            raise RuntimeError('MASS not available. Cannot run integration tests.')

    @pytest.mark.slow
    def test_raise_mass_error(self):
        logging.disable(logging.CRITICAL)
        self.assertRaises(MassError, run_moo_cmd, "ls", ["moose:nosuchdir"])


if __name__ == "__main__":
    unittest.main()
