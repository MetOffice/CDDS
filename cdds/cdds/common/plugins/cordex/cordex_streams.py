# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
"""
The :mod:`cordex_streams` module contains the code required to
handle stream information for CORDEX streams.
"""
import os

from cdds.common.plugins.base.base_streams import BaseStreamInfo, BaseStreamStore


class CordexStreamInfo(BaseStreamInfo):
    """
    Class to store the information for streams. The information of the streams
    are defined in a json file.
    """

    def __init__(self, config_path: str = '') -> None:
        if not config_path:
            local_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(local_dir, 'data/streams/streams_config.json')
        super(CordexStreamInfo, self).__init__(config_path)


class CordexStreamStore(BaseStreamStore):
    """
    Singleton class to store for the stream information.

    The class is a singleton to avoid excessive loading of the stream information.
    """

    def __init__(self):
        stream_info = CordexStreamInfo()
        super(CordexStreamStore, self).__init__(stream_info)

    @classmethod
    def create_instance(cls) -> 'CordexStreamStore':
        """
        Creates a new class instance.

        :return: New class instance
        :rtype: CordexStreamStore
        """
        return CordexStreamStore()
