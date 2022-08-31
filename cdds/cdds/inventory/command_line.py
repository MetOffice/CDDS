# (C) British Crown Copyright 2020-2022, Met Office.
# Please see LICENSE.rst for license details.
"""
Populate the dataset inventory.
"""
import argparse
import gzip
import logging
import os
import shutil

from cdds.inventory.db_models import (get_row_id_by_column_value, execute_insert_query, populate_dataset_dictionary,
                                      setup_db)
from cdds.inventory.dao import DBVariableStatus
from hadsdk.mass import mass_list_dir, mass_list_files_recursively

from hadsdk import __version__
from hadsdk.arguments import read_default_arguments
from hadsdk.common import configure_logger, common_command_line_args, get_log_datestamp, mass_output_args
from hadsdk.constants import INVENTORY_DB_FILENAME, INVENTORY_FACET_LIST


JASMIN_STATUS_MAP = {
    'completed': DBVariableStatus.AVAILABLE,
    'in progress': DBVariableStatus.IN_PROGRESS,
    'failed': DBVariableStatus.IN_PROGRESS,
    'inconsistent state': DBVariableStatus.IN_PROGRESS,
}


def main_populate_inventory(arguments=None):
    """
    Populate the dataset inventory.
    """
    args = parse_args(arguments)
    configure_logger(args.log_name, args.log_level, args.append_log)
    logger = logging.getLogger(__name__)
    logger.info('Using hadSDK version {}'.format(__version__))

    datestamp = get_log_datestamp()
    inventory_filename = '{}_{}'.format(INVENTORY_DB_FILENAME, datestamp)
    new_inventory_path = os.path.join(args.root_inventory_dir, inventory_filename + '.db')
    old_inventory_path = os.path.join(args.root_inventory_dir, INVENTORY_DB_FILENAME + '.db')
    db_connection = setup_db(new_inventory_path)

    try:
        if args.crepp_filepath:
            logger.info('Creating inventory file {} from CREPP at {}'.format(new_inventory_path, args.crepp_filepath))
            populate_inventory_from_file(db_connection, args.crepp_filepath)
        else:
            mass_path = os.path.join(args.output_mass_root, args.output_mass_suffix)
            logger.info('Creating inventory file {} from MASS location {}'.format(new_inventory_path, mass_path))
            populate_inventory_from_mass(db_connection, mass_path)
        archive_and_replace_file(new_inventory_path, old_inventory_path)
        exit_code = 0
    except BaseException as exc:
        logger.exception(exc)
        exit_code = 1
    return exit_code


def parse_args(arguments):
    """
    Return the names of the command_line arguments for
    ``populate_inventory`` and their validated values.

    If this function is called from the Python interpreter with
    ``arguments`` that contains any of the ``--version``, ``-h`` or
    ``--help`` options, the Python interpreter will be terminated.

    Parameters
    ----------
    args: list of strings
        The command line arguments to be parsed.

    Returns
    -------
    : :class:`hadsdk.arguments.Arguments`
        The names of the command line arguments and their validated
        values.
    """
    user_arguments = arguments
    arguments = read_default_arguments('hadsdk', 'populate_inventory')
    parser = argparse.ArgumentParser(
        description=__doc__.replace('|', ''),
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        '-i', '--root_inventory_dir', type=str, default=arguments.root_inventory_dir,
        help=('The name of the directory that will contain the constructed inventory.'))
    parser.add_argument(
        '-j', '--crepp_filepath', type=str, default=None,
        help=('Location of CREPP inventory'))

    mass_output_args(parser, arguments.output_mass_suffix, arguments.output_mass_root)
    # Add arguments common to all scripts.
    common_command_line_args(parser, arguments.log_name, arguments.log_level,
                             __version__)
    args = parser.parse_args(user_arguments)
    arguments.add_user_args(args)
    return arguments


def parse_line(line):
    """
    Parse a line containing a CREPP dataset

    Parameters
    ----------
    line : str
        Line containing dataset_id and status

    Returns
    -------
        : tuple(str, str)
        Dataset id and status
    """
    line_elems = line.split()
    dataset_id = line_elems[0]
    status = line_elems[1] if len(line_elems) == 2 else ' '.join(line_elems[1:])
    return dataset_id, JASMIN_STATUS_MAP[status].value


def populate_inventory_from_file(db_connection, crepp_filepath):
    """
    Opens and parses the contents of CREPP dataset dump, and populates inventory's dataset table.

    Parameters
    ----------
    db_conn : sqlite3.Connection
        Database connection instance
    crepp_filepath : str
        Location of CREPP dataset dump
    """
    cursor = db_connection.cursor()
    with open(crepp_filepath) as fp:
        for line in fp:
            try:
                dataset_id, status = parse_line(line)
                dataset_facets = dataset_id.split('.')
                facet_dict = build_facet_dictionary(dataset_facets, INVENTORY_FACET_LIST)
                dataset_dict = populate_dataset_dictionary(cursor, facet_dict)
                dataset_dict['variant'] = dataset_facets[5]
                dataset_dict['status_id'] = get_row_id_by_column_value(cursor, 'status', status)
                dataset_dict['timestamp'] = dataset_facets[9]
                dataset_dict['dataset_id'] = dataset_id
                execute_insert_query(cursor, 'dataset', dataset_dict)
            except ValueError:
                pass
        db_connection.commit()
        return


def walk_mass_dir(root, facet_list, inventory):
    """
    Explores recursively MASS location given as root, matching
    directories at the current level with the first element from
    the facet_list. Once it gets down to the final 4 facets, it builds
    a list of datasets contained in the (current) root directory and
    adds them to the database.

    Parameters
    ----------
    root: str
        MASS root location
    facet_list: list
        A list of facets which should correspond to the directory hierarchy
        under root
    inventory: sqlite3.Connection
        Database connection instance
    """
    cursor = inventory.cursor()
    logger = logging.getLogger(__name__)
    if len(facet_list) == 4:
        # we're down to variable/grid/status/timestamp/
        datasets = mass_list_files_recursively(root, False)
        for dataset_id, dataset_metadata in datasets.items():
            dataset_facets = dataset_id.split('.')
            facet_dict = build_facet_dictionary(dataset_facets, INVENTORY_FACET_LIST)
            dataset_dict = populate_dataset_dictionary(cursor, facet_dict)
            dataset_dict['variant'] = dataset_facets[5]
            dataset_dict['status_id'] = get_row_id_by_column_value(cursor, 'status', dataset_metadata['status'])
            dataset_dict['timestamp'] = dataset_metadata['timestamp']
            dataset_dict['dataset_id'] = dataset_id
            execute_insert_query(cursor, 'dataset', dataset_dict)
            row_id = cursor.lastrowid
            for file_metadata in dataset_metadata['files']:
                file_metadata['dataset_id'] = row_id
                execute_insert_query(cursor, 'netcdf_file', file_metadata)
        inventory.commit()
        return
    else:
        directories = mass_list_dir(root, False)
        for elem in directories:
            if facet_list[0] == 'mip':
                logger.info('Processing data for {}'.format(os.path.basename(elem)))
            walk_mass_dir(elem, facet_list[1:], inventory)
    return


def build_facet_dictionary(dataset_facets, facet_list):
    """
    Builds a dictionary with facet values from dataset_id

    Parameters
    ----------
    dataset_facets: list
        List of facet values from the dataset_id
    facet_list: list
        List of facets

    Returns
    -------
    : dict
        Dictionary of facets and their values
    """
    # these facets correspond to simple strings in the database, so there is no need to find their primary keys
    excluded_facets = ['variant', 'status', 'timestamp']
    return {facet: dataset_facets[index] for index, facet in enumerate(facet_list) if facet not in excluded_facets}


def populate_inventory_from_mass(db_conn, mass_dir):
    """
    Build inventory for the provided MASS location

    Parameters
    ----------
    db_conn : sqlite3.Connection
        Database connection instance
    mass_dir : str
        MASS location of the archive to be inventorised
    """
    walk_mass_dir(mass_dir, INVENTORY_FACET_LIST, db_conn)


def archive_and_replace_file(new_inventory_path, old_inventory_path):
    """
    Gzip newly created archive and rename the file (possibly overwriting the previous version).

    Parameters
    ----------
    new_inventory_path : str
        Path to the new sqlite database file containing the inventory
    old_inventory_path : str
        Path to the file to be overwritten.
    """
    with open(new_inventory_path, 'rb') as f_in:
        with gzip.open(new_inventory_path + '.gz', 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
            shutil.move(new_inventory_path, old_inventory_path)
