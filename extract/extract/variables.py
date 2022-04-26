# (C) British Crown Copyright 2016-2021, Met Office.
# Please see LICENSE.rst for license details.
"""
Package to establish required output variables to be supported by a CDDS
extract process

"""

import json

from extract.common import byteify


class Variables(object):
    """
    Provides methods for obtaining information on output variables to
    be produced by CDDS.
    """

    def __init__(self, process_type):
        """Initialises variables information

        Parameters
        ----------
        process_type: str
            process type (e.g. extract)

        """
        self.process_type = process_type
        self.variables = {}
        self.var_list = []
        self.missing_var = []

    def get_variables(self, var_file):
        """Opens variables file and returns content in python dict.

        Parameters
        ----------
        var_file: str
            path to variables file

        Results
        -------
        dict
            information from variables file (or False if not successful)
        """
        try:
            with open(var_file, 'r') as variables_file:
                self.variables = json.load(variables_file)
                if not self.variables:
                    return False
                else:
                    return self.variables

        except IOError:
            return False

    def create_variables_list(self, file_content):
        """Convert variables from dict into a list of var/miptable/streams.

        Parameters
        ----------
        file_content: dict
            contains required variables in standard format

        Results
        -------
        list of dict
            variable name/mip table pairs - dict per variable
        """
        for var in file_content['requested_variables']:
            if var['active']:
                self.var_list.append(
                    {
                        "name": str(var['label']),
                        "table": str(var['miptable']),
                        "stream": str(var["stream"])
                    })
            else:
                reason_str = "not active "
                for comment in var['comments']:
                    reason_str += "%s, " % comment

                self.missing_var.append({"name": var['label'],
                                         "table": var['miptable'],
                                         "reason": reason_str})

        return self.var_list

    def missing_variables_list(self):
        """Returns list of missing variables from the variables file.
        Information returned includes:

            name   str  variable name
            table  str  MIP table variables referenced in
            reason str  reason why missing

        Returns
        -------
        list of dict
            missing variable information - dict per variable
        """
        return self.missing_var
