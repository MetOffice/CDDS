# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.

import logging
import sqlite3
import os

from cdds.common.sqlite import execute_insert_query, execute_query


def setup_db(db_file):
    """
    Initialises a qc database.

    Parameters
    ----------
    db_file : str
        Path to the database file.

    Returns
    -------
    : sqlite3.Connection
        Database connection instance.
    """
    conn = connect(db_file)
    conn.execute('PRAGMA foreign_keys = 1')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    dictionary_tables = ['mip_era', 'mip', 'institution', 'model', 'mip_table', 'experiment', 'grid', 'status']
    create_sql = []
    for dictionary_table in dictionary_tables:
        create_sql.append(
            'CREATE TABLE {} '
            '(id INTEGER PRIMARY KEY AUTOINCREMENT, '
            'created DATETIME DEFAULT (DATETIME(\'NOW\')) NOT NULL, '
            'name TEXT NOT NULL)'.format(dictionary_table)
        )
    create_sql += [
        (
            'CREATE TABLE variable'
            '(id INTEGER PRIMARY KEY AUTOINCREMENT, '
            'created DATETIME DEFAULT (DATETIME(\'NOW\')) NOT NULL, '
            'name TEXT NOT NULL, '
            'standard_name TEXT, '
            'out_name TEXT, '
            'long_name TEXT)'
        ),
        (
            'CREATE TABLE dataset '
            '(id INTEGER PRIMARY KEY AUTOINCREMENT, '
            'created DATETIME DEFAULT (DATETIME(\'NOW\')) NOT NULL, '
            'changed DATETIME DEFAULT (DATETIME(\'NOW\')) NOT NULL, '
            'variant TEXT NOT NULL, '
            'mip_era_id INTEGER NOT NULL, '
            'mip_id INTEGER NOT NULL, '
            'institution_id INTEGER NOT NULL, '
            'model_id INTEGER NOT NULL, '
            'mip_table_id INTEGER NOT NULL, '
            'variable_id INTEGER NOT NULL, '
            'experiment_id INTEGER NOT NULL, '
            'status_id INTEGER NOT NULL, '
            'grid_id INTEGER NOT NULL, '
            'timestamp INTEGER NOT NULL, '
            'dataset_id TEXT NOT NULL, '

            'FOREIGN KEY(mip_era_id) REFERENCES mip_era(id),'
            'FOREIGN KEY(mip_id) REFERENCES mip(id),'
            'FOREIGN KEY(institution_id) REFERENCES institution(id),'
            'FOREIGN KEY(model_id) REFERENCES model(id),'
            'FOREIGN KEY(mip_table_id) REFERENCES mip_table(id),'
            'FOREIGN KEY(variable_id) REFERENCES variable(id),'
            'FOREIGN KEY(experiment_id) REFERENCES experiment(id)'
            'FOREIGN KEY(status_id) REFERENCES status(id)'
            'FOREIGN KEY(grid_id) REFERENCES grid(id)'
            ')'
        ),
        (
            'CREATE TABLE netcdf_file'
            '(id INTEGER PRIMARY KEY AUTOINCREMENT, '
            'created DATETIME DEFAULT (DATETIME(\'NOW\')) NOT NULL, '
            'filesize INTEGER NOT NULL DEFAULT 0, '
            'filename TEXT NOT NULL, '
            'mass_path TEXT NOT NULL, '
            'dataset_id INTEGER NOT NULL, '
            'FOREIGN KEY(dataset_id) REFERENCES dataset(id))'
        )
    ]
    for command in create_sql:
        cursor.execute(command)
    conn.commit()

    return conn


def connect(db_file):
    """
    Connect to the qc database.

    Parameters
    ----------
    db_file : str
        Path to the database file.

    Returns
    -------
    : sqlite3.Connection
        Database connection instance.
    """
    logger = logging.getLogger(__name__)
    if not db_file.endswith('.db') and db_file != ':memory:':
        db_file += '.db'
    if os.path.exists(db_file):
        conn = sqlite3.connect(db_file)
        conn.execute('PRAGMA foreign_keys = 1')
        conn.row_factory = sqlite3.Row
        return conn
    elif db_file != ':memory:':
        logger.info('Creating database file {}'.format(db_file))

    conn = sqlite3.connect(db_file)
    return conn


def get_row_id_by_column_value(cursor, table_name, value, col_name='name', populate=True):
    """
    Searches database table for a row with column having provided value and returns the row id.
    If the `populate` parameter is True and the row does not exists, inserts a new row and returns the row id.

    Parameters
    ----------
    cursor : sqlite3.Cursor
        Db cursor.
    table_name : str
        Table name
    value : str
        Searched value
    col_name : str
        Name of the column that should contain the matching value
    populate : bool
        If True and the row cannot be found, it will be automatically inserted

    Returns
    -------
    : int
        Primary key of the row
    """
    sql = 'SELECT id FROM {} WHERE {} = :{}'.format(table_name, col_name, col_name)
    row = execute_query(cursor, sql, {col_name: value}).fetchone()
    if row is None:
        if populate:
            execute_insert_query(cursor, table_name, {col_name: value})
            row_id = cursor.lastrowid
        else:
            row_id = None
    else:
        row_id = row['id']
    return row_id


def build_sql_query(facets):
    """
    Builds a select query for selecting datasets matching given facets

    Parameters
    ----------
    facets: dict
        Dictionary of facets and their values

    Returns
    -------
    : string
        Interpolated query string
    """

    COLUMN_MAP = {
        'mip_era': 'mip_era.name',
        'mip': 'mip.name',
        'model': 'model.name',
        'experiment': 'experiment.name',
        'variant': 'variant',
        'mip_table': 'mip_table.name',
        'variable': 'variable.name',
        'institution': 'institution.name',
        'grid': 'grid.name',
        'status': 'current_status',
    }

    condition = ['{} = :{}'.format(COLUMN_MAP[key], key) for key, val in facets.items() if val is not None]
    sql = (
        'SELECT d.id, d.created, d.changed, d.timestamp, d.variant, d.dataset_id, '
        'mip.name as mip_name, institution.name as institution_name, '
        'model.name as model_name, experiment.name as experiment_name, '
        'mip_era.name as mip_era_name, '
        'mip_table.name as mip_table_name, variable.name as variable_name, '
        'status.name as current_status, grid.name as grid_name '
        'FROM dataset d '
        'INNER JOIN mip ON d.mip_id = mip.id '
        'INNER JOIN mip_era ON d.mip_era_id = mip_era.id '
        'INNER JOIN model ON d.model_id = model.id '
        'INNER JOIN experiment ON d.experiment_id = experiment.id '
        'INNER JOIN institution ON d.institution_id = institution.id '
        'INNER JOIN mip_table ON d.mip_table_id = mip_table.id '
        'INNER JOIN grid ON d.grid_id = grid.id '
        'INNER JOIN variable ON d.variable_id = variable.id '
        'INNER JOIN status ON d.status_id = status.id '
        'WHERE {} '
    ).format(' AND '.join(condition))
    return sql


def populate_dataset_dictionary(cursor, facet_dict):
    """
    A helper function to populate a dictionary of facets with matching primary key values from inventory.

    Parameters
    ----------
    cursor : sqlite3.Cursor
        Db cursor
    facet_dict : dict
        Dictionary containing facet names and their values

    Returns
    -------
    : dict
        A dictionary of facet IDs and database PKs.
    """
    return {
        '{}_id'.format(facet): get_row_id_by_column_value(cursor, facet, value) for facet, value in facet_dict.items()
    }


def get_simulation_datasets(cursor, mip_era, mip, model, experiment, variant, status):
    """
    A helper function to populate a dictionary of facets with matching primary key values from inventory.

    Parameters
    ----------
    cursor : sqlite3.Cursor
        Db cursor
    facet_dict : dict
        Dictionary containing facet names and their values

    Returns
    -------
    : list
        A list of database rows
    """

    facets = {'mip_era': mip_era, 'mip': mip, 'model': model, 'experiment': experiment, 'variant': variant,
              'status': status}
    sql = build_sql_query(facets)
    return execute_query(cursor, sql, facets).fetchall()


def is_expired(connection):
    """
    Returns if the given connection is still active

    Parameters
    ----------
    connection: sqlite3.Connection
        connection to the SQLite Database

    Returns
    -------
    : bool
        True if connection is inactive and
        expired otherwise False
    """
    logger = logging.getLogger(__name__)
    result = False
    try:
        cursor = connection.cursor()
        cursor.execute('SELECT SQLITE_VERSION()')
    except sqlite3.Error as error:
        logger.debug('Database connection is expired: {}', error)
        result = True
    return result
