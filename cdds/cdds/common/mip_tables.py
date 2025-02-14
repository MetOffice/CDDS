# (C) British Crown Copyright 2017-2025, Met Office.
# Please see LICENSE.md for license details.

from os import listdir
from os.path import isfile, join
import json

# If a file matches one of the following suffixes, then it is ignored when loading MIP tables
NON_TABLE_FILE_SUFFIXES = ['_CV.json', '_coordinate.json', '_grids.json', '_formula_terms.json']


class MipTables(object):
    """A class encapsulating access and basic operations on mip tables"""

    def __init__(self, basedir):
        """
        A constructor.

        Parameters
        ----------
        basedir : str
            A path to a directory with json mip tables

        """

        self.META = [
            "long_name",
            "standard_name",
            "units",
            "cell_measures",
            "cell_methods"
        ]

        self._tables = {}
        self._variables = {}
        self._name_mappings = {}
        self._version = None
        self._load_tables_from_directory(basedir)

    @property
    def tables(self):
        """
        Returns a list of table names
        """
        return sorted(self._tables.keys())

    @property
    def version(self):
        """
        Returns version of mip tables
        """
        return self._version

    def get_variable_meta(self, table, variable, subset=True):
        """
        Retrieves a dictionary of metadata attributes associated with
        a particular variable from a provided mip table

        Parameters
        ----------
        table : str
            Name of the mip table, e.g. "Amon"
        variable : str
            Name of the variable, e.g. "pr"
        subset : bool
            If True only returns a long name, standard name and units
        """

        assert table in self._tables, (
            "Could not find MIP Table {}".format(table)
        )
        if variable not in self._tables[table]:
            assert (table, variable) in self._name_mappings, (
                "Variable {} missing in {}".format(variable, table)
            )
            key = self._name_mappings[(table, variable)]
        else:
            key = variable
        meta = self._tables[table][key]

        return {
            k: meta[k] for k in meta if not subset or k in self.META
        }

    def get_variables(self, table):
        """
        Retrieves a list of variables in a provided mip table

        Parameters
        ----------
        table : str
            Name of the mip table

        Returns
        ------
        : list
            List of variables
        """
        return self._variables[table]

    def _load_tables_from_directory(self, basedir):
        files = [f for f in listdir(basedir)
                 if isfile(join(basedir, f)) and all([not f.endswith(i) for i in NON_TABLE_FILE_SUFFIXES])]
        for filename in files:
            with open(join(basedir, filename)) as json_data:
                try:
                    d = json.load(json_data)
                    if "Header" in d:
                        table_name = d["Header"]["table_id"].split(" ")[-1]
                        if self.version is None:
                            self._version = d["Header"].get("data_specs_version", None)
                        self._tables[table_name] = d["variable_entry"]
                        self._variables[table_name] = []
                        for key, var_meta in d["variable_entry"].items():
                            self._variables[table_name].append(
                                key)
                            self._name_mappings[(
                                table_name, var_meta["out_name"]
                            )] = key
                except ValueError:
                    pass
        if len(list(self._tables.keys())) == 0:
            raise ValueError(
                "{} does not appear to contain valid mip tables".format(
                    basedir
                ))


class UserMipTables(MipTables):
    """A class encapsulating access and basic operations on mip tables"""

    def __init__(self, basedir):
        """
        A constructor.

        Parameters
        ----------
        basedir : str
            A path to a directory with json mip tables

        """

        super().__init__(basedir)

        self.META = [
            "cell_measures",
            "cell_methods",
            "comment",
            "dimensions",
            "frequency",
            "long_name",
            "modeling_realm",
            "ok_min_mean_abs",
            "ok_max_mean_abs"
            "out_name",
            "positive",
            "standard_name",
            "type",
            "units",
            "valid_min",
            "valid_max",
        ]
