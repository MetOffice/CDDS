# (C) British Crown Copyright 2024, Met Office.
# Please see LICENSE.rst for license details.
from abc import abstractmethod, ABCMeta

from cdds.common.request.request_section import Section


class SimpleValidation(object, metaclass=ABCMeta):

    def __int__(self, section: Section):
        self._section = section

    @abstractmethod
    def do_validations(self):
        pass
