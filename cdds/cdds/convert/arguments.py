# (C) British Crown Copyright 2021-2024, Met Office.
# Please see LICENSE.rst for license details.
from argparse import Namespace

from cdds.common.cdds_files.cdds_directories import (
    ancil_files, replacement_coordinates_file, hybrid_heights_files, requested_variables_file, component_directory
)
from cdds.common.request.request import Request


def add_user_config_data_files(arguments: Namespace, request: Request) -> Namespace:
    """
    Add all additional data files for producing |user configuration files| during cdds convert to the arguments.
    Following data files will be updated:
    - the paths of the ancil files
    - the replacement coordinates file
    - the hybrid heights files

    :param arguments:
    :type arguments:
    :param request:
    :type request:
    :return:
    :rtype:
    """
    output_cfg_dir = component_directory(request, 'configure')

    setattr(arguments, 'ancil_files', ancil_files(request))
    setattr(arguments, 'replacement_coordinates_file', replacement_coordinates_file(request))
    setattr(arguments, 'hybrid_heights_files', hybrid_heights_files(request))
    setattr(arguments, 'requested_variables_list_file', requested_variables_file(request))
    setattr(arguments, 'output_cfg_dir', output_cfg_dir)
    return arguments
