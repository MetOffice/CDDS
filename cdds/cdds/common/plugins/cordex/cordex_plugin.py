# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.
from typing import Type, Dict, Any

from cdds.common.plugins.base.base_plugin import BasePlugin, MipEra
from cdds.common.plugins.file_info import ModelFileInfo, RegionalModelFileInfo
from cdds.common.plugins.cordex.cordex_attributes import CordexGlobalAttributes
from cdds.common.plugins.cordex.cordex_models import CordexModelStore
from cdds.common.plugins.cordex.cordex_grid import CordexGridLabel
from cdds.common.plugins.cordex.cordex_streams import CordexStreamStore
from cdds.common.plugins.attributes import GlobalAttributes
from cdds.common.plugins.grid import GridLabel
from cdds.common.plugins.models import ModelParameters
from cdds.common.plugins.streams import StreamInfo


class CordexPlugin(BasePlugin):

    def __init__(self) -> None:
        super(CordexPlugin, self).__init__(MipEra.CORDEX)

    def models_parameters(self, model_id: str) -> ModelParameters:
        model_store = CordexModelStore.instance()
        return model_store.get(model_id)

    def overload_models_parameters(self, source_dir: str) -> None:
        model_store = CordexModelStore.instance()
        model_store.overload_params(source_dir)

    def grid_labels(self) -> Type[GridLabel]:
        return CordexGridLabel

    def stream_info(self) -> StreamInfo:
        stream_store = CordexStreamStore.instance()
        return stream_store.get()

    def global_attributes(self, request: Dict[str, Any]) -> GlobalAttributes:
        return CordexGlobalAttributes()

    def model_file_info(self) -> ModelFileInfo:
        return RegionalModelFileInfo()
