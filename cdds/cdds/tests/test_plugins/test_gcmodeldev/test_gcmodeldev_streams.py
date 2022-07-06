# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
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
