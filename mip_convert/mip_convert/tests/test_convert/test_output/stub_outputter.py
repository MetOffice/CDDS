# (C) British Crown Copyright 2015-2021, Met Office.
# Please see LICENSE.md for license details.


class StubOutputterFactory(object):

    def getSaver(self, table, entry, outputs_per_file):
        return NullOutputter()

    def close(self):
        pass


class NullOutputter(object):

    def write_var(self, variable):
        pass


class StubCmor(object):
    def setup(self, *args, **kwargs):
        pass

    def dataset(self, *args, **kwargs):
        pass

    def axis(self, *args, **kwargs):
        return 0

    def variable(self, *args, **kwargs):
        return 0

    def write(self, *args, **kwargs):
        pass

    def close(self, *args, **kwargs):
        pass

    def load_table(self, *args, **kwargs):
        return 0
