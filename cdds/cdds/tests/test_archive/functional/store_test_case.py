# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
from unittest import TestCase, mock
import pytest

from cdds.common.plugins.plugin_loader import load_plugin
from cdds.common.mass import mass_info


@pytest.mark.slow
class StoreTestCase(TestCase):
    """
    TEST DIRECTORY
        Root test directory
            >> /project/cdds/testdata/functional_tests/transfer/

    MODEL INFORMATION
        * All test uses the nc files created by the model ``UKESM1-0-LL`` for experiment ``piControl``
          and variant ``r1i1p1f2`` (50 year chunk)
        * The most tests only consider the stream ``ap5`` and the variable ``Amon/tas``

    MASS
        Root MASS location
            >> moose:/adhoc/projects/cdds/testdata/transfer_functional
    """

    @classmethod
    def setUpClass(cls):
        available, cmds = mass_info(simulation=False)
        if not available:
            raise RuntimeError('MASS not available. Cannot run integration tests.')
        if not cmds['GET'] or not cmds['PUT']:
            raise RuntimeError('Needed MOSSE commands not processable. Cannot run integration tests.')
        load_plugin()

    def assertSize(self, actual_list, expected_size):
        self.assertEqual(len(actual_list), expected_size)

    def assertHasFiles(self, filelist_per_cmd, *sub_filenames):
        for filelist in filelist_per_cmd:
            self.assertSize(filelist, len(sub_filenames))
            for index, filename in enumerate(sub_filenames):
                self.assertIn(filename, filelist[index])

    def assertMessagesContain(self, messages, *expected_sub_messages):
        for message in messages:
            for expected_sub_message in expected_sub_messages:
                self.assertIn(expected_sub_message, message)
