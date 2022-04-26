# (C) British Crown Copyright 2015-2021, Met Office.
# Please see LICENSE.rst for license details.


class StubParser(object):
    def __init__(self):
        self.sections = dict()

    def add(self, section, option, value):
        if section not in self.sections:
            self.sections[section] = dict()

        self.sections[section][option] = value

    def addList(self, section, option, values):
        self.add(section, option, ' '.join(values))

    def get(self, section, option):
        return self.sections[section][option]

    def has_option(self, section, option):
        return option in self.sections[section]
