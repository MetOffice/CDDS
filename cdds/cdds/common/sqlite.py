# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
"""
The :mod:`sqlite` module contains helper functions to simplify sqlite queries.
"""


def generate_insert_sql(table, columns, pk='id'):
    """
    A helper function to generate sql insert queries.

    Parameters
    ----------
    table : str
        Name of db table.
    columns : list
        List of column names.
    pk : str
        Name of the primary key (default 'id').

    Returns
    -------
    : str
        A string containing an insert query.
    """

    return 'INSERT INTO {} ({}, {}) VALUES (NULL, {})'.format(
        table, pk, ', '.join(columns), ', '.join(['?'] * len(columns))
    )


def execute_insert_query(cursor, table, values, pk='id'):
    """
    Executes insert query.

    Parameters
    ----------
    cursor : sqlite3.Cursor
        Db cursor.
    table : str
        Db table name.
    values : dict
        Dictionary containing column names and values to be inserted.
    pk : str
        Name of the primary key (default 'id').

    """
    cursor.execute(
        generate_insert_sql(table, values.keys(), pk),
        tuple(values.values())
    )


def execute_query(cursor, sql, params):
    """
    Executes generic sql query

    Parameters
    ----------
    cursor : sqlite3.Cursor
        A cursor instance
    sql : str
        Query string
    params : dict
        Dictionary containing values to interpolate into the query string

    Returns
    -------
    : sqlite3.Cursor
        Cursor object
    """
    return cursor.execute(*(sql, params))
