from unittest import TestCase
from mip_convert.command_line import main


class TestMe(TestCase):

    def test_me(self):
        config = '/home/h04/kschmatz/test-data/output_dir/mip_convert.cfg.atmos-native'

        arguments = [
            config,
            '-s' 'apa'
        ]

        main(arguments)
