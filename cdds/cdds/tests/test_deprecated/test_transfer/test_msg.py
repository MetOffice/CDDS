# (C) British Crown Copyright 2016-2025, Met Office.
# Please see LICENSE.md for license details.
import datetime
import json
import os.path
from unittest.mock import Mock
import unittest

from cdds.deprecated.transfer import msg, state
from cdds.tests.test_deprecated.test_transfer import util


class TestQueue(unittest.TestCase):

    def test_known(self):
        known = {
            "admin": ["critical", "info"],
            "moose": ["available", "withdrawn"]}
        for prefix in known:
            for suffix in known[prefix]:
                self.assertTrue(msg.Queue.known(prefix, suffix))
            self.assertFalse(msg.Queue.known(prefix, "bad"))
        self.assertFalse(msg.Queue.known("no_such_q", "withdrawn"))

    def test_is_valid(self):
        self.assertTrue(msg.Queue.is_valid("moose.available"))
        self.assertFalse(msg.Queue.is_valid("moose.no_such_state"))
        self.assertFalse(msg.Queue.is_valid("bad_q.no_such_state"))
        self.assertFalse(msg.Queue.is_valid("bad_q"))

    def test_queue_name(self):
        queue = msg.Queue("moose", "available")
        self.assertEqual(queue.queue_name, "moose.available")
        queue = msg.Queue("moose", "no_such_state")
        self.assertIsNone(queue.queue_name)

    def test_msg_class(self):
        queue = msg.Queue("moose", "available")
        self.assertEqual(queue.message_class(), msg.MooseMessage)


class TestMessage(unittest.TestCase):

    def test_make_from_content(self):
        content = {"foo": 1, "bar": 2}
        message = msg.Message(content=content)
        self.assertEqual(message.content, content)
        self.assertEqual(message.body, json.dumps(content))

    def test_make_from_body(self):
        body = '{"foo": 1, "bar": 2}'
        message = msg.Message(body=body)
        self.assertEqual(message.body, body)
        self.assertEqual(message.content, json.loads(body))

    def test_eq_ignores_published_timestamp(self):
        content_a = {"foo": 1, "published": "20140101T000000Z"}
        content_b = {"foo": 1, "published": "20150601T155023Z"}
        message_a = msg.Message(content=content_a)
        message_b = msg.Message(content=content_b)
        self.assertEqual(message_a, message_b)

    def test_published(self):
        now = datetime.datetime.utcnow()
        # published ts accurate to second, so zero out microsec.
        now = now.replace(microsecond=0)
        content = {"foo": 1, "bar": 2}
        message = msg.Message(content=content)
        message.add_published_ts()
        self.assertTrue(message.published >= now)


class TestMessageSorting(unittest.TestCase):

    def test_sort_one_message(self):
        message = self.simple_message(ds="20140101")
        ordered_queue = msg.Message.sort_messages([message])
        self.assertEqual(ordered_queue, [message])

    def test_cannot_sort_without_published(self):
        message_a = self.simple_message(ds="20140101")
        message_b = self.simple_message()
        self.assertRaises(
            ValueError, msg.Message.sort_messages, [message_a, message_b])

    def test_easy_case(self):
        msgs = []
        for ds in ["20140101", "20130101", "20150304"]:
            msgs.append(self.simple_message(ds=ds))
        ordered = msg.Message.sort_messages(msgs)
        self.assertEqual(
            ordered[0].content["published"], self.add_ts("20130101"))
        self.assertEqual(
            ordered[1].content["published"], self.add_ts("20140101"))

    def test_sort_two_lists(self):
        msgs_a = []
        for ds in ["20140101", "20140301"]:
            msgs_a.append(self.simple_message(ds=ds))
        msgs_b = []
        for ds in ["20140201", "20140401"]:
            msgs_b.append(self.simple_message(ds=ds))
        ordered = msg.Message.sort_messages(msgs_a, msgs_b)
        self.assertEqual(
            ordered[0].content["published"], self.add_ts("20140101"))
        self.assertEqual(
            ordered[1].content["published"], self.add_ts("20140201"))

    def test_sort_multiple(self):
        a = [self.simple_message("20140101")]
        b = [self.simple_message("20130201")]
        c = [self.simple_message("20150501")]
        ordered = msg.Message.sort_messages(a, b, c)
        self.assertEqual(len(ordered), 3)
        expected_order = [
            self.add_ts("20130201"), self.add_ts("20140101"),
            self.add_ts("20150501")]
        for got, expected in zip(ordered, expected_order):
            self.assertEqual(got.content["published"], expected)

    def simple_message(self, ds=None):
        content = {"foo": 1}
        if ds:
            content["published"] = self.add_ts(ds)
        return msg.Message(content)

    def add_ts(self, ds):
        return ds + "T000000Z"


class TestMooseMessage(unittest.TestCase):

    def test_moose_dir(self):
        content = {
            "mass_dir": "fake_moose_dir",
            "facets": {"mip": "CMIP5", "institute": "MOHC"}}
        message = msg.MooseMessage(content=content)
        self.assertEqual(message.moose_dir, "fake_moose_dir")
        del content["mass_dir"]
        message = msg.MooseMessage(content=content)
        self.assertIsNone(message.moose_dir)

    def test_facets(self):
        content = {
            "moose_dir": "fake_moose_dir",
            "facets": {"mip": "CMIP5", "institute": "MOHC"}}
        message = msg.MooseMessage(content=content)
        self.assertEqual(message.facets, content["facets"])

    def test_mip(self):
        content = {
            "moose_dir": "fake_moose_dir",
            "facets": {"mip": "CMIP5", "institute": "MOHC"}}
        message = msg.MooseMessage(content=content)
        self.assertEqual(message.mip, "CMIP5")

    def test_message_type(self):
        content = {"facets": {}}
        message = msg.MooseMessage(content=content)
        self.assertEqual(message.type, "moose")


class TestAdminMessage(unittest.TestCase):

    def test_message_structure(self):
        content = {
            "level": "critical", "description": "drs updated",
            "action": "update lib"}
        admin_msg = msg.AdminMessage(content=content)
        self.assertEqual(admin_msg.description, "drs updated")
        self.assertTrue(admin_msg.is_critical())

    def test_critical(self):
        admin = msg.AdminMessage.critical("drs updated", "update lib")
        self.assertTrue(admin.is_critical())
        self.assertEqual(admin.action, "update lib")

    def test_info(self):
        admin = msg.AdminMessage.info("drs updated", "update when convenient")
        self.assertTrue(admin.is_info())
        self.assertFalse(admin.is_critical())

    def test_type(self):
        admin_msg = msg.AdminMessage(content={"level": "info"})
        self.assertEqual(admin_msg.type, "admin")


class TestCommunication(unittest.TestCase):

    def setUp(self):
        cfg = util.patch_open_config("GEOMIP")
        self.mock_channel = Mock()
        mock_channel_maker = util.create_patch(
            self, "cdds.deprecated.transfer.rabbit.RabbitMqManager._configured_channel")
        mock_channel_maker.return_value = self.mock_channel
        self.mock_rabbit = util.create_patch(
            self, "cdds.deprecated.transfer.rabbit.RabbitMqManager.start")
        self.comm = msg.Communication(cfg)
        self.comm._rabbit_mgr._connection = True
        self.available = state.make_state(state.AVAILABLE)
        util.create_patch(self, "logging.warning")

    def test_publish_message_logic(self):
        mock_publish = util.create_patch(
            self, "cdds.deprecated.transfer.rabbit.PersistentPublish.call")
        mock_publish.return_value = True
        self.comm.publish_message(msg.MooseMessage(
            {"state": "available", "dataset_id": "d.u.m.m.y"}))
        mock_store = util.create_patch(
            self, "cdds.deprecated.transfer.msg.Communication.store_message")
        mock_publish.assert_called_once_with(self.mock_channel, "dds")
        self.assertFalse(mock_store.called)

    def test_publish_msg_adds_published_timestamp(self):
        mock_publish = util.create_patch(
            self, "cdds.deprecated.transfer.rabbit.PersistentPublish.call")
        mock_publish.return_value = True
        msg_content = {"state": "available", "dataset_id": "d.u.m.m.y"}
        # Round down precision of "now" to seconds so we get the same
        # precision as the "published" timestamp.
        now = datetime.datetime.utcnow()
        now = now.replace(microsecond=0)
        my_message = self.comm.publish_message(msg.MooseMessage(msg_content))
        self.assertTrue("published" in my_message.content)
        published = datetime.datetime.strptime(
            my_message.content["published"], "%Y%m%dT%H%M%SZ")
        self.assertTrue(published >= now)

    def test_delivery_failures_triggers_message_store(self):
        mock_publish = util.create_patch(
            self, "cdds.deprecated.transfer.rabbit.PersistentPublish.call")
        mock_publish.return_value = False
        mock_store_msg = util.create_patch(
            self, "cdds.deprecated.transfer.msg.Communication.store_message")
        self.comm.publish_message(msg.MooseMessage(
            {"state": "available", "dataset_id": "d.u.m.m.y"}))
        self.assertTrue(mock_store_msg.called)

    def test_publish_without_connection_triggers_message_store(self):
        self.comm._rabbit_mgr._connection = None
        mock_store_msg = util.create_patch(
            self, "cdds.deprecated.transfer.msg.Communication.store_message")
        self.comm.publish_message(msg.MooseMessage(
            {"state": "available", "dataset_id": "d.u.m.m.y"}))
        self.assertTrue(mock_store_msg.called)

    def test_read_first_message(self):
        mock_get_first = util.create_patch(
            self, "cdds.deprecated.transfer.rabbit.GetFirst.call")
        mock_method_frame = Mock()
        mock_method_frame.delivery_tag = 1
        mock_get_first.return_value = (mock_method_frame, '{"msg": "body"}')
        test_msg = self.comm.get_first_matching_message(
            msg.Queue("moose", "available"))
        mock_get_first.assert_called_once_with(self.mock_channel, "dds")
        self.assertEqual(test_msg.delivery_tag, 1)

    def test_get_all_messages(self):
        messages = []
        for message_number in range(3):
            mock_method_frame = Mock()
            mock_method_frame.delivery_tag = message_number
            message_body = '{"msg": "%s"}' % message_number
            messages.append((mock_method_frame, message_body))
        mock_get_all = util.create_patch(
            self, "cdds.deprecated.transfer.rabbit.GetAll.call")
        mock_get_all.return_value = messages
        converted_messages = self.comm.get_all_messages(
            msg.Queue("moose", "available"))
        self.assertEqual(len(converted_messages), 3)
        for msg_num in range(len(converted_messages)):
            self.assertEqual(
                converted_messages[msg_num].content["msg"], "%d" % msg_num)
            self.assertEqual(converted_messages[msg_num].delivery_tag, msg_num)

    def test_remove_message(self):
        mock_ack = util.create_patch(
            self, "cdds.deprecated.transfer.rabbit.AckMessage.call")
        mock_message = Mock()
        mock_message.delivery_tag = 1
        self.comm.remove_message(msg.Queue("moose", "available"), mock_message)
        mock_ack.assert_called_once_with(self.mock_channel, "dds")


class TestMessageStore(unittest.TestCase):

    def setUp(self):
        cfg = util.patch_open_config("GEOMIP")
        self.msg_store = msg.MessageStore(cfg)

    def test_store_message_makes_expected_calls(self):
        mock_msg_file = util.create_patch(
            self, "cdds.deprecated.transfer.msg.MessageStore._msg_file")
        mock_msg_file.return_value = "fake_msg_file"
        mock_save_message = util.create_patch(
            self, "cdds.deprecated.transfer.msg.MessageStore._save_message")
        fake_content = {
            "state": "available", "msg": "fake message",
            "published": "20150515T135523Z"}
        message = msg.Message(content=fake_content)
        self.msg_store.store_message(message)
        self.assertTrue(mock_msg_file.called)
        mock_save_message.assert_called_once_with(
            "fake_msg_file", {"state": "available", "msg": "fake message",
                              "type": None})

    def test_msg_file_makes_sortable_distinct_name(self):
        # We want glob to pretend that we match no files, and then
        # that we match one.
        self.mock_returns = [
            [],
            ["%s_00" % datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")]]
        glob_returns = util.mock_with_side_effects(self)
        util.create_patch(self, "glob.glob", use_mock=glob_returns)
        msg_file_name = []
        for quick_loop in range(2):
            msg_file_name.append(self.msg_store._msg_file())
        self.assertEqual(len(msg_file_name), 2)
        self.assertTrue(msg_file_name[0] != msg_file_name[1])
        self.assertRegex(msg_file_name[0], "[0-9]{14}_00")
        self.assertRegex(msg_file_name[1], "[0-9]{14}_01")

    def test_save_message(self):
        fake_content = {"msg": "fake"}
        fake_path = os.path.join("fake_msg_dir", "fake_base")
        mock_exists = util.create_patch(self, "os.path.exists")
        mock_exists.return_value = False
        mock_msg_fh = Mock()
        mock_open = util.create_patch(self, "builtins.open")
        mock_open.return_value = mock_msg_fh
        mock_json = util.create_patch(self, "json.dump")

        self.msg_store._save_message("fake_base", fake_content)
        mock_exists.assert_called_once_with(fake_path)
        mock_open.assert_called_once_with(fake_path, "w")
        mock_json.assert_called_once_with(fake_content, mock_msg_fh)
        self.assertTrue(mock_msg_fh.close.called)

    def test_save_message_fails_if_file_exists(self):
        mock_exists = util.create_patch(self, "os.path.exists")
        mock_exists.return_value = True
        self.assertRaises(
            IOError, self.msg_store._save_message,
            "fake_base", {"msg": "fake"})

    def test_load_message_handles_moose_type(self):
        mock_read_msg = util.create_patch(
            self, "cdds.deprecated.transfer.msg.MessageStore._read_message")
        mock_read_msg.return_value = {"type": "moose"}
        message = self.msg_store.load_message("")
        self.assertIsInstance(message, msg.MooseMessage)

    def test_load_message_handles_admin_type(self):
        mock_read_msg = util.create_patch(
            self, "cdds.deprecated.transfer.msg.MessageStore._read_message")
        mock_read_msg.return_value = {"type": "admin"}
        message = self.msg_store.load_message("")
        self.assertIsInstance(message, msg.AdminMessage)

    def test_load_message_of_unknown_type(self):
        mock_read_msg = util.create_patch(
            self, "cdds.deprecated.transfer.msg.MessageStore._read_message")
        mock_read_msg.return_value = {"type": "unknown"}
        message = self.msg_store.load_message("")
        self.assertIs(message, None)


if __name__ == "__main__":
    unittest.main()
