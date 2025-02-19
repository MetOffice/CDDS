# (C) British Crown Copyright 2025, Met Office.
# Please see LICENSE.md for license details.
"""
The :mod:`hadrem3_plugin` module contains the code for the HadGEM3 plugin.
"""
import iris.cube
import os

from typing import Dict, Any

from mip_convert.plugins.base.base_plugin import BaseMappingPlugin
from mip_convert.plugins.hadrem3.data.processors import *


class HadREM3MappingPlugin(BaseMappingPlugin):
    """
    Plugin for HadREM3 models
    """

    def __init__(self):
        data_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')
        super(HadREM3MappingPlugin, self).__init__('HadREM3', data_dir)

        self.input_variables: Dict[str, iris.cube.Cube] = {}

    def evaluate_expression(self, expression: Any, input_variables: Dict[str, iris.cube.Cube]) -> iris.cube.Cube:
        """
        Update the iris Cube containing in the input variables list by evaluating the given expression.

        :param expression: Expression that should be evaluated
        :type expression: Any
        :param input_variables:
        :type input_variables: Dict[str, Cube]
        :return: The updated iris Cube
        :rtype: Cube
        """
        # TODO: Remove assign to class variable after refactoring mipconvert.mipconvert.new_variable line 793
        self.input_variables = input_variables
        return eval(expression)
