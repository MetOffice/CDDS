# (C) British Crown Copyright 2026, Met Office.
# Please see LICENSE.md for license details.
import unittest

from cdds.misc.update_variables_from_validate import get_newest_validate_log


class TestGetNewestLog(unittest.TestCase):

    def test_read_variables_file(self):
        logs = ['validate_ap6_2026-09-07T0951Z.log', 'validate_ap6_2026-09-09T1220Z.log',
                'validate_ap6_2026-09-09T0619Z.log', 'validate_ap6_2026-09-09T0620Z.log']
        result = get_newest_validate_log(logs)
        expected = 'validate_ap6_2026-09-09T1220Z.log'
        msg = ("Error: Failed to correctly identify the newest extract_validate log. "
               f"Expected '{expected}`, got `{result}`")
        self.assertEqual(result, expected, msg)


if __name__ == "__main__":
    unittest.main()
