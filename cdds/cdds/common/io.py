# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
import json
import os
import tempfile

from typing import Any, Dict, Tuple


def read_json(json_file: str) -> Dict[str, Any]:
    """
    Read the JSON file ``json_file``.

    Parameters
    ----------
    json_file: str
        The name of file to read.

    Returns
    -------
    : dict
        Data read from ``json_file``.
    """
    with open(json_file, 'r') as file_handle:
        data = json.load(file_handle)
    return data


def write_json(json_file: str, data: Dict[str, Any], indent: int = 2, sort_keys: bool = True,
               separators: Tuple[str, str] = (',', ':'), **kwargs: Any):
    """
    Write ``data`` to a JSON file with the name ``json_file``.

    Parameters
    ----------
    json_file: str
        The name of file to write to.
    data: dict
        Data to write to ``json_file``.
    indent: int, optional
        number of characters to indent
    sort_keys: bool, optional
        Sort keys in output file
    separators: tuple
        Specifies the separators in the json file between items and key-values. The default is ``(', ', ': ')``.
    **kwargs
        Other keyword arguments to pass to json.dump
    """
    with open(json_file, 'w') as file_handle:
        json.dump(data, file_handle, indent=indent, sort_keys=sort_keys, separators=separators, **kwargs)


def delete_file(file_path: str) -> None:
    """
    Delete file if exists.

    :param file_path: Path to the file that should be deleted
    :type file_path: str
    """
    if os.path.exists(file_path):
        os.remove(file_path)


def write_into_temp_file(data: Any) -> str:
    """
    Writes the data into a new created temporary file.

    :param data: Data that should be written
    :type data: Any
    :return: Path to the new temporary file where data is written to
    :rtype: str
    """
    id, path = tempfile.mkstemp()
    try:
        with open(path, 'w') as temp_file:
            temp_file.write(str(data))
    except IOError:
        raise IOError('Could not write into temp file: {}'.format(path))
    return path
