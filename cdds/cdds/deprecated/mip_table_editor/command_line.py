# (C) British Crown Copyright 2022-2025, Met Office.
# Please see LICENSE.md for license details.

import argparse
import logging

from cdds import __version__
from cdds.common import configure_logger, common_command_line_args
from cdds.deprecated.mip_table_editor.mip_tables import ControlledVocabulary, MipTableVariable, MipTable


def main_table_editor(arguments=None):
    """Main routine for the mip_table_editor"""

    arguments = parse_args(arguments)

    # Create the configured logger.
    configure_logger(arguments.log_name, arguments.log_level, arguments.append_log)
    # Retrieve the logger.
    logger = logging.getLogger(__name__)
    # Log version.
    logger.info('Using CDDS version {}'.format(__version__))

    try:
        if arguments.domain:
            CV_object = ControlledVocabulary(arguments)
        elif arguments.variable:
            Mip_object = MipTableVariable(arguments)
        else:
            Mip_object = MipTable(arguments)
        return 0
    except BaseException as err:
        logger.exception(err)
        return 1


EPILOG_TEXT = '''Example usage of the mip_table_editor tool.

Replace `/path/to/tables` with a path to the Mip Tables.

-------------------------------------------------------------------------------
Working with the Controlled Vocabulary

Add a new experiment ID
mip_table_editor /path/to/tables add -d experiment_id -n hist-bgc-ext

Clone an existing source ID
mip_table_editor /path/to/tables clone -d source_id -n INM-CM5-H

Modify an existing institution id
mip_table_editor /path/to/tables modify -d institution_id -n MOHC

Remove an existing source_id
mip_table_editor /path/to/tables remove -d source_id -n INM-CM5-H-New

View an experiment_id
mip_table_editor /path/to/tables view -d experiment_id -n hist-bgc

-------------------------------------------------------------------------------
Working with Mip Table Variables

Add a new variable 'foo' to the Emon Mip Table
mip_table_editor /path/to/tables add -T Emon -V foo

Clone the existing variable 'tas' from the Amon Mip Table
mip_table_editor /path/to/tables clone -T Amon -V tas

Modify the existing variable 'aragos' from the Omon Mip Table
mip_table_editor /path/to/tables modify -T Omon -V aragos

Remove the variable `ccb` from the CFday Mip Table
mip_table_editor /path/to/tables remove -T CFday -V ccb

View the variable `hus` from the 6hrLev Mip Table
mip_table_editor /path/to/tables view -T 6hrLev -V hus

-------------------------------------------------------------------------------
Working with Mip Tables

Add a new Mip Table called Foo
mip_table_editor /path/to/tables add -T Foo

Clone the existing Amon Mip Table
mip_table_editor /path/to/tables clone -T Amon -n foobar

Modify the Foo Mip Table
mip_table_editor /path/to/tables modify -T Foo

Remove the Mip Table foobar
mip_table_editor /path/to/tables remove -T foobar

View the Amon Mip Table
mip_table_editor /path/to/tables view -T Amon


'''


def parse_args(arguments):
    """Function for parsing the commandline arguments.

    Parameters
    ----------
    arguments: list | None

    Returns
    -------
    args: argparse.Namespace

    """
    parser = argparse.ArgumentParser(prog='A command line tool for modifying Mip Tables and the Controlled Vocabulary.',
                                     epilog=EPILOG_TEXT,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('path',
                        help='Path to the mip_tables that need editing.')
    parser.add_argument('action',
                        help='Type of action to apply.',
                        action='store',
                        choices=['add', 'clone', 'modify', 'remove', 'view'])
    parser.add_argument('-d', '--domain',
                        help='The domain within the CV to apply an action to.',
                        default=None,
                        choices=['source_id', 'experiment_id', 'institution_id'])
    parser.add_argument('-n', '--name',
                        help='The name an existing field, or when used with the "add" action, the name of a new field.',
                        default=None)
    parser.add_argument('-T', '--table',
                        help='Specify a Mip table.',
                        action='store')
    parser.add_argument('-V', '--variable',
                        help='Specify a Variable.',
                        default=None)
    parser.add_argument('-k', '--key',
                        help='View only the keys of a domain',
                        default=False,
                        action='store_true')
    parser.add_argument('-e', '--editor',
                        help='Specify an editor to use instead of $EDITOR.',
                        default=None,
                        metavar='')
    common_command_line_args(parser, 'mip_table_editor', logging.INFO, __version__)
    parsed_arguments = parser.parse_args(arguments)
    return parsed_arguments
