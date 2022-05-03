# (C) British Crown Copyright 2020-2021, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = no-member
from hadsdk.inventory.dao import InventoryDAO


class InventoryDaoStub(InventoryDAO):
    def __init__(self, connection):
        self._connection = connection
