from unittest import TestCase
from cdds.extract.command_line import main_cdds_extract


class MyTestCase(TestCase):

    def test_me(self):
        arguments = ['/home/h04/kschmatz/request.json',
                     '-s', 'apa',
                     '--root_proc_dir', '/home/h04/kschmatz/test-data/proc_dir',
                     '--root_data_dir', '/home/h04/kschmatz/test-data/data_dir']

        main_cdds_extract(arguments)
