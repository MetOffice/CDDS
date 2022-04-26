# (C) British Crown Copyright 2019-2021, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`mass_record` module contains record object of the MASS archiving system
and functions on this record.
"""


def filter_records_by_paths(record_map, search_paths):
    """
    Filters the records of the given record map and returns a map that only
    contains the records that paths contain at least one path of the given
    search paths.

    Parameters
    ----------
    record_map: dict
        Map of Mass records that should be filtered.

    search_paths: list
        List of paths that are looked for.

    Returns
    -------
    : dict
        Filtered map of records where the path contains at least one path of
        the given search paths.
    """
    result = {}
    for search_path in search_paths:
        matches = {k: v for (k, v) in record_map.items() if v.path_contains(search_path)}
        result.update(matches)
    return result


def get_records_from_stdout(stdout, searched_paths=None):
    """
    Returns a map of Mass records for the paths specified in the stdout. A Mass record
    contains the record path, the parent record path, a flag if empty and a flag if
    it is a directory. If the `searched_paths` argument is set, only Mass records that
    paths are contained (completely or partly) in the given searched paths will be returned.

    Parameters
    ----------
    stdout: str
        Output string of a mass ls -lR command.

    searched_paths: list
        List of paths that are looked for. For all paths a record will be returned.

    Returns
    -------
    : dict
        Map of records where keys are the record paths and values the corresponding MassRecord.
    """
    stdout_lines = [line for line in stdout.split('\n') if line]
    record_map = {}
    for line in stdout_lines:
        entries = [entry for entry in line.split()]
        path_index = len(entries) - 1
        record = MassRecord(entries[path_index], entries[0])
        record_map[record.path] = record

    set_is_empty_flag(record_map)
    if searched_paths:
        record_map = filter_records_by_paths(record_map, searched_paths)
    return record_map


def set_is_empty_flag(record_map):
    """
    Finds all empty records in the given record map and sets the empty flag for each record
    correctly. It assumes that files, collections or data sets are not empty by default.

    Parameters
    ----------
    record_map: dict
        Map of records where keys are the record paths and values the corresponding MassRecord.

    Returns
    -------
    : dict
        Map of records where keys are the record paths and values the corresponding MassRecord
        with correct set empty flag.
    """
    # do a bottom first lookup
    paths = list(record_map.keys())
    paths.sort(key=len, reverse=True)

    for path in paths:
        record = record_map[path]
        if record.is_dir and record.not_empty:
            parent = record.parent
            if parent in record_map:
                parent_data = record_map[parent]
                parent_data.set_empty(False)
        elif record.is_not_dir:
            # by default: files, collections and data sets are not empty
            record.set_empty(False)
            parent = record.parent
            if parent in record_map:
                parent_data = record_map[parent]
                parent_data.set_empty(False)

    return record_map


class MassRecord:
    """
    A MassRecord object represents a record (directory, file, data set, collection) in
    Mass storing the record path, its parent path, a flag if dir and a flag if empty
    """

    def __init__(self, path, media_type):
        self._path = path
        self._parent = self._path.rsplit('/', 1)[0]
        self._is_dir = media_type == 'D'
        self._empty = True

    @property
    def path(self):
        """
        Returns the record path in Mass.

        Returns
        -------
        : str
            Absolute path of the record.
        """
        return self._path

    @property
    def parent(self):
        """
        Returns path of the parent of the record in Mass.

        Returns
        -------
        : str
            Absolute path of parent of the record.
        """
        return self._parent

    @property
    def is_empty(self):
        """
        Returns if record is empty.

        Returns
        -------
        : bool
            True if record is empty.
        """
        return self._empty

    @property
    def not_empty(self):
        """
        Returns if record is not empty

        Returns
        -------
        : bool
            True if record is not empty.
        """
        return not self._empty

    def set_empty(self, empty):
        """
        Sets the empty flag of the record to the given value.

        Parameters
        ----------
        empty: bool
            True if record is empty, otherwise False.
        """
        self._empty = empty

    @property
    def is_dir(self):
        """
        Returns if the record is a directory.

        Returns
        -------
        : bool
            True if record is a directory.
        """
        return self._is_dir

    @property
    def is_not_dir(self):
        """
        Returns if the record is not a directory.

        Returns
        -------
        : bool
            True if record is not a directory.
        """
        return not self._is_dir

    def path_contains(self, search_path):
        return search_path in self._path
