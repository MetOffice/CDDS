# (C) British Crown Copyright 2022-2025, Met Office.
# Please see LICENSE.md for license details.
"""
The :mod:`cmip7_streams` module contains the code required to
handle stream information for CMIP7 streams.
"""
import os

from cdds.common.plugins.base.base_streams import BaseStreamInfo, BaseStreamStore


class Cmip7StreamInfo(BaseStreamInfo):
    """
    Class to store the information for streams. The information of the streams
    are defined in a json file.
    """

    def __init__(self, config_path: str = '') -> None:
        if not config_path:
            local_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(local_dir, 'data/streams/streams_config.json')
        super(Cmip7StreamInfo, self).__init__(config_path)


class Cmip7StreamStore(BaseStreamStore):
    """
    Singleton class to store for the stream information.

    The class is a singleton to avoid excessive loading of the stream information.
    """

    def __init__(self) -> None:
        stream_info = Cmip7StreamInfo()
        super(Cmip7StreamStore, self).__init__(stream_info)

    @classmethod
    def create_instance(cls) -> 'Cmip7StreamStore':
        """
        Creates a new class instance.

        :return: New class instance
        :rtype: Cmip7StreamStore
        """
        return Cmip7StreamStore()
