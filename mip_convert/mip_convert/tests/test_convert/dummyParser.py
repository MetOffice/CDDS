# (C) British Crown Copyright 2015-2021, Met Office.
# Please see LICENSE.rst for license details.


class SafeConfigParser(object):
    """
    act as a stub config parser
    """

    def read(self, fname):
        self.read_file = fname
