import os.path

from cdds.common.plugins.base.base_grid_mapping import BaseGridMapping


class CMIP7GridMapping(BaseGridMapping):
    data_folder = os.path.join(os.path.dirname(__file__), "data", "grid_mapping")

    @property
    def additional_default_grids_file(self) -> str:
        """
        Returns the path to an additional default grid configuration that overrides the values
        in the basic default grid information.

        :return: Path to the default grid information file
        :rtype; str
        """
        return os.path.join(self.data_folder, "default_grids.cfg")

    @property
    def additional_grids_file(self) -> str:
        """
        Returns the path to an additional default grid configuration that overrides the values
        in the basic default grid information.

        :return: Path to the grid information file
        :rtype: str
        """

        return os.path.join(self.data_folder, "grids.cfg")
