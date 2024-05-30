# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
import os

from cdds.common.plugins.gcmodeldev.gcmodeldev_streams import GCModelDevStreamInfo, GCModelDevStreamStore

from unittest import TestCase


class TestGCModelDevStreamInfoRetrieveStreamId(TestCase):

    def setUp(self):
        local_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(local_dir, 'data/streams/streams_config.json')
        self.stream_info = GCModelDevStreamInfo(config_path)

    def test_retrieve_stream_id_from_default(self):
        variable = 'tas'
        mip_table = 'Amon'
        stream, substream = self.stream_info.retrieve_stream_id(variable, mip_table)
        self.assertTupleEqual((stream, substream), ('apm', None))

    def test_retrieve_stream_id_unknown(self):
        variable = 'tas'
        mip_table = 'Xmon'
        stream, substream = self.stream_info.retrieve_stream_id(variable, mip_table)
        self.assertEqual((stream, substream), ('unknown', None))


class TestGCModelDevStreamStore(TestCase):

    def tearDown(self):
        GCModelDevStreamStore.clean_instance()

    def test_get_stream_info(self):
        store = GCModelDevStreamStore.instance()
        stream_info = store.get()
        self.assertIsInstance(stream_info, GCModelDevStreamInfo)

    def test_stream_store_is_singleton(self):
        GCModelDevStreamStore.instance()
        self.assertRaises(Exception, GCModelDevStreamStore())
