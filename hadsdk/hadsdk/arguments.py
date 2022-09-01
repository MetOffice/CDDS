# (C) British Crown Copyright 2019-2022, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`arguments` module contains the code required to handle
arguments, i.e. values that can be changed by the user, e.g. via the
command line.
"""
import importlib
import logging
import os

from cdds.common.constants import ARGUMENTS_FILENAME, PACKAGE_KEY_FOR_ARGUMENTS
from cdds.common.io import read_json
from cdds.common.platforms import System

import hadsdk


def read_default_arguments(package_name, script_name, return_class=None):
    """
    Return the default arguments for the command line script
    ``script_name`` in the CDDS package ``package_name``.

    Parameters
    ----------
    package_name: str
        The name of the CDDS package.
    script_name: str
        The name of the command line script.
    return_class: function (optional)
        The desired returned class if this one is NONE then use `hadsdk.arguments.Arguments`

    Returns
    -------
    : :class: extends from `hadsdk.arguments.Arguments`
        The default arguments.
    """
    default_global_args, default_package_and_script_args = read_argument_files(
        package_name)
    default_package_args, default_script_args = retrieve_script_arguments(
        script_name, default_package_and_script_args)

    if return_class is None:
        return Arguments(default_global_args, default_package_args, default_script_args)

    return return_class(default_global_args, default_package_args, default_script_args)


def read_argument_files(package_name):
    """
    Return the default arguments for the CDDS package ``package_name``.

    Parameters
    ----------
    package_name: str
        The name of the CDDS package.

    Returns
    -------
    : dict, dict
        The default global, and package and script arguments, respectively.
    """
    # Retrieve the logger.
    logger = logging.getLogger(__name__)

    system = System()
    default_global_args_file = system.default_global_args_file()
    default_package_args_file = system.default_package_args_file(package_name)

    # Read the default global arguments.
    logger.debug('Reading the default global arguments from "{}"'.format(default_global_args_file))
    default_global_args = read_json(default_global_args_file)

    # Deal with special cases. This may need to be done in a better way.
    log_level = default_global_args['log_level']
    default_global_args['log_level'] = eval(log_level)

    # Read the default package-specific arguments.
    logger.debug('Reading the default package arguments from "{}"'.format(default_package_args_file))
    default_package_and_script_args = read_json(default_package_args_file)

    return default_global_args, default_package_and_script_args


def retrieve_script_arguments(script_name, default_package_and_script_args):
    """
    Return the default arguments for the command line script
    ``script_name``.

    Parameters
    ----------
    script_name: str
        The name of the command line script.
    default_package_and_script_args: dict
        The default package-specific and script arguments for all the
        command line scripts.

    Returns
    -------
    : dict, dict
        The default package and script arguments, respectively.
    """
    default_package_args = {}
    default_script_args = {}
    if PACKAGE_KEY_FOR_ARGUMENTS in default_package_and_script_args:
        default_package_args = default_package_and_script_args[
            PACKAGE_KEY_FOR_ARGUMENTS]
    if script_name in default_package_and_script_args:
        default_script_args = default_package_and_script_args[script_name]

    return default_package_args, default_script_args


class Arguments(object):
    """
    Store the arguments for a script in a CDDS package.
    """
    def __init__(self, default_global_args, default_package_args,
                 default_script_args):
        """
        Parameters
        ----------
        default_global_args: dict
            The default global arguments.
        default_package_args: dict
            The default package-specific arguments.
        default_script_args: dict
            The default script-specific arguments.
        """
        self._default_global_args = default_global_args
        self._default_package_args = default_package_args
        self._default_script_args = default_script_args
        self._resolved_args = {}
        self._resolve_arguments()
        self._parameters = ['mip_table_dir']
        self._add_attributes()

    @property
    def args(self):
        _args = {}
        for parameter in self._parameters:
            argument = getattr(self, parameter)
            if parameter == 'mip_table_dir':
                if argument is not None:
                    _args[parameter] = argument
            else:
                _args[parameter] = argument
        return _args

    def _resolve_arguments(self):
        # Update self._resolved_args in the following order:
        self._add_global_args()
        self._add_package_args()
        self._add_script_args()

    def _add_global_args(self):
        self._resolved_args.update(self._default_global_args)

    def _add_package_args(self):
        self._resolved_args.update(self._default_package_args)

    def _add_script_args(self):
        self._resolved_args.update(self._default_script_args)

    def _add_attributes(self):
        for parameter, argument in self._resolved_args.items():
            self._add_attribute(parameter, argument)

    def _add_attribute(self, parameter, argument):
        self._parameters.append(parameter)
        setattr(self, parameter, argument)

    def add_user_args(self, user_args):
        """
        Add the arguments from the user.

        Parameters
        ----------
        user_args: :class:`argparse.Namespace` object
            The names of the command line arguments and their validated
            values.
        """
        for parameter, argument in vars(user_args).items():
            self._add_attribute(parameter, argument)

    def add_or_update(self, new_arguments):
        """
        Add or update the given arguments.

        Parameters
        ----------
        new_arguments: dict
            The names of the command line arguments and their validated values.
        """
        for parameter, argument in new_arguments.items():
            if hasattr(self, parameter):
                setattr(self, parameter, argument)
            else:
                self._add_attribute(parameter, argument)

    @property
    def mip_table_dir(self):
        try:
            argument = os.path.join(
                self.root_mip_table_dir, self.data_request_version)
        except (TypeError, AttributeError):
            argument = None
        return argument
