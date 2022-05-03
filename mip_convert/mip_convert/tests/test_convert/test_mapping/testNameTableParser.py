# (C) British Crown Copyright 2015-2021, Met Office.
# Please see LICENSE.rst for license details.

import unittest
from io import StringIO

from mip_convert.process.process import MappingError
from mip_convert.process.process import Mapping

from mip_convert.process.mapping_config import MappingTableParser, MappingTableLineParser, LineException
from mip_convert.process.mapping_config import MappingTableError


class AnyOldRecord(object):
    def meta_data(self, other):
        if hasattr(other, 'comment'):
            self.comment = other.comment
        self.units = other.units
        self.stash_history = other.stash_history
        self.positive = other.positive


class TestMapping(unittest.TestCase):
    def testEquality(self):
        mapping1 = Mapping('m01s01i001', 'K', '', 'comment')
        mapping2 = Mapping('m01s01i001', 'K', '', 'comment2')
        self.assertFalse(mapping1 == mapping2)

    def testCommentAddToVar(self):  # best place to test this?
        mapping = Mapping('m01s01i001', 'K', 'up', 'comment')
        variable = AnyOldRecord()
        mapping.addMetaData(variable, 100.)
        self.assertEqual(variable.comment, 'comment')
        self.assertEqual(variable.units, 'K')
        self.assertEqual(variable.stash_history, 'm01s01i001')
        self.assertEqual(variable.positive, 'up')

    def testTimeStepMapping(self):
        mapping = Mapping('m01s01i001/TIMESTEP', 'K', 'up', 'comment')
        variable = AnyOldRecord()
        mapping.addMetaData(variable, 100.)
        self.assertEqual(variable.comment, 'comment')
        self.assertEqual(variable.units, 'K')
        self.assertEqual(variable.stash_history, 'm01s01i001/TIMESTEP (TIMESTEP = 100.000000s)')
        self.assertEqual(variable.positive, 'up')

    def testNoCommentAddToVar(self):
        empty_comments = ('', ' ')
        for comment in empty_comments:
            mapping = Mapping('m01s01i001', 'K', 'up', comment)
            variable = AnyOldRecord()
            mapping.addMetaData(variable, 100.)
            self.assertFalse(hasattr(variable, 'comment'))


class TestMappingConstructorProblems(unittest.TestCase):

    def testNotImplemented(self):
        for expression in ('m01s01i001[level=1]', 'm01s01i001[level=sumall]', '(m01s01i235-m01s01i201)/m01s01i23'):
            self.assertRaises(NotImplementedError, Mapping, expression, None, '')

    def testPositiveAccepatble(self):
        self.assertRaises(MappingError, Mapping, 'm01s01i001', 'K', 'flp')


# mapping for a missing varid/mapping_id - will get key error for now


class TestMappingTableParser(unittest.TestCase):

    def set_line(self, line):
        """
        act as a stub line parser
        """
        self.lines.append(line)

    def get(self, entry):
        """
        act as a stub line parser
        """
        fields = {
            'mapping': 0,
            'version': 1,
            'units': 2,
            'published': 3,
            'positive': 4,
            'comment': 5
        }
        return self.lines[-1].split(':')[fields[entry]]

    def add_input(self, mapping, version, units, published, positive='', comment=''):
        self.input_vars.append((mapping, version, units, published, positive, comment))

    def add_comment(self, mapping, version, units, published):
        self.add_input(MappingTableParser.comment_char + mapping, version, units, published)

    def add_duplicate(self, mapping1, mapping2, version, units, published):
        for i in range(2):
            self.add_input(mapping1, version, units, published)

    def _makeDuplicateExample(self):
        self.varid = 'varid1'
        self.add_duplicate('mapping1', 'mapping2', self.version, 'm', self.varid)

    def setUp(self):
        self.input_vars = list()
        self.lines = list()
        self.units = 'm'
        self.version = '>=2.0'  # mapping table version

    def readLinesFromSequence(self, sequence, version):
        line = 'a header\n' + '\n'.join(sequence) + '\n'
        input_file = StringIO(line)
        self.table_parser = MappingTableParser(version, self)
        self.table_parser.read(input_file)

    def readFromVariables(self, version='2.0.1'):
        lines = [':'.join(part) + ':' + self.units for part in self.input_vars]
        self.readLinesFromSequence(lines, version)

    def testGetFullMappingErrorOnDuplicateMapping(self):
        self._makeDuplicateExample()
        self.readFromVariables()
        self.assertRaises(MappingTableError, self.table_parser.getMapping, self.varid)

    def testMapping(self):
        variable_id = 'varid'
        mapping = 'm01s01i000'
        self.add_input(mapping, self.version, 'm', variable_id)
        self.readFromVariables()
        self.assertEqual(Mapping(mapping, 'm', ''), self.table_parser.getMapping(variable_id))

    def testCommentLine(self):
        self.add_comment('mapping3', self.version, 'm', 'varid3')
        self.readFromVariables()
        self.assertRaises(KeyError, self.table_parser.getMapping, 'varid3')

    def testOnVersion(self):
        self.add_input('mapping_good', self.version, 'm', 'varid4')
        self.add_input('mapping', '<2.0', 'm', 'varid4')
        self.readFromVariables()
        self.assertEqual(Mapping('mapping_good', 'm', ''), self.table_parser.getMapping('varid4'))

    def testOnVersion66(self):
        self.add_input('mapping_good', '>= 6.6', 'm', 'varid4')
        self.readFromVariables(version='6.6.3')
        self.assertEqual(Mapping('mapping_good', 'm', ''), self.table_parser.getMapping('varid4'))
        self.add_input('mapping_good', '>= 5', 'm', 'varid5')
        self.readFromVariables(version='5.6.3')
        self.assertEqual(Mapping('mapping_good', 'm', ''), self.table_parser.getMapping('varid5'))

    def testWithPositive(self):
        self.add_input('mapping', self.version, 'K', 'var5', positive='up')
        self.readFromVariables()
        self.assertEqual(Mapping('mapping', 'K', 'up'), self.table_parser.getMapping('var5'))

        self.add_input('mapping', self.version, 'K', 'varUp', positive='Up')
        self.readFromVariables()
        self.assertEqual(Mapping('mapping', 'K', 'up'), self.table_parser.getMapping('varUp'))

    def testWithComment(self):
        self.add_input('mapping', self.version, 'K', 'var6', positive='up', comment='some text')
        self.readFromVariables()
        self.assertEqual(Mapping('mapping', 'K', 'up', 'some text'), self.table_parser.getMapping('var6'))


class TestLineParser(unittest.TestCase):
    # Not sure about units, lbproc etc. (not currently used)

    def setUp(self):
        self.line_parser = MappingTableLineParser()

    def testGetExamples(self):
        publisheds = ('CFMIP (CF1, varid)', 'CFMIP (CF1, varid)')
        for published in publisheds:
            line = '|standard_name|cell_methods|units|positive|mapping|lbproc|version| %s |notes|comment|' % published
            self.line_parser.set_line(line)
            self.assertEqual(published, self.line_parser.get('published'))
            for example in ('mapping', 'standard_name', 'units', 'version', 'positive', 'comment'):
                self.assertEqual(example, self.line_parser.get(example))

    def testInvalidLine(self):
        self.assertRaises(LineException, self.line_parser.set_line, 'invalid_line')


if __name__ == '__main__':
    unittest.main()
