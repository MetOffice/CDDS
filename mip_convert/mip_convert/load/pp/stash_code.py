# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
import regex as re

msi_regex = re.compile(r"m(\d{2})s(\d{2})i(\d{3})")
section_factor = 1000


class StashCode(object):
    """
    A stash code made up of model, section, item, can have different representations.
    This class deals with those representations
    """

    def __init__(self, model, section, item):
        self.model = int(model)
        self.section = int(section)
        self.item = int(item)

    def _asSecItem(self):
        """
        returns the stash code as an integer in format similar to ppfp
        """
        return self.section * section_factor + self.item

    def asSecItem(self):
        """
        returns the stash code in a string formatted similar to ppfp
        """
        return str(self._asSecItem())

    def asMsi(self):
        """
        returns the stash code in the fotmat used in the mapping table
        """
        return 'm%02ds%02di%03d' % (self.model, self.section, self.item)

    def asDict(self):
        return {'lbuser7': self.model, 'lbuser4': self._asSecItem()}

    def __eq__(self, other):
        """
        returns True if other stash code is equivalent to this one
        """
        return self.section == other.section and self.item == other.item and self.model == other.model

    # what about hashcode?


def from_msi(msi):
    """
    construct a stash code from a string "mXXsXXiXXX\"
    """
    match = msi_regex.search(msi)

    if match:
        model = match.group(1)
        section = match.group(2)
        item = match.group(3)
    else:
        raise ValueError("stash code '%s' does not match '%s'" % (msi, msi_regex.pattern))

    return StashCode(model, section, item)


def from_header(header):
    """
    constructs a stash code based on pp header elements
    """
    model = header.lbuser7
    section = header.lbuser4 // section_factor
    item = header.lbuser4 - section * section_factor
    return StashCode(model, section, item)
