# (C) British Crown Copyright 2024, Met Office.
# Please see LICENSE.rst for license details.
import pytest

from cdds.prepare.command_line import main_generate_variable_list

from unittest import TestCase


@pytest.mark.skip
class TestExamples(TestCase):

    def test_me(self):
        arguments = [
            '/home/h04/kschmatz/temp/prepare_failure/request.cfg'
        ]

        main_generate_variable_list(arguments)
