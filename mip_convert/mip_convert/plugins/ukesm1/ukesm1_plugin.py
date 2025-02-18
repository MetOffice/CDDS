# (C) British Crown Copyright 2025, Met Office.
# Please see LICENSE.md for license details.
import iris.cube
import os

from typing import Dict, Any

from mip_convert.plugins.base.base_plugin import BaseMappingPlugin


class UKESM1MappingPlugin(BaseMappingPlugin):

    def __init__(self):
        data_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')
        super(UKESM1MappingPlugin, self).__init__('eUKESM1', data_dir)

        self.input_variables: Dict[str, iris.cube.Cube] = {}

    def evaluate_expression(self, expression: Any, input_variables: Dict[str, iris.cube.Cube]) -> iris.cube.Cube:
        """
        Update the iris Cube containing in the input variables list by evaluating the given expression.

        :param expression:
        :type expression: Any
        :param input_variables:
        :type input_variables: Dict[str, Cube]
        :return: The updated iris Cube
        :rtype: Cube
        """
        # TODO: Remove assign to class variable after refactoring mipconvert.mipconvert.new_variable line 793
        self.input_variables = input_variables
        return eval(expression)
