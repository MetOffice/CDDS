# (C) British Crown Copyright 2015-2021, Met Office.
# Please see LICENSE.md for license details.
from mip_convert.load.pp.stash_code import from_header
from mip_convert.load.pp.stash_code import StashCode


class BaseHeader(object):
    DEFAULT_VALUE = {
        'lbyr': 1999,
        'lbmon': 1,
        'lbdat': 1,
        'lbdatd': 1,
        'lbhr': 0,
        'lbmin': 0,
        'lbtim': 122,
        'lbcode': 1,
        'lbhem': 1,
        'lbrow': 4,
        'lbnpt': 4,
        'lbext': 0,  # may change
        'lbrel': 1,  # not sure?
        'lbfc': 1,
        'lbcfc': 1,
        'lbproc': 128,
        'lbvc': 1,
        'lbrvc': 1,
        'lbexp': 1,
        'lbproj': 1,
        'lbtyp': 1,
        'lbsrce': '08021111',  # UM v8.2
        'lbuser1': 1,
        'lbuser4': 1,
        'lbuser5': 1,  # maychange
        'lbuser7': 1,
        'bdatum': 1,
        'bplat': 90,
        'bplon': 0,
        'bgor': 1,
        'bzy': -1,
        'bdy': 1,
        'bzx': -1,
        'bdx': 1,
        'bmdi': -99,  # maychange
        'bmks': 1,  # maychange
        'blev': 100

    }

    def __init__(self, **kwargs):
        for att in self.DEFAULT_VALUE:
            setattr(self, att, self.DEFAULT_VALUE[att])

        for kw, value in list(kwargs.items()):
            setattr(self, kw, value)

        self.set_valid_times(self.lbyr, self.lbmon, self.lbdat, kwargs)

    def set_valid_times(self, year, mon, dat, kwargs):
        self.lbyr = year
        self.lbmon = mon
        self.lbdat = dat

        self.lbyrd = self.lbyr
        if 'lbmond' not in kwargs:
            self.lbmond = self.lbmon + 1
        if 'lbdatd' not in kwargs:
            self.lbdatd = self.lbdat
        self.lbhrd = self.lbhr
        self.lbmind = self.lbmin

    def change_header(self, differ):
        for att in differ:
            default = getattr(self, att)
            setattr(self, att, 1 + default)

    def stash_code(self):
        return from_header(self)

    def getAttNames(self):
        return list(self.DEFAULT_VALUE.keys())

    def isInstantaneous(self):  # not sure this should really be there
        return self.lbtim / 10 in (0, 1) and self.lbproc == 0

    def __eq__(self, other):
        result = True
        for att in self.getAttNames():
            result = result and getattr(self, att) == getattr(other, att)
        return result
