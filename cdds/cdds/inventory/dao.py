# (C) British Crown Copyright 2020-2025, Met Office.
# Please see LICENSE.md for license details.
"""
The :mod:`dao.py` module contains all necessary object and
methods to access the inventory database
"""
import enum

import cdds.inventory.db_models as inventory
import cdds.common as common


class InventoryDAO(object):
    """
    Database access object holds a connection to the
    inventory database and provides access methods
    """
    _connected = False

    def __init__(self, db_file):
        """
        Creates a class instance, checks if the given inventory configuration file exists
        and creates a new connection to the inventory database

        Parameters
        ----------
        db_file: str
            path to the inventory configuration file
        """
        self._db_file = db_file
        self._check_db_file()
        self._connection = inventory.connect(self._db_file)

    def _check_db_file(self):
        if self._db_file is None or self._db_file == '':
            raise IOError('Database file must be set.')
        common.check_file(self._db_file)

    def _check_connection(self):
        if inventory.is_expired(self._connection):
            self._connection = inventory.connect(self._db_file)

    def close(self):
        """
        Closes the inventory database connection
        """
        if not inventory.is_expired(self._connection):
            self._connection.close()
        InventoryDAO._connected = False

    def get_variables_data(self, model, experiment, variant_label, mip_era=None, institution=None):
        """
        Returns all variables specified by given experiment, model, variant,
        MIP era and institution.

        Parameters
        ----------
        model:  str
            name of the simulation model
        experiment: str
            ID of the experiment
        variant_label: str
            Label of the variant
        mip_era: str (optional)

        institution: str (optional)

        Returns
        -------
        : :class:`DBData`
            contains all variables in the inventory database
        """
        self._check_connection()

        facets = self._build_facets(model, experiment, variant_label, mip_era, institution)

        sql = inventory.build_sql_query(facets)
        cursor = self._connection.cursor()
        data = cursor.execute(sql, facets).fetchall()
        return DBVariableData(data)

    @staticmethod
    def _build_facets(model, experiment, variant, mip_era, institution):
        facets = {
            'model': model,
            'experiment': experiment,
            'variant': variant
        }

        if mip_era is not None:
            facets['mip_era'] = mip_era
        if institution is not None:
            facets['institution'] = institution

        return facets


class DBVariableData(object):
    """
    Contains the data of variables in the inventory
    data base specified by the key `mip_table.variable_name`
    """

    def __init__(self, db_data):
        """
        Parameters
        ----------
        db_data: list of list of str
            rows in the database containing the variable data
        """
        self._row = {row[5]: DBVariable(row) for row in db_data}
        self._variables_data = {(row[11], row[12]): DBVariable(row) for row in db_data}

    def get_variable(self, mip_table, variable_name):
        """
        Returns the data of the variable having given mip table and name

        Parameters
        ----------
        mip_table: str
            MIP table of the requested variable
        variable_name: str
            name of the requested variable

        Return
        ------
        :`cdds.inventory.dao.DBVariable`
            data of the variable in the database
        """
        identifier = (mip_table, variable_name)
        return self._variables_data[identifier]


class DBVariable(object):
    """
    Database variable and its information containing in the
    inventory database
    """

    def __init__(self, db_data):
        """
        Parameters
        ----------
        db_data: list of str
            data row of one variable in the inventory database
        """
        self._data = db_data

    def has_not_status(self, status):
        return self._data[13] != status.value

    @property
    def id(self):
        return self._data[5]

    @property
    def mip(self):
        return self._data[6]

    @property
    def mip_era(self):
        return self._data[10]

    @property
    def experiment(self):
        return self._data[9]

    @property
    def model(self):
        return self._data[8]

    @property
    def variant(self):
        return self._data[4]

    @property
    def mip_table(self):
        return self._data[11]

    @property
    def name(self):
        return self._data[12]

    @property
    def status(self):
        return self._data[13]

    @property
    def institute(self):
        return self._data[7]

    @property
    def version(self):
        return self._data[3]

    @property
    def grid(self):
        return self._data[14]


class DBVariableStatus(enum.Enum):
    """
    Define status of variables in the inventory database
    """
    AVAILABLE = 'available'
    EMBARGOED = 'embargoed'
    IN_PROGRESS = 'in progress'
