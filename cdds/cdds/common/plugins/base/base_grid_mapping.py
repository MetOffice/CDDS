# (C) British Crown Copyright 2025, Met Office.
# Please see LICENSE.md for license details.
"""The :mod:`base_mapping` module contains the code required to provide the
grid mapping information for the requested MIP variables.
"""
import os

from cdds.common.plugins.grid_mapping import GridMapping
from typing import Tuple


DEFAULT_SECTION_IN_CFG = 'DEFAULT'


class BaseGridMapping(GridMapping):
    """Class to store the grids information stored in the corresponding configuration files"""

    def __init__(self):
        super(BaseGridMapping, self).__init__()

        data_folder = os.path.join(os.path.dirname(__file__), 'data', 'grid_mapping')
        default_grids_file = os.path.join(data_folder, 'default_grids.cfg')
        grids_file = os.path.join(data_folder, 'grids.cfg')

        if self.additional_default_grids_file:
            self.default_grids_config = self.read_configuration(
                [default_grids_file, self.additional_default_grids_file]
            )
        else:
            self.default_grids_config = self.read_configuration(default_grids_file)

        if self.additional_grids_file:
            self.grids_config = self.read_configuration([grids_file, self.additional_grids_file])
        else:
            self.grids_config = self.read_configuration(grids_file)

    def retrieve_mapping(self, variable_name: str, mip_table_id: str) -> Tuple[str, str]:
        """Return the grid mapping information (grid type and grid name) for the MIP requested variable.

        Parameters
        ----------
        variable_name : str
            The MIP request variable name
        mip_table_id : str
            The MIP table identifier

        Returns
        -------
        Tuple[str, str]
            The grid type and grid name
        """
        grid_type = None
        grid_name = None
        if self.grids_config.has_section(mip_table_id) and self.grids_config.has_option(mip_table_id, variable_name):
            grid_type, grid_name = self.grids_config.get(mip_table_id, variable_name).split(' ')
        elif self.default_grids_config.has_section(mip_table_id):
            grid_type, grid_name = self.default_grids_config.get(mip_table_id, 'default').split(' ')
        else:
            grid_type, grid_name = self.default_grids_config.get(DEFAULT_SECTION_IN_CFG, 'default').split(' ')
        return grid_type, grid_name

    @property
    def additional_default_grids_file(self) -> str:
        """Returns the path to an additional default grid configuration that overrides the values
        in the basic default grid information.

        This method should be overridden of a child class if additional default grid information are
        needed.

        Returns
        -------
        str
            Path to the default grid information file

        """
        return ''

    @property
    def additional_grids_file(self) -> str:
        """Returns the path to an additional default grid configuration that overrides the values
        in the basic default grid information.

        This method should be overridden of a child class if additional default grid information are
        needed.

        Returns
        -------
        str
            Path to the grid information file
        """
        return ''
