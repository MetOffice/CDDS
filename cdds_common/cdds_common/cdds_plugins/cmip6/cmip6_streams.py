# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`cmip6_streams` module contains the code required to
handle stream information for CMIP6 streams.
"""
import os

from cdds_common.cdds_plugins.base.base_streams import BaseStreamInfo, BaseStreamStore


class Cmip6StreamInfo(BaseStreamInfo):

    def __init__(self, config_path: str = ''):
        if not config_path:
            local_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(local_dir, 'data/streams/streams_config.json')
        super(Cmip6StreamInfo, self).__init__(config_path)


class Cmip6StreamStore(BaseStreamStore):

    def __init__(self) -> None:
        stream_info = Cmip6StreamInfo()
        super(Cmip6StreamStore, self).__init__(stream_info)

    @classmethod
    def create_instance(cls) -> 'Cmip6StreamStore':
        return Cmip6StreamStore()
