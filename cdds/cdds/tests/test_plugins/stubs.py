# (C) British Crown Copyright 2021-2025, Met Office.
# Please see LICENSE.md for license details.
from typing import Type

from cdds.common.plugins.file_info import ModelFileInfo
from cdds.common.plugins.grid import GridLabel, GridType, GridInfo
from cdds.common.plugins.models import ModelParameters
from cdds.common.plugins.plugins import CddsPlugin
from cdds.common.plugins.streams import StreamInfo


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

    def model_file_info(self) -> ModelFileInfo:
        return None

    def license(self) -> str:
        return ''

    def mip_table_dir(self) -> str:
        return ''

    def proc_directory(self, request) -> str:
        pass

    def data_directory(self, request) -> str:
        pass

    def requested_variables_list_filename(self, request) -> str:
        pass
