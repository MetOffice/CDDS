# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.

from collections import OrderedDict


def parseMipTable(mipfile):
    """
    Parse a MIP table, returning a composite dictionary of the form::

        {
          'atts': {k1: v1, k2: v2, ... },
          'expts': {'expt_id1': 'expt_name1',
                    'expt_id2': 'expt_name2', ... },
          'axes': {'axis1': {...}, 'axis2': {...}, ... },
          'vars': {'var1': {...}, 'var2': {...}, ... },
          'gmaps': {'gmap1': {...}, 'gmap2': {...}, ...}
        }

    The meaning of each subdictionary is as follows:

    * the 'atts' subdictionary stores top-level (global) attributes.
    * the 'expts' subdictionary stores (expt-id, expt-name) pairs.
      Note: order is opposite to that in MIP table.
    * the 'axes' subdictionary stores attributes for each axis_entry
      block.
    * the 'vars' subdictionary stores attributes for each
      variable_entry block.
    * the 'gmaps' subdictionary stores attributes for each
      mapping_entry block.

    The current function performs no error checking - it assumes the
    MIP table is in correct format! If that's likely to be a problem
    then wrap your code in a try/except block.

    This function also assumes that ALL axis and variable entry blocks
    appear after any expt ids and global attributes.

    All dictionary values are stored as strings. Conversion to other
    data types must be done by the calling program.

    :param mipfile: The pathname of the MIP table to parse.
    :type  mipfile: string

    :return: A composite dictionary as described above.
    :rtype:  dict
    """
    mipDict = {
        'atts': {},
        'expts': {},
        'axes': {},
        'vars': OrderedDict(),
        'gmaps': {}
    }

    blockOn = False
    blockDict = {}
    blockKeys = ('axis_entry', 'variable_entry', 'mapping_entry')
    blockType = ""
    blockID = ""

    fhandle = open(mipfile, 'r')
    for line in fhandle:
        line = line.strip()
        if not line or line[0] == '!':
            # skip blank lines and comment lines
            continue

        # Decode key and value from current line.
        key, _sep, value = line.partition(':')
        key = key.strip()
        value = _trimValue(value)

        # Start of new axis or variable block.
        if key in blockKeys:
            # Store current block if necessary.
            if blockOn:
                _addBlock(blockType, blockID, blockDict, mipDict)
            blockType, _sep, _entry = key.partition('_')
            blockID = value
            blockDict = {}
            blockOn = True

        # expt_id_ok entry - store as experiment id and name (opposite
        # order to MIP table)
        elif key == "expt_id_ok":
            bits = value.split("'")
            exptName = bits[1]
            exptID = bits[3]
            mipDict['expts'][exptID] = exptName

        # Add K-V pair to global, axis or variable dictionary.
        else:
            # Axis or variable attribute
            if blockOn:
                blockDict[key] = value
            # Global attribute
            else:
                mipDict['atts'][key] = value

    # End of file: store final block if necessary.
    if blockOn:
        _addBlock(blockType, blockID, blockDict, mipDict)

    # Return a dictionary containing all four subdictionaries.
    return mipDict


def _addBlock(blockType, blockID, blockDict, mipDict):
    """Add an axis, variable or grid mapping subdictionary."""
    if blockType == "axis":
        mipDict['axes'][blockID] = blockDict
    elif blockType == "variable":
        mipDict['vars'][blockID] = blockDict
    elif blockType == "mapping":
        mipDict['gmaps'][blockID] = blockDict


def _trimValue(value):
    """
    Trim superfluous characters and trailing comments from an attribute
    value.
    """
    if '!' in value:
        value = value.partition('!')[0]
    return value.strip()
