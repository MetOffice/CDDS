# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.md for license details.
"""
The :mod:`cmip6_plus_streams` module contains the code required to
handle stream information for CMIP6Plus streams.
"""
import os

from cdds.common.plugins.base.base_streams import BaseStreamInfo, BaseStreamStore


class Cmip6PlusStreamInfo(BaseStreamInfo):
    """
    Class to store the information for streams. The information of the streams
    are defined in a json file.
    """

    def __init__(self, config_path: str = '') -> None:
        if not config_path:
            local_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(local_dir, 'data/streams/streams_config.json')
        super(Cmip6PlusStreamInfo, self).__init__(config_path)


class Cmip6PlusStreamStore(BaseStreamStore):
    """
    Singleton class to store for the stream information.

    The class is a singleton to avoid excessive loading of the stream information.
    """

    def __init__(self) -> None:
        stream_info = Cmip6PlusStreamInfo()
        super(Cmip6PlusStreamStore, self).__init__(stream_info)

    @classmethod
    def create_instance(cls) -> 'Cmip6PlusStreamStore':
        """
        Creates a new class instance.

        :return: New class instance
        :rtype: Cmip6PlusStreamStore
        """
        return Cmip6PlusStreamStore()
