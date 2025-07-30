# (C) British Crown Copyright 2025, Met Office.
# Please see LICENSE.md for license details.

from cdds.misc.system_information import check_environment_variables


def test_system_information_valid():
    result = check_environment_variables()
    assert result == 0
