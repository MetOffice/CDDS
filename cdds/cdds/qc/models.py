# (C) British Crown Copyright 2017-2021, Met Office.
# Please see LICENSE.md for license details.


import sqlite3
import os
from cdds.qc.constants import (
    QC_DB_FILENAME, STATUS_WARNING, STATUS_ERROR, STATUS_IGNORED,
    DS_TYPE_SINGLE_FILE, DS_TYPE_DATASET, SUMMARY_STARTED,
    SUMMARY_FAILED, SUMMARY_PASSED
)


def setup_db(db_file=QC_DB_FILENAME):
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
    if not db_file.endswith(".db") and db_file != ":memory:":
        db_file += ".db"
    if os.path.exists(db_file):
        conn = sqlite3.connect(db_file)
        conn.execute("PRAGMA foreign_keys = 1")
        return conn
    elif db_file != ":memory:":
        print("Creating database file {}".format(db_file))
    conn = sqlite3.connect(db_file)
    conn.execute("PRAGMA foreign_keys = 1")
    cursor = conn.cursor()
    create_sql = [
        (
            "CREATE TABLE qc_run "
            "(id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "started DATETIME DEFAULT (DATETIME('NOW')) NOT NULL, "
            "finished DATETIME, "
            "basepath TEXT NOT NULL, "
            "run_id INTEGER, "
            "mip_table TEXT)"
        ),
        (
            "CREATE TABLE qc_dataset "
            "(id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "validated DATETIME DEFAULT (DATETIME('NOW')) NOT NULL, "
            "filename TEXT NOT NULL, "
            "variable_directory TEXT NOT NULL, "
            "realization_index TEXT NOT NULL, "
            "model TEXT NOT NULL, "
            "experiment TEXT NOT NULL, "
            "mip_table TEXT NOT NULL, "
            "variant TEXT NOT NULL, "
            "variable TEXT NOT NULL, "
            "variable_name TEXT NOT NULL,"
            "grid TEXT NOT NULL, "
            "summary INTEGER NOT NULL, "
            "qc_run_id INTEGER NOT NULL, "
            "FOREIGN KEY(qc_run_id) REFERENCES qc_run(id))"
        ),
        (
            "CREATE TABLE qc_message "
            "(id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "message TEXT NOT NULL, "
            "status INTEGER NOT NULL, "
            "checker TEXT NOT NULL, "
            "qc_dataset_id INTEGER NOT NULL, "
            "FOREIGN KEY(qc_dataset_id) REFERENCES qc_dataset(id))"
        )
    ]
    for command in create_sql:
        cursor.execute(command)
    conn.commit()

    return conn


def get_qc_runs(cursor, run_id):
    """
    Executes a select query on the qc_run table filtering by run_id

    Parameters
    ----------
    cursor : sqlite3.Cursor
        A cursor instance
    run_id : int
        Run id

    Returns
    -------
    : sqlite3.Cursor
        Cursor object
    """
    return cursor.execute(
        "SELECT id, mip_table FROM qc_run WHERE run_id = ?", (run_id,)
    )


def get_qc_files(cursor, qc_run_id, all_errors=False):
    """
    Executes a select query on the qc_files table filtering by qc_run_id.

    Column order:
    - experiment
    - mip_table
    - variable
    - filename
    - error message

    Parameters
    ----------
    cursor : sqlite3.Cursor
        A cursor instance
    qc_run_id : int
        PK from the qc_run table
    all_errors : bool
        If True will also return ignored messages.

    Returns
    -------
    : sqlite3.Cursor
        Cursor object
    """
    skipped = 0 if all_errors else STATUS_IGNORED

    return cursor.execute(
        "SELECT qcd.experiment, qcd.mip_table, qcd.variable, qcd.filename, "
        "qcm.message FROM qc_dataset qcd "
        "INNER JOIN qc_message qcm ON qcm.qc_dataset_id = qcd.id "
        "WHERE qcd.qc_run_id = ? AND qcm.status != ?"
        "ORDER BY qcd.filename", (qc_run_id, skipped,)
    )


def get_error_counts(cursor, run_id, all_errors=False):
    """
    Executes a select query calculating distribution of errors per .

    Column order:
    - mip_table
    - variable
    - filename
    - error message count

    Parameters
    ----------
    cursor : sqlite3.Cursor
        A cursor instance
    run_id : int
        Run id

    Returns
    -------
    : sqlite3.Cursor
        Cursor object
    """
    skipped = 0 if all_errors else STATUS_IGNORED

    return cursor.execute(
        "SELECT qcd.mip_table,qcd.variable,qcd.filename,count(qcm.message) "
        "FROM qc_message qcm "
        "INNER JOIN qc_dataset qcd ON qcm.qc_dataset_id = qcd.id "
        "INNER JOIN qc_run qcr ON qcd.qc_run_id = qcr.id "
        "WHERE qcr.run_id = ? AND qcm.status != ?"
        "GROUP BY filename "
        "ORDER BY count(qcm.message) desc ", (run_id, skipped, )
    )


def get_errors_by_variable(cursor, run_id, all_errors=False):
    """
    Executes a select query calculating number of errors for every file in
    the qc run.

    Column order:
    - mip_table
    - variable
    - checker
    - error message
    - file count

    Parameters
    ----------
    cursor : sqlite3.Cursor
        A cursor instance
    run_id : int
        Run id from the qc_run table

    Returns
    -------
    : sqlite3.Cursor
        Cursor object
    """
    skipped = 0 if all_errors else STATUS_IGNORED

    return cursor.execute(
        "SELECT qcd.mip_table, qcd.variable, qcm.checker, qcm.message, "
        "count(qcd.filename) FROM qc_message qcm "
        "INNER JOIN qc_dataset qcd ON qcm.qc_dataset_id = qcd.id "
        "INNER JOIN qc_run qcr ON qcd.qc_run_id = qcr.id "
        "WHERE qcr.run_id = ? AND qcm.status != ? "
        "GROUP BY qcd.mip_table, qcd.variable, qcm.checker, qcm.message "
        "ORDER BY qcd.mip_table, qcd.variable ", (run_id, skipped)
    )


def get_aggregated_errors(cursor, run_id, all_errors=False):
    """
    Aggregates all errors and calculate a number of occurrences.

    Column order:
    - mip_table
    - checker
    - error message
    - file count
    - pipe-separated list of affected variables

    Parameters
    ----------
    cursor : sqlite3.Cursor
        A cursor instance
    run_id : int
        Run id from the qc_run table
    all_errors : bool
        If True will also return ignored messages.

    Returns
    -------
    : sqlite3.Cursor
        Cursor object
    """
    skipped = 0 if all_errors else STATUS_IGNORED

    return cursor.execute(
        "SELECT qcd.mip_table, qcm.checker, qcm.message, "
        "count(qcd.filename), group_concat(variable,'|') FROM qc_message qcm "
        "INNER JOIN qc_dataset qcd ON qcm.qc_dataset_id = qcd.id "
        "INNER JOIN qc_run qcr ON qcd.qc_run_id = qcr.id "
        "WHERE qcr.run_id = ? AND qcm.status != ?"
        "GROUP BY qcd.mip_table, qcm.checker, qcm.message "
        "ORDER BY count(qcd.filename) DESC, qcd.mip_table, qcd.variable ",
        (run_id, skipped)
    )


def get_validated_variables(cursor, run_id, all_errors=False):
    """
    Executes a select query returning a list of variables that passed the qc.

    Column order:
    - mip_table
    - variable_directory
    - variable

    Parameters
    ----------
    cursor : sqlite3.Cursor
        A cursor instance
    run_id : int
        Run id from the qc_run table
    all_errors : bool
        If True will also return ignored variables with ignored messages.

    Returns
    -------
    : sqlite3.Cursor
        Cursor object
    """
    skipped = 0 if all_errors else STATUS_IGNORED
    return cursor.execute(
        "SELECT qcd.mip_table, qcd.variable_directory, qcd.variable_name "
        "FROM qc_dataset qcd "
        "LEFT JOIN qc_message qcm ON qcm.qc_dataset_id = qcd.id "
        "AND qcm.status != ? "
        "INNER JOIN qc_run qcr ON qcd.qc_run_id = qcr.id "
        "WHERE qcr.run_id = ? "
        "GROUP BY qcd.mip_table, qcd.variable_directory,"
        "qcd.variable_name HAVING count(qcm.id) = 0 "
        "ORDER BY qcd.mip_table, qcd.variable_directory, "
        "qcd.variable_name ", (skipped, run_id, )
    )
