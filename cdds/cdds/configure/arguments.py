# (C) British Crown Copyright 2019-2021, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`arguments` module contains the code required to handle
arguments, i.e. values that can be changed by the user, e.g. via the
command line for CDDS Configure.
"""
import os

from cdds.common.plugins.grid import GridType
from cdds.common.plugins.plugins import PluginStore

from hadsdk.arguments import read_argument_files, retrieve_script_arguments, Arguments


def read_configure_arguments(script_name):
    """
    Return the default arguments for the command line script
    ``script_name`` in CDDS configure.

    Parameters
    ----------
    script_name: str
        The name of the command line script.

    Returns
    -------
    : :class:`cdds.configure.arguments.ConfigureArguments`
        The default arguments for CDDS Configure.
    """
    default_global_args, default_package_and_script_args = read_argument_files(
        'cdds.configure')
    default_package_args, default_script_args = retrieve_script_arguments(
        script_name, default_package_and_script_args)

    return ConfigureArguments(default_global_args, default_package_args,
                              default_script_args)


class ConfigureArguments(Arguments):
    """
    Store the arguments for a script in CDDS Configure.
    """
    def __init__(self, default_global_args, default_package_args,
                 default_script_args):
        super(ConfigureArguments, self).__init__(
            default_global_args, default_package_args, default_script_args)
        self.ancil_files = None

    def add_additional_information(self, request):
        """
        Adds additional necessary information according the given request.

        :param request: Request for the CDDS configure process
        :type request: `cdds.common.request.Request`
        """
        self.add_ancil_files(request.model_id)
        self.add_hybrid_heights_files(request.model_id)
        self.add_replacement_coordinates_file(request.model_id)

        self._add_attribute('institution_id', request.institution_id)
        self._add_attribute('license', request.license)

    def add_ancil_files(self, model_id):
        """
        Constructs the full paths to the ancillary files for a specific model
        and makes them available via the ``ancil_files`` and ``args`` attributes.

        :param model_id: ID of model
        :type model_id: str
        """
        parameter = 'ancil_files'
        root_dir = self.root_ancil_dir

        plugin = PluginStore.instance().get_plugin()
        models_parameters = plugin.models_parameters(model_id)
        ancil_files = models_parameters.all_ancil_files(root_dir)
        argument = ' '.join(ancil_files)
        self._add_attribute(parameter, argument)

    def add_replacement_coordinates_file(self, model_id):
        """
        Constructs the full paths to the replacement coordinates file for a specific
        model and makes them available via the ``replacement_coordinates_file`` and
        ``args`` attributes.

        :param model_id: ID of model
        :type model_id: str
        """
        parameter = 'replacement_coordinates_file'

        plugin = PluginStore.instance().get_plugin()
        grid_info = plugin.grid_info(model_id, GridType.OCEAN)
        filename = grid_info.replacement_coordinates_file
        argument = os.path.join(self.root_replacement_coordinates_dir, filename)
        self._add_attribute(parameter, argument)

    def add_hybrid_heights_files(self, model_id):
        """
        Constructs the full paths to the hybrid heights files of a specific
        model and overwrites the hybrid_heights_files attribute.

        :param model_id: ID of model
        :type model_id: str
        """
        root_dir = self.root_hybrid_heights_dir

        plugin = PluginStore.instance().get_plugin()
        models_parameters = plugin.models_parameters(model_id)
        hybrid_heights_files = models_parameters.all_hybrid_heights_files(root_dir)
        argument = ' '.join(hybrid_heights_files)
        self._add_attribute('hybrid_heights_files', argument)
