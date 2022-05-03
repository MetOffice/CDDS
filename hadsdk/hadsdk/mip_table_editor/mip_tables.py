# (C) British Crown Copyright 2021, Met Office.
# Please see LICENSE.rst for license details.

import json
import pprint
import subprocess
import tempfile

from os import listdir, remove, environ
from os.path import isfile, join

from cdds_common.common.io import read_json, write_json
from hadsdk.mip_table_editor.constants import CV_OBJECT, TABLE_OBJECT, VARIABLE_OBJECT


def editor(input_dict):
    """
    A general function that takes a python dictionary and opens it for editing in a text editor as
    a .json formatted file, it then returns the edited .json  file as a dictionary.
    PARAMETERS
    ----------
    input_dict: dictionary
        A dictionary representing the .json fields to be edited.

    RETURNS
    -------
    output_dict: dictionary
        The .json file converted to a dictionary
    """

    temporary_file = tempfile.NamedTemporaryFile(delete=False)

    with open(temporary_file.name, 'w') as f:
        f.write(json.dumps(input_dict, indent=4, separators=(',', ':'), sort_keys=False))

    try:
        text_editor = environ['EDITOR']
    except KeyError as error:
        raise error

    subprocess.run([text_editor, temporary_file.name])

    with open(temporary_file.name, 'r') as f:
        # valid .json check here.
        output_dict = json.load(f)

    return output_dict


class OperationBaseClass():
    """
    A base class for holding common methods between the ControlledVocabulary,
    MipTable, and MipTableVariable.
    """

    def switch_statement(self):
        if self.arguments.action == 'add':
            self._add()
        elif self.arguments.action == 'clone':
            self._clone()
        elif self.arguments.action == 'modify':
            self._modify()
        elif self.arguments.action == 'remove':
            self._remove()
        elif self.arguments.action == 'view':
            self._view()
        else:
            print('"{}" is not a valid action'.format(self.arguments.action))

    def send_to_editor(self, dictionary):
        return editor(dictionary)

    def read_miptable_file(self, path):
        self.files = [f for f in listdir(path) if isfile(join(path, f)) and f != 'CMIP6_CV.json']

        for table in self.files:
            key = table.split('_')[1].split('.json')[0]

            if self.arguments.table == key:
                return join(path, table)

    def update_dictionary(self, dictionary):
        self.cv_dict['CV'][self.arguments.domain].update(dictionary)


class ControlledVocabulary(OperationBaseClass):

    def __init__(self, arguments, cv_path=None):
        self.arguments = arguments
        self.setup()
        self.switch_statement()
        write_json(self.cv_filepath, self.cv_dict, indent=4, sort_keys=False, separators=(',', ':'))

    def setup(self):
        '''Convert the CMIP6_CV.json to a python dictionary'''

        self.cv_files = [f for f in listdir(self.arguments.path) if isfile(join(self.arguments.path, f))]

        self.cv_filepaths = [path for path in self.cv_files if path.endswith('CV.json')]

        if len(self.cv_filepaths) != 1:
            raise IndexError

        self.cv_filepath = join(self.arguments.path, self.cv_filepaths[0])
        self.cv_dict = read_json(self.cv_filepath)

    def check_key_exists(self):
        pass

    def _add(self):
        dictionary = CV_OBJECT[self.arguments.domain]
        dictionary = {self.arguments.name: dictionary}
        self.new_experiment_dict = self.send_to_editor(dictionary)
        self.update_dictionary(self.new_experiment_dict)

    def _clone(self):
        dictionary = self.cv_dict['CV'][self.arguments.domain][self.arguments.name]
        dictionary = {self.arguments.name: dictionary}
        self.new_experiment_dict = self.send_to_editor(dictionary)
        if self.arguments.name in self.new_experiment_dict.keys():
            print("Cannot use clone to overwrite existing {}".format(self.arguments.domain))
        else:
            self.update_dictionary(self.new_experiment_dict)

    def _modify(self):
        dictionary = self.cv_dict['CV'][self.arguments.domain][self.arguments.name]
        dictionary = {self.arguments.name: dictionary}
        self.new_experiment_dict = self.send_to_editor(dictionary)
        self.cv_dict['CV'][self.arguments.domain].pop(self.arguments.name)
        self.update_dictionary(self.new_experiment_dict)

    def _remove(self):
        self.cv_dict['CV'][self.arguments.domain].pop(self.arguments.name)

    def _view(self):
        pp = pprint.PrettyPrinter()

        if (self.arguments.name is not None) and (self.arguments.key is False):
            pp.pprint(self.cv_dict['CV'][self.arguments.domain][self.arguments.name])
        elif (self.arguments.name is None) and (self.arguments.key is False):
            pp.pprint(self.cv_dict['CV'][self.arguments.domain])
        elif (self.arguments.name is not None) and (self.arguments.key is True):
            pp.pprint(self.cv_dict['CV'][self.arguments.domain][self.arguments.name].keys())
        elif (self.arguments.name is None) and (self.arguments.key is True):
            pp.pprint(self.cv_dict['CV'][self.arguments.domain].keys())


class MipTable(OperationBaseClass):

    def __init__(self, arguments):
        self.arguments = arguments
        self.setup()
        self.switch_statement()

    def setup(self):
        if self.arguments.action != 'add':
            self.mip_table_file = self.read_miptable_file(self.arguments.path)

    def print_tables(self):
        for table in self.table_paths:
            print(table)

    def _write(self, dictionary):
        self.cv_dict['CV'][self.arguments.domain].update(dictionary)

    def _add(self):
        path = join(self.arguments.path, 'CMIP6_{}.json'.format(self.arguments.table))
        write_json(path, TABLE_OBJECT, indent=4, sort_keys=False, separators=(',', ':'))

    def _clone(self):
        dictionary = read_json(self.mip_table_file)
        dictionary = self.send_to_editor(dictionary)
        new_path = join(self.arguments.path, 'CMIP6_{}.json'.format(self.arguments.name))
        write_json(new_path, dictionary, indent=4, sort_keys=False, separators=(',', ':'))

    def _modify(self):
        dictionary = read_json(self.mip_table_file)
        dictionary = self.send_to_editor(dictionary)
        write_json(self.mip_table_file, dictionary, indent=4, sort_keys=False, separators=(',', ':'))

    def _remove(self):
        remove(self.mip_table_file)

    def _view(self):
        pp = pprint.PrettyPrinter()
        pp.pprint(read_json(self.mip_table_file))


class MipTableVariable(OperationBaseClass):

    def __init__(self, arguments):
        self.arguments = arguments
        self.setup()
        self.switch_statement()

    def setup(self):
        self.mip_table_file = self.read_miptable_file(self.arguments.path)
        self.mip_table_dict = read_json(self.mip_table_file)

    def update_dictionary(self, dictionary):
        self.mip_table_dict['variable_entry'].update(dictionary)

    def _add(self):
        dictionary = {self.arguments.variable: VARIABLE_OBJECT}
        self.new_experiment_dict = self.send_to_editor(dictionary)
        self.update_dictionary(self.new_experiment_dict)
        write_json(self.mip_table_file, self.mip_table_dict, indent=4, sort_keys=False, separators=(',', ':'))

    def _clone(self):
        dictionary = self.mip_table_dict['variable_entry'][self.arguments.variable]
        dictionary = {self.arguments.variable: dictionary}
        self.new_experiment_dict = self.send_to_editor(dictionary)
        self.update_dictionary(self.new_experiment_dict)
        write_json(self.mip_table_file, self.mip_table_dict, indent=4, sort_keys=False, separators=(',', ':'))

    def _modify(self):
        dictionary = self.mip_table_dict['variable_entry'][self.arguments.variable]
        self.new_experiment_dict = self.send_to_editor(dictionary)
        self.new_experiment_dict = {self.arguments.variable: self.new_experiment_dict}
        self.update_dictionary(self.new_experiment_dict)
        write_json(self.mip_table_file, self.mip_table_dict, indent=4, sort_keys=False, separators=(',', ':'))

    def _remove(self):
        self.mip_table_dict['variable_entry'].pop(self.arguments.variable)
        write_json(self.mip_table_file, self.mip_table_dict, indent=4, sort_keys=False, separators=(',', ':'))

    def _view(self):
        pp = pprint.PrettyPrinter()
        pp.pprint(self.mip_table_dict['variable_entry'][self.arguments.variable])
