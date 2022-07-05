# (C) British Crown Copyright 2022-2022, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`gcmodeldev_streams` module contains the code required to
handle stream information for GCModelDev streams.
"""
import os

from common.cdds_plugins.base.base_streams import BaseStreamInfo, BaseStreamStore


class GCModelDevStreamInfo(BaseStreamInfo):
    """
    Class to store the information for streams. The information of the streams
    are defined in a json file.
    """

    def __init__(self, config_path: str = '') -> None:
        if not config_path:
            local_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(local_dir, 'data/streams/streams_config.json')
        super(GCModelDevStreamInfo, self).__init__(config_path)


class GCModelDevStreamStore(BaseStreamStore):
    """
    Singleton class to store for the stream information.

    The class is a singleton to avoid excessive loading of the stream information.
    """

    def __init__(self) -> None:
        stream_info = GCModelDevStreamInfo()
        super(GCModelDevStreamStore, self).__init__(stream_info)

    @classmethod
    def create_instance(cls) -> 'GCModelDevStreamStore':
        """
        Creates a new class instance.

        :return: New class instance
        :rtype: GCModelDevStreamStore
        """
        return GCModelDevStreamStore()
