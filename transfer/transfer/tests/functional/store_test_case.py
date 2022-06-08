# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
from unittest import TestCase, mock
from nose.plugins.attrib import attr

from cdds_common.cdds_plugins.plugin_loader import load_plugin
from hadsdk.mass import mass_info


@attr('slow')
class StoreTestCase(TestCase):
    """
    All tests are described in details at:
    https://metoffice.atlassian.net/wiki/spaces/GWVGF/pages/3776905225/Transfer+Archiving+Use+Cases
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
