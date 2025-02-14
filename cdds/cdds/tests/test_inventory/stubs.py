# (C) British Crown Copyright 2020-2025, Met Office.
# Please see LICENSE.md for license details.
# pylint: disable = no-member
from cdds.inventory.dao import InventoryDAO


class InventoryDaoStub(InventoryDAO):
    def __init__(self, connection):
        self._connection = connection
