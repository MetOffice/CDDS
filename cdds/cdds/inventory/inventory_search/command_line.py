# (C) British Crown Copyright 2020-2022, Met Office.
# Please see LICENSE.rst for license details.

import argparse
import os

from cdds.common.constants import INVENTORY_DB_FILENAME, INVENTORY_FACET_LIST
from cdds.inventory.inventory_search.search import perform_user_query


def main_user_search():
    """
    Contains the main function calls for performing a search of the inventory.db
    using a users search terms and then printing the output.
    """
    arguments = parse_args()

    search_pattern = check_user_input(arguments.facet_pattern)

    facets_dict = populate_facets_dict(search_pattern)

    perform_user_query(facets_dict, arguments)


def parse_args():
    """
    Function for parsing any command line arguments or flags fiven

    Returns
    -------
    args : argparse.Namespace
        Contains the user arguments and default arguments
    """
    parser = argparse.ArgumentParser('A commandline tool for querying the inventory.db database.')
    parser.add_argument('facet_pattern')
    parser.add_argument('-s', '--show_location',
                        help='Flag to show individual file locations in MASS',
                        action='store_true')
    parser.add_argument('-d', '--directories_only',
                        help='Show directories but hide individual files',
                        action='store_true')
    parser.add_argument('-i', '--inventory_path',
                        help='Specify a path to a different inventory database file',
                        metavar='')
    parser.add_argument('-l', '--mass_suffix',
                        help='Specify where the inventory should look in MASS. ',
                        metavar='')
    args = parser.parse_args()

    return args


def check_user_input(input_string):
    """
    Checks that the correct number of facets have been passed in by the user
    and that there are no empty fields. Should raise a RuntimeError if fields
    are missing or the wrong number of fields are given.

    Parameters
    ----------
    input_string : string
        The users input search string.
    Returns
    -------
    input_list: list
        The user input string split on the "." character.
    """

    input_list = input_string.split('.')

    if len(input_list) != 9:
        raise RuntimeError('Incorrect number of arguments. '
                           + '{} given 9 required.'.format(len(input_list)))

    if '' in input_list:
        empty_arguments = [str(i + 1)
                           for i in range(len(input_list))
                           if input_list[i] == '']
        raise RuntimeError('Empty argument given in position(s) '
                           + '{}'.format(' '.join(empty_arguments)))

    return input_list


def populate_facets_dict(values):
    """
    Takes in the specific facets the user would like to match and returns a
    facets dictionary that will be used as an argument to build an SQL query.

    Parameters
    ----------
    values : list
        A list of the facets to search for
    Returns
    -------
    facets : dict
        Key value pair dictionary of the facet type and the facet search term
    """

    facets = {k: v for k, v in zip(INVENTORY_FACET_LIST, values) if v != '*'}

    return facets
