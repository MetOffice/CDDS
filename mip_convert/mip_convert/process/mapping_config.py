# (C) British Crown Copyright 2009-2022, Met Office.
# Please see LICENSE.md for license details.
import regex as re
from mip_convert.common import VersionString
from mip_convert.process.process import Mapping

DUPLICATE = 'duplicate mapping for "%s"'


class MappingTableError(Exception):
    pass


class MappingTableParser(object):
    """
    Parses a text based mapping table.  All lines except the header or comment
    line are parsed.

    Mapping table is assumed to start with a header and be terminated
    with a new line.

    Comment lines are ignored.  The comment character can be read (or set)
    using the class variable comment_char.

    """

    comment_char = '#'

    def __init__(self, version, line_parser):
        """
        @param version: the um version that the mappings will be required for.
                        although um version can be a string with minor versions
                        only the major version is used in comparisions to see whether
                        a mapping should be included or not.
        @param line_parser: an object that will parse individual mapping table lines.
        @type line_parser: object with interface as L{MappingTableLineParser}
        """
        self._version = version
        self._line_parser = line_parser
        self._mappings = dict()

    def _add_line(self):
        """
        process a line, makeing its information available to other api calls
        """
        if self._line_parser.get('published') not in self._mappings:
            self._mappings[self._line_parser.get('published')] = list()

        new_mapping = Mapping(self._line_parser.get('mapping'),
                              self._line_parser.get('units'),
                              self._line_parser.get('positive'),
                              self._line_parser.get('comment'),
                              )
        self._mappings[self._line_parser.get('published')].append(new_mapping)

    def _get_line_version(self):
        return self._line_parser.get('version')

    def _include_line(self, line):
        """
        checks to see whether a line should be included in table

        rejects comments and wrong _version mappings

        may have to parse the line and so has the side effect of making
        values from the line available else where (not sure this is great)
        """
        # TODO: feature envy smell
        yret = False
        if line[0] != self.comment_char:
            self._line_parser.set_line(line[:-1])
            line_version = self._get_line_version()
            if line_version in ('', ' ') or eval('VersionString("%s") %s' % (self._version, line_version)):
                yret = True
        return yret

    def read(self, file_obj):
        """
        read the mapping table from the file like object file_obj
        """
        file_obj.readline()  # skip first line as header
        for line in file_obj.readlines():
            if self._include_line(line):
                self._add_line()

    def getMapping(self, published):
        """
        returns the mapping against for the publised project/table/variable entry
        """
        mappings = self._mappings[published]
        if len(mappings) != 1:
            raise MappingTableError(DUPLICATE % published)
        return mappings[0]

    def getProcessor(self, published):
        """
        find a the processor for the mapping_id

        @param mapping_id: mapping id in the mapping table
        """
        return self.getMapping(published).getProcessor()


class LineException(Exception):
    pass


class MappingTableLineParser(object):
    """
    Parse a single line of the mapping table.
    The line is broken down into a set of entries, one for each column
    in the mapping table.

    These entries are made available through get_<entry> type methods.
    """

    headings = ('standard_name',
                'cell_methods',
                'units',
                'positive',
                'mapping',
                'lbproc',
                'version',
                'published',
                'notes',
                'comment')

    _lookup = dict(list(zip(headings, list(range(1, len(headings) + 1)))))
    _published_re = re.compile(r'\s*[\*\w\s]+\((\w+,\s*)?(\w+)\)')

    def _line_parse_problem(self):
        raise LineException("on line: '%s'" % self.line)

    def get(self, entry):
        """
        return the entry for the current line

        assumes: set_line(line) has already been called
        """
        return self.columns[self._lookup[entry]]

    def set_line(self, line):
        """
        line to be parsed
        """
        self.line = line
        columns = self.line.split('|')
        if len(columns) != len(self.headings) + 2:
            self._line_parse_problem()
        self.columns = [val.strip() for val in columns]


def getReadMapper(fname, version):
    """
    reads mapping table from fname for um version and returns a mapper.

    the mapper supports a getMapping(mapid) method.
    """
    mapper = MappingTableParser(version, MappingTableLineParser())
    fi = open(fname, 'r')
    mapper.read(fi)
    fi.close()
    return mapper
