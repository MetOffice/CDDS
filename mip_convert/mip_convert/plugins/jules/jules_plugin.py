# (C) British Crown Copyright 2026, Met Office.
# Please see LICENSE.md for license details.
"""The :mod:`jules_plugin` module contains the code for the JULES plugin."""
import iris.cube
import os

from typing import Dict, Any

from mip_convert.plugins.base.base_plugin import BaseMappingPlugin
from mip_convert.plugins.base.data.processors import *


class JULESMappingPlugin(BaseMappingPlugin):
    """Plugin for JULES land surface model output"""

    def __init__(self):
        data_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')
        super(JULESMappingPlugin, self).__init__('JULES', data_dir)

        self.input_variables: Dict[str, iris.cube.Cube] = {}

    def evaluate_expression(self, expression: Any, input_variables: Dict[str, iris.cube.Cube]) -> iris.cube.Cube:
        """Update the iris Cube containing in the input variables list by evaluating the given expression.

        Parameters
        ----------
        expression : Any
            Expression to be evaluated
        input_variables : Dict[str, Cube]
            The input variables required to produce the MIP requested variable in the form {input_variable_name: cube}.

        Returns
        -------
        Cube
            The updated iris Cube
        """
        # TODO: Remove assign to class variable after refactoring mipconvert.mipconvert.new_variable line 793
        self.input_variables = input_variables
        return eval(expression)
