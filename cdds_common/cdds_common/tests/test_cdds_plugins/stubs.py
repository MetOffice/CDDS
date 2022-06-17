# (C) British Crown Copyright 2021, Met Office.
# Please see LICENSE.rst for license details.
from typing import Dict, Type, List

from cdds_common.cdds_plugins.grid import GridLabel, GridType, GridInfo
from cdds_common.cdds_plugins.models import ModelParameters
from cdds_common.cdds_plugins.plugins import CddsPlugin
from cdds_common.cdds_plugins.streams import StreamInfo


class EmptyCddsPlugin(CddsPlugin):

    MIP_ERA = "cdds_mip_era"

    def __init__(self):
        super(EmptyCddsPlugin, self).__init__(EmptyCddsPlugin.MIP_ERA)

    def grid_info(self, grid_type: GridType) -> Type[GridInfo]:
        return None

    def overload_grid_info(self, source_dir: str) -> None:
        pass

    def models_parameters(self, model_id: str) -> ModelParameters:
        return None

    def overload_models_parameters(self, model_id: str, source_dir: str) -> None:
        pass

    def grid_dim_sizes(self) -> Dict[str, int]:
        return {}

    def grid_labels(self) -> GridLabel:
        return None

    def stream_info(self) -> StreamInfo:
        return None
