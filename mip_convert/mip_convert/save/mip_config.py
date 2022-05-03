# (C) British Crown Copyright 2009-2022, Met Office.
# Please see LICENSE.rst for license details.
"""
A set of classes to represent MIP table entities in object form.
"""
import json
import regex as re


def _read_json(table_path):
    """Reads the mip table information from a json file."""
    with open(table_path, 'r') as fp:
        result = json.load(fp)
    return result


def _copy_atts(table_dict):
    """
    Copy the attributes from a json mip table to
    make them look like an old style mip table.
    """
    table_dict['atts'] = table_dict['Header']
    table_dict['atts']['project_id'] = table_dict['Header']['mip_era']
    table_dict['vars'] = table_dict['variable_entry']
    table_dict['axes'] = table_dict['axis_entry']


class MipTableFactory(object):
    """
    Class responsible for calling into a third party MIP table parser
    and returning a MIP table object.

    Checks that paths etc all exist.
    """

    TABLE = 'MIP table'

    def __init__(self, parser, path_checker):
        """
        return a MipTableFactory

          parser - object (module or class instance) with a parseMipTable
                   fucntion/method that returns a dictionary hierarchy
                   representation of the MIP table
          path_checker - object with a fullFileName method that
                   knows where to expect to find a file
        """
        self.parser = parser
        self.path_checker = path_checker
        self.tables = dict()

    def _read_table_dict(self, table_name):
        """
        Returns a dictionary version of the mip table with table_name.
        The MIP table can be either json or old style (CMIP5) format.
        """
        table_dict = dict()
        table_path = self.path_checker.fullFileName(table_name)
        if table_name.endswith('.json'):
            table_dict = _read_json(table_path)
            pattern = re.compile(r'[a-zA-Z0-9]+_([a-zA-Z0-9]+).json')
            match = pattern.match(table_name)
            coordinate_name = table_name.replace(match.group(1), 'coordinate')
            axes_path = self.path_checker.fullFileName(coordinate_name)
            table_dict.update(_read_json(axes_path))
            _copy_atts(table_dict)
        else:
            table_dict = self.parser.parseMipTable(table_path)
        return table_dict

    def _loadTable(self, table_name):
        """
        loads a table with the name table_name
        """
        table_dict = self._read_table_dict(table_name)
        table = MipTable(table_dict, table_name.endswith('.json'))
        self.tables[table_name] = table

    def getTable(self, table_name):
        """
        returns the MipTable oject corresponding to table_name
        """
        if table_name not in self.tables:
            self._loadTable(table_name)
        return self.tables[table_name]


class MipTable(object):
    """
    Class representing a mip table.

    This is an incomplete implementation and is simply enough to get going
    """

    def __init__(self, parsed_input, is_json=False):
        """
        return a MipTable based on parsed_input
          parsed_input  - a hierarchical dictionary representation of the
                          table contents
        """
        self.input = parsed_input
        self.is_json = is_json

    @property
    def _variables(self):
        """
        return the variable dictionary of the table
        """
        return self.input['vars']

    @property
    def project_id(self):
        """return the project id of this table"""
        return self.input['atts']['project_id']

    @property
    def table_id(self):
        """
        returns the id of this table
        """
        table = 'Table '
        if self.input['atts']['table_id'].startswith(table):
            return self.input['atts']['table_id'][len(table):]
        else:
            return self.input['atts']['table_id']  # right thing to do?

    @property
    def table_name(self):
        """
        returns the table name for this mip table

        the table name is distinct from the table id as it usually include the project
        name too.
        """
        name = self.project_id + '_' + self.table_id
        if self.is_json:
            name = name + '.json'
        return name

    @property
    def generic_levels(self):
        """returns the generic levels named in the table"""
        result = ''
        if 'generic_levels' in self.input['atts']:
            result = self.input['atts']['generic_levels']
        return result

    def variable_names(self):
        """
        return the list of variable entries in this table
        """
        return list(self._variables.keys())

    def hasVariable(self, variable):
        """
        returns True if the table contains variables
        """
        return variable in self._variables

    def getVariable(self, variable):
        """
        return a MipVariable for variable
        """
        return MipVar(self._variables[variable])

    @property
    def axes(self):
        """
        returns a dictionary of the MipAxes in the table
        """
        axxes = dict()
        for (entry, axis) in list(self.input['axes'].items()):
            axxes[entry] = MipAxis(entry, axis)
        return axxes


class MipVar(object):
    """
    Minimal class to represent a MIP table variable entry
    """

    def __init__(self, parsed_var):
        """
        return a MipVar based on the dictionary parsed_var
        """
        self.parsed = parsed_var

    @property
    def dimensions(self):
        """
        returns a list of dimension entry names for this variable
        """
        return self.parsed['dimensions'].split()


class MipAxis(object):
    """
    Minimal class to represnt a MIP table axis entry
    """

    def __init__(self, entry, parsed_axis):
        """
        return a MipAxis for entry based on dictionary parsed_axis
        """
        self.entry = entry
        self.parsed = parsed_axis

    @property
    def axis(self):
        """
        return the axis attribute for this axis if axis attribute does not
        exist returns the entry.
        """
        # In the old MIP tables, if there was no appropriate value for the 'axis' attribute
        # for a particular 'axis_entry', the 'axis' attribute did not exist. However, in the
        # new JSON MIP tables, the 'axis' attribute always exists; the value is set equal to
        # an empty string if there is no appropriate value. Ensure this method works in both cases.
        result = ''
        if 'axis' in self.parsed:
            result = self.parsed['axis']
        if result == '':
            result = self.entry
        return result
