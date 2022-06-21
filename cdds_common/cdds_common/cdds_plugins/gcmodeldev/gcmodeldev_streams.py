# (C) British Crown Copyright 2022-2022, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`gcmodeldev_streams` module contains the code required to
handle stream information for GCModelDev streams.
"""
import os

from cdds_common.cdds_plugins.base.base_streams import BaseStreamInfo, BaseStreamStore


class GCModelDevStreamInfo(BaseStreamInfo):

    def __init__(self, config_path: str = ''):
        if not config_path:
            local_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(local_dir, 'data/streams/streams_config.json')
        super(GCModelDevStreamInfo, self).__init__(config_path)


class GCModelDevStreamStore(BaseStreamStore):

    def __init__(self) -> None:
        stream_info = GCModelDevStreamInfo()
        super(GCModelDevStreamStore, self).__init__(stream_info)

    @classmethod
    def create_instance(cls) -> 'GCModelDevStreamStore':
        return GCModelDevStreamStore()
