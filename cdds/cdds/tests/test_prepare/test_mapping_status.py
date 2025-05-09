# (C) British Crown Copyright 2020-2025, Met Office.
# Please see LICENSE.md for license details.
# pylint: disable = no-member
import unittest

from cdds.prepare.mapping_status import MappingStatus, ProducibleState


class TestMappingStatus(unittest.TestCase):

    def test_variable_is_producible(self):
        instance = MappingStatus.get_instance()
        state = instance.producible('cfc12global', 'Amon')
        self.assertEqual(state, ProducibleState.PRODUCE)

    def test_variable_is_not_producible(self):
        instance = MappingStatus.get_instance()
        state = instance.producible('cct', 'Amon')
        self.assertEqual(state, ProducibleState.NOT_PRODUCE)

    def test_variable_is_unknown(self):
        instance = MappingStatus.get_instance()
        state = instance.producible('unknown_variable', 'unknown_miptable')
        self.assertEqual(state, ProducibleState.UNKNOWN)


class TestProducible(unittest.TestCase):

    def test_produce_to_variables_data_value(self):
        state = ProducibleState.PRODUCE
        value = ProducibleState.to_variables_data_value(state)
        self.assertEqual(value, 'yes')

    def test_produce_to_variables_data_value(self):
        state = ProducibleState.NOT_PRODUCE
        value = ProducibleState.to_variables_data_value(state)
        self.assertEqual(value, 'no')

    def test_produce_to_variables_data_value(self):
        state = ProducibleState.UNKNOWN
        value = ProducibleState.to_variables_data_value(state)
        self.assertEqual(value, 'unknown')


if __name__ == '__main__':
    unittest.main()
