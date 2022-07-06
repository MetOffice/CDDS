# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`cmip6_streams` module contains the code required to
handle stream information for CMIP6 streams.
"""
import os

from common.plugins.base.base_streams import BaseStreamInfo, BaseStreamStore


class Cmip6StreamInfo(BaseStreamInfo):
    """
    Class to store the information for streams. The information of the streams
    are defined in a json file.
    """

    def __init__(self, config_path: str = '') -> None:
        if not config_path:
            local_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(local_dir, 'data/streams/streams_config.json')
        super(Cmip6StreamInfo, self).__init__(config_path)


class Cmip6StreamStore(BaseStreamStore):
    """
    Singleton class to store for the stream information.

    The class is a singleton to avoid excessive loading of the stream information.
    """

    def __init__(self) -> None:
        stream_info = Cmip6StreamInfo()
        super(Cmip6StreamStore, self).__init__(stream_info)

    @classmethod
    def create_instance(cls) -> 'Cmip6StreamStore':
        """
        Creates a new class instance.

        :return: New class instance
        :rtype: Cmip6StreamStore
        """
        return Cmip6StreamStore()
