# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.


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
