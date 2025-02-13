# (C) British Crown Copyright 2016-2021, Met Office.
# Please see LICENSE.md for license details.
import unittest

from cdds.deprecated.transfer import state


class TestState(unittest.TestCase):

    def setUp(self):
        self.all_states = {
            state.Embargoed, state.Available, state.Withdrawn,
            state.Superseded}
        self.valid_states = {
            "embargoed": {
                "can_move_to": {state.Available},
                "can_come_from": set([])},
            "available": {
                "can_move_to": {state.Withdrawn, state.Superseded},
                "can_come_from": {state.Embargoed, state.Withdrawn}},
            "withdrawn": {
                "can_move_to": {state.Available},
                "can_come_from": {state.Superseded, state.Available}},
            "superseded": {
                "can_move_to": {state.Withdrawn},
                "can_come_from": {state.Available}}
        }

    def invalid_states(self, state_name, direction):
        return self.all_states - self.valid_states[state_name][direction]

    def check_states(self, test_state):
        state_name = test_state.name()
        for old_type in self.valid_states[state_name]["can_come_from"]:
            self.assertTrue(
                test_state.can_come_from(old_type()),
                "%s -> %s should be ok" % (old_type, state_name))
        for old_type in self.invalid_states(state_name, "can_come_from"):
            self.assertFalse(
                test_state.can_come_from(old_type()),
                "%s -> %s shouldn't be ok" % (old_type, state_name))
        for new_type in self.valid_states[state_name]["can_move_to"]:
            self.assertTrue(
                test_state.can_move_to(new_type()),
                "%s -> %s should be ok" % (state_name, new_type))
        for new_type in self.invalid_states(state_name, "can_move_to"):
            self.assertFalse(
                test_state.can_move_to(new_type()),
                "%s -> %s shouldn't be ok" % (state_name, new_type))

    def test_embargoed(self):
        embargoed = state.Embargoed()
        self.assertEqual(embargoed.name(), "embargoed")
        self.assertTrue(embargoed.can_be_put())
        self.assertFalse(embargoed.inform())
        self.check_states(embargoed)

    def test_available(self):
        available = state.Available()
        self.assertEqual(available.name(), "available")
        self.assertFalse(available.can_be_put())
        self.assertTrue(available.inform())
        self.check_states(available)

    def test_withdrawn(self):
        withdrawn = state.Withdrawn()
        self.assertEqual(withdrawn.name(), "withdrawn")
        self.assertFalse(withdrawn.can_be_put())
        self.assertTrue(withdrawn.inform())
        self.check_states(withdrawn)

    def test_superseded(self):
        superseded = state.Superseded()
        self.assertEqual(superseded.name(), "superseded")
        self.assertFalse(superseded.can_be_put())
        self.assertFalse(superseded.inform())
        self.check_states(superseded)


if __name__ == "__main__":
    unittest.main()
