# (C) British Crown Copyright 2023-2025, Met Office.
# Please see LICENSE.md for license details.
"""The :mod:`cordex_streams` module contains the code required to
handle stream information for CORDEX streams.
"""
import os

from cdds.common.plugins.base.base_streams import BaseStreamInfo, BaseStreamStore


class CordexStreamInfo(BaseStreamInfo):
    """Class to store the information for streams. The information of the streams
    are defined in a json file.
    """

    def __init__(self, config_path: str = '') -> None:
        if not config_path:
            local_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(local_dir, 'data/streams/streams_config.json')
        super(CordexStreamInfo, self).__init__(config_path)


class CordexStreamStore(BaseStreamStore):
    """Singleton class to store for the stream information.

    The class is a singleton to avoid excessive loading of the stream information.
    """

    def __init__(self):
        stream_info = CordexStreamInfo()
        super(CordexStreamStore, self).__init__(stream_info)

    @classmethod
    def create_instance(cls) -> 'CordexStreamStore':
        """Creates a new class instance.

        Returns
        -------
        CordexStreamStore
            New class instance
        """
        return CordexStreamStore()
