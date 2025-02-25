# (C) British Crown Copyright 2025, Met Office.
# Please see LICENSE.md for license details.
"""
The :mod:`hadrem_cp4a_plugin` module contains the code for the HadREM-CP4A plugin.
"""
import os

from typing import Dict, Any

import iris.cube

from mip_convert.plugins.base.base_plugin import BaseMappingPlugin
from mip_convert.plugins.hadrem_cp4a.data.processors import *


class HadREM_CP4AMappingPlugin(BaseMappingPlugin):
    """
    Plugin for HadREM-CP4A models
    """

    def __init__(self):
        data_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')
        super(HadREM_CP4AMappingPlugin, self).__init__('HadREM-CP4A', data_dir)

        self.input_variables: Dict[str, iris.cube.Cube] = {}

    def evaluate_expression(self, expression: Any, input_variables: Dict[str, iris.cube.Cube]) -> iris.cube.Cube:
        """
        Update the iris Cube containing in the input variables list by evaluating the given expression.

        :param expression: Expression to be evaluated
        :type expression: Any
        :param input_variables: The input variables required to produce the
            MIP requested variable in the form {input_variable_name: cube}.
        :type input_variables: Dict[str, Cube]
        :return: The updated iris Cube
        :rtype: Cube
        """
        # TODO: Remove assign to class variable after refactoring mipconvert.mipconvert.new_variable line 793
        self.input_variables = input_variables
        return eval(expression)
