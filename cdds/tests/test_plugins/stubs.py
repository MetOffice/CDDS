# (C) British Crown Copyright 2021, Met Office.
# Please see LICENSE.rst for license details.
from typing import Type

from common.plugins.grid import GridLabel, GridType, GridInfo
from common.plugins.models import ModelParameters
from common.plugins.plugins import CddsPlugin
from common.plugins.streams import StreamInfo


class EmptyCddsPlugin(CddsPlugin):

    MIP_ERA = "cdds_mip_era"

    def __init__(self):
        super(EmptyCddsPlugin, self).__init__(EmptyCddsPlugin.MIP_ERA)

    def grid_info(self, model_id: str, grid_type: GridType) -> GridInfo:
        return None

    def models_parameters(self, model_id: str) -> ModelParameters:
        return None

    def overload_models_parameters(self, source_dir: str) -> None:
        pass

    def grid_labels(self) -> Type[GridLabel]:
        return None

    def stream_info(self) -> StreamInfo:
        return None
