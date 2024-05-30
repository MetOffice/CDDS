# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.


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
