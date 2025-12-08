# (C) British Crown Copyright 2017-2025, Met Office.
# Please see LICENSE.md for license details.
"""Tools for interfacing with the cdds convert workflow."""
import json
from configparser import ConfigParser

from cdds.convert.exceptions import SuiteConfigMissingValueError


def update_suite_conf_file(filename, section_name, changes_to_apply, raw_value=False, delimiter="="):
    """Update the contents of a rose suite configuration file, on disk,
    based on supplied keywords.

    Parameters
    ----------
    filename : str
        Name of the file to update.
    section_name : str
        The section of the rose-suite.conf to apply changes to.
    changes_to_apply : dict
        A dictionary containing field_name:field_value pairs.
    raw_value : bool
        If False, format values using json.dumps.
    delimiter : str, optional
        Character used for delimiting keys and values in the suite
        configuration file.

    Other keywords are used to specify changes to be made

    Returns
    -------
    list
        Each element is a 3-tuple with elements for the name of the
        field that is changed, the original value, and the new value.
    """
    parser = ConfigParser(delimiters=[delimiter])
    parser.optionxform = str
    parser.read(filename)
    section = parser[section_name]
    changes = []
    for field, new_value in changes_to_apply.items():
        if not raw_value:
            new_value = json.dumps(new_value)
        if field not in section:
            raise SuiteConfigMissingValueError('Field "{}" not found in "{}".'
                                               ''.format(field, filename))
        if section[field] != new_value:
            try:
                changes.append((field, str(section[field]),
                                str(new_value)))
                section[field] = new_value
            except TypeError as error:
                msg = ('Failed attempting to set field "{}" to "{}": '
                       '').format(field, repr(new_value))
                raise TypeError(msg + str(error))

    parser.write(open(filename, 'w'))
    return changes
