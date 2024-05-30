# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.

from cdds.common.constants import INVENTORY_HEADINGS, INVENTORY_HEADINGS_FORMAT
from cdds.inventory.dao import DBVariable
from cdds.inventory.db_models import build_sql_query, connect, execute_query
from cdds.common.mass import mass_list_dir


def perform_user_query(facets, arguments):
    """
    Creates an SQL query from a facets dictionary which is then used to query
    the inventory.db. Any output of this query is then printed.

    Parameters
    ----------
    facets : dictionary
        The facets used to build a query.
    arguments : argparse.Namespace
        Contains the user arguments and default arguments.
    """

    db_connection = connect(arguments.inventory_path)
    sql = build_sql_query(facets)
    rows = execute_query(db_connection.cursor(), sql, facets).fetchall()

    print_query(rows, arguments)


def print_query(rows, arguments):
    """
    Performs the printing of the results from a query to the terminal. Will
    print the locations in MASS if the appropriate flags are set.

    Parameters
    ----------
    rows : list
        A list of sqlite3.Row objects
    arguments : argparse.Namespace
        Contains the user arguments and default arguments
    """

    print('')
    print(INVENTORY_HEADINGS_FORMAT.format(*INVENTORY_HEADINGS))

    for row in rows:
        db_variable_instance = DBVariable(row)
        fields = [db_variable_instance.mip_era,
                  db_variable_instance.mip,
                  db_variable_instance.institute,
                  db_variable_instance.model,
                  db_variable_instance.experiment,
                  db_variable_instance.variant,
                  db_variable_instance.mip_table,
                  db_variable_instance.name,
                  db_variable_instance.grid,
                  db_variable_instance.status,
                  db_variable_instance.version]

        # print a facet string as well for easy copy and pasting
        facet_string = ".".join(fields[:-2])
        printed_fields = fields + [facet_string]

        print(INVENTORY_HEADINGS_FORMAT.format(*printed_fields))

        if arguments.show_location and arguments.mass_suffix != "production/":
            get_mass_file_paths(fields, arguments)

    print('')
    print('A total of {} records were found.'.format(len(rows)))


def get_mass_file_paths(fields, arguments):
    """
    Finds the URI's for the given facet fields.

    Parameters
    ----------
    fields : list
        List of facets constructed from an sqlite3.Row object
    arguments : argparse.Namespace
        Contains the user arguments and default arguments
    """
    files_in_mass = []
    # Construct a path to check in MASS
    root_path = arguments.mass_suffix
    path = root_path + '/'.join(fields)
    files_in_mass = mass_list_dir(path, False)

    if not files_in_mass:
        raise RuntimeError('Exists in inventory but cannot be found in MASS.')

    if arguments.directories_only:
        print('{}'.format(path))
        print('')
    else:
        print('{}'.format(path))
        for file_path in files_in_mass:
            print('{}'.format(file_path))
        print('')
