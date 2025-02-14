# (C) British Crown Copyright 2020-2025, Met Office.
# Please see LICENSE.md for license details.
from logging import CRITICAL, DEBUG


class BaseCheckResult(object):

    def __init__(self, passed, message):
        self._passed = passed
        self._message = message

    @property
    def passed(self):
        return self._passed

    @property
    def message(self):
        return self._message

    @property
    def level(self):
        return DEBUG if self._passed else CRITICAL


class ValidationError(Exception):
    pass
