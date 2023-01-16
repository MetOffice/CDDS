# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.
import os

from cdds.common.plugins.base.base_streams import BaseStreamInfo, BaseStreamStore


class CordexStreamInfo(BaseStreamInfo):

    def __init__(self, config_path: str = '') -> None:
        if not config_path:
            local_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(local_dir, 'data/streams/streams_config.json')
        super(CordexStreamInfo, self).__init__(config_path)


class CordexStreamStore(BaseStreamStore):

    def __init__(self):
        stream_info = CordexStreamInfo()
        super(CordexStreamStore, self).__init__(stream_info)

    @classmethod
    def create_instance(cls) -> 'CordexStreamStore':
        return CordexStreamStore()
