# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
# pylint: disable = no-member
from cdds.inventory.dao import InventoryDAO


class InventoryDaoStub(InventoryDAO):
    def __init__(self, connection):
        self._connection = connection
