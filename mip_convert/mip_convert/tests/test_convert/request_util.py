# (C) British Crown Copyright 2015-2025, Met Office.
# Please see LICENSE.md for license details.
"""Stub classes used in more than one test module"""


class StubRequest(object):
    def __init__(self, stream, variable, table):
        self.stream = stream
        self._entry = variable
        self._table = table
        self.number_processed = 0
        self.fail_on_read = False
        self.fail_exception = None

    def output_name(self):
        return '%s:%s' % (self._table, self._entry)

    def _process(self, input_file):
        self.number_processed = self.number_processed + 1
        self.file_processed = input_file
        if self.fail_on_read:
            raise self.fail_exception
        return self.var

    def read_and_write(self, input_file):
        self.output.write_var(self._process(input_file))
