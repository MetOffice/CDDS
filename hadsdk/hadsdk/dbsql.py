# (C) British Crown Copyright 2016-2021, Met Office.
# Please see LICENSE.rst for license details.
"""
Class for accessing mysql/mariadb database
"""
from configparser import ConfigParser
# import HTMLParser
import os
import re

# import MySQLdb

from hadsdk.db_exception import (
    DaoConnectionException, DaoInvalidInputException)


class SqlDb(object):
    """ Parent class for handling access to a mysql/mariadb database.
    """

    def __init__(self, connect_env):
        """Sets database connection credentials. The username and
        password to use for the specified section are retrieved from
        the `cremdb` section of  the `$HOME/.cdds_credentials` file.

        Parameters
        ----------
        connect_env : dict
            Host and database name for connection
        """
        self.dbname = connect_env.get("dbname", None)
        self.host = connect_env.get("host", None)
        self.user, self.passwd = retrieve_credentials()
        self.dbconn = None

    def connect(self):
        """Connects to mysql/mariadb database through python MySQLdb API

        """
        if (self.dbname is not None and self.host is not None
                and self.user is not None):
            try:
                self.dbconn = MySQLdb.connect(host=self.host, user=self.user,
                                              passwd=self.passwd,
                                              db=self.dbname)
            except:
                raise DaoConnectionException(MySQLdb.Error)
        else:
            raise DaoConnectionException(
                "Missing config required to connect to db")

    def disconnect(self):
        """Disconnects from mysql/mariadb database

        """
        if self.dbconn is not None:
            self.dbconn.close()

    def single_row_select(self, query, query_param):
        """Query and return 0 to 1 database records - typically used
        when only one record is expected.

        Parameters
        ----------
        query : str
            SQL query string
        query_param : tuple
            SQL query parameters

        Returns
        -------
        dict
            database record with fields as dictionary elements
        """
        self.connect()

        cursor = self.query(query, query_param)
        record = cursor.fetchone()

        self.disconnect()

        if not record:
            record = {}
        return self.clean(record)

    def multi_row_select(self, query, query_param):
        """Query and return O to N records - typically used
        when more than one record is expected.

        Parameters
        ----------
        query : str
            SQL query string
        query_param : tuple
            SQL query parameters

        Returns
        -------
        list of dict
            database records stored as dictionaries within list
        """
        self.connect()

        cursor = self.query(query, query_param)
        records = cursor.fetchall()

        self.disconnect()

        clean = []
        for record in records:
            clean.append(self.clean(record))
        return clean

    def query(self, query, query_param):
        """Perform non-transactional query

        Parameters
        ----------
        query : str
            SQL query string
        query_param : tuple
            SQL query parameters

        Returns
        -------
        obj or None
            retrieved database records
        """
        cursor = self.dbconn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(query, query_param)
        return cursor

    def insert(self, table, data):
        """Insert a record into a database table using a transactional query

        Parameters
        ----------
        table : str
            name of target database table
        data : dict
            field values for database record

        Returns
        -------
        int
            number of records inserted
        int
            record id (primary key) for last record inserted
        """
        if table is None:
            raise DaoInvalidInputException("no table defined for insert")

        if data is None:
            raise DaoInvalidInputException(
                "no data provided for insert to table {}".format(table))

        columns = ""
        placeholders = ""
        param = ()
        for key, value in data.iteritems():
            columns += "`{}`, ".format(key)
            placeholders += "%s, "
            param = param + (value,)

        query = "INSERT into {} ( {} ) VALUES ( {} )".format(
            table, columns.rstrip(", "), placeholders.rstrip(", "))

        self.connect()

        rows, lastrowid = self._tquery(query, param)
        self.disconnect()
        return rows, lastrowid

    def update(self, table, data, query_param):
        """Update one or more records in a database table with
        a transactional query

        Parameters
        ----------
        table : str
            name of target database table
        data : dict
            field values to be changed
        query_param: dict
            parameters for WHERE clause in SQL update query

        Returns
        -------
        int
            number of records updated
        """
        if table is None:
            raise DaoInvalidInputException("no table defined for update")

        if data is None:
            raise DaoInvalidInputException(
                "no data provided for update to table {}".format(table))

        param = ()
        query = "UPDATE {} SET ".format(table)
        for field, value in data.items():
            query += "`{}`=%s, ".format(field)
            param = param + (value,)
        query = query.strip(", ")
        query += " WHERE 1=1 "

        for field, value in query_param.items():
            query += " AND `{}`=%s ".format(field)
            param = param + (value, )
        query = query.strip(", ")

        self.connect()
        rows, _ = self._tquery(query, param)
        self.disconnect()
        return rows

    def delete(self, table, query_param):
        """Delete one or more records in a database table with
        a transactional query

        Parameters
        ----------
        table : str
            name of target database table
        query_param: dict
            parameters for WHERE clause in SQL delete query

        Returns
        -------
        int
            number of records deleted
        """

        if table is None:
            raise DaoInvalidInputException("no table defined for delete")
        if query_param is None:
            raise DaoInvalidInputException(
                "no records identified for delete from table {}".format(table))

        query = "DELETE FROM {} WHERE 1=1 ".format(table)
        param = ()
        for field, value in query_param.items():
            query += " AND `{}`=%s ".format(field)
            param = param + (value, )

        self.connect()
        rows, _ = self._tquery(query, param)
        self.disconnect()
        return rows

    def clean(self, metadata):
        """Checks every element in a dict for non-unicode characters and
        cleans them if necessary

        Parameters
        ----------
        metadata : dict
            dictionary of elements that may require cleaning

        Returns
        -------
        dict
            cleaned dict
        """
        for attribute in metadata:
            if self._needs_cleaning(metadata[attribute]):
                metadata[attribute] = self.clean_string(metadata[attribute])
        return metadata

    @staticmethod
    def clean_string(to_clean):
        """Cleans unwanted characters from string

        Tidy up special characters and multiple blank lines from
        our long strings. We can have Windows line feeds (which we
        translate to Linux newlines), multiple blank lines that we
        want to squash down to just one blank line, HTML character
        entities and Unicode chars that pyesdoc cannot currently
        handle.

        Parameters
        ----------
        to_clean : str
            string to be cleaned

        Returns
        -------
        str
            cleaned string
        """
        clean = re.sub(r"(\r\n)", "\n", to_clean)   # Windows newlines
        clean = re.sub(r"(\n){3,}", "\n\n", clean)  # squash blank lines

        # Attempt to convert HTML character entities to characters.
        # This uses an undocumented function in HTMLParser, which
        # Stack Overflow says might not work for all possible entities.
        html_parser = HTMLParser.HTMLParser()
        clean = html_parser.unescape(clean)

        #  Until Mark G. and I have agreed what to do about Unicode
        #  characters like the degree symbol, I have to strip out
        #  anything too big for ASCII so that I can pass strings into
        #  pyesdoc [Emma Hibling].
        clean = "".join(i for i in clean if ord(i) < 127)
        return str(clean)

    @staticmethod
    def _needs_cleaning(record):
        """Checks if argument is of type string or unicode

        Parameters
        ----------
        record : any
            item to be checked

        Returns
        -------
        bool
            true if item is string or unicode
        """
        return isinstance(record, str) or isinstance(record, unicode)

    def _tquery(self, query, query_param):
        """Performs transactional query with rollback on failure

        Parameters
        ----------
        query : str
            SQL query string
        query_param : tuple
            SQL query parameters

        Returns
        -------
        int
            number of records affected
        int
            record id for last record inserted (if insert - otherwise 0)
        """
        cursor = self.dbconn.cursor(MySQLdb.cursors.DictCursor)

        rows_affected = 0
        last_rowid = 0
        try:
            cursor.execute(query, query_param)
            rows_affected = cursor.rowcount
            last_rowid = cursor.lastrowid
            self.dbconn.commit()

        except MySQLdb.Error:
            # Rollback in case there is any error
            if self.dbconn:
                self.dbconn.rollback()

        return rows_affected, last_rowid


def retrieve_credentials():
    """
    Retrieve the username and password for cremdb from the `cremdb`
    section of `$HOME/.cdds_credentials`.

    Returns
    -------
    : tuple of strings
        username, password.

    Raises
    ------
    RuntimeError
        If the credentials file or `cremdb` section cannot be
        found, or if the unix permissions are not appropriate (must
        not be readable by group or all).
    """
    credentials_file = os.path.join(os.environ['HOME'],
                                    '.cdds_credentials')
    if not os.path.exists(credentials_file):
        raise RuntimeError('Could not find credentials file at "{}"'
                           ''.format(credentials_file))
    unix_permissions = oct(os.stat(credentials_file).st_mode)[-3:]
    if unix_permissions[1:] != '00':
        raise RuntimeError('Credentials file "{}" must only be readable by '
                           'owner'.format(credentials_file))
    config = ConfigParser()
    config.read([credentials_file])
    if 'cremdb' not in config.sections():
        raise RuntimeError('Could not find section "cremdb" in credentials '
                           'file "{}"'.format(credentials_file))

    return (config.get('cremdb', 'username'),
            config.get('cremdb', 'password'))
