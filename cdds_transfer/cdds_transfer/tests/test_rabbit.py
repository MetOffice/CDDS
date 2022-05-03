# (C) British Crown Copyright 2016-2021, Met Office.
# Please see LICENSE.rst for license details.
from unittest.mock import call
import logging
from nose.plugins.attrib import attr
import os.path
import pika
import unittest

from cdds_transfer import config, msg, rabbit
from cdds_transfer.tests import util
from cdds_transfer.common import SYSTEMS_ALLOWED_TO_SEND_MESSAGES


def config_path():
    return os.path.join(os.environ['HOME'], '.cdds_credentials')


def check_if_rabbit_test_can_run():
    hostname = os.uname()[1]
    if hostname not in SYSTEMS_ALLOWED_TO_SEND_MESSAGES:
        raise unittest.SkipTest(
            "Host name \"{}\" not on the list of systems allowed to send "
            "messages.".format(hostname))
    if not os.path.exists(config_path()):
        raise unittest.SkipTest(
            "Please install a \".cdds_credentials\" file in your home "
            "directory")


@attr("slow")
class TestRabbitMqManager(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        check_if_rabbit_test_can_run()

    def setUp(self):
        cfg = config.Config(config_path())
        self.mgr = rabbit.RabbitMqManager(cfg)

    def patch_connection(self, use_mock=None):
        return util.create_patch(self, "pika.BlockingConnection", use_mock)

    def patch_connection_raises_exception(self, exception):
        self.mock_returns = [exception]
        return self.patch_connection(util.mock_with_side_effects(self))

    def patch_reconnect(self):
        return util.create_patch(
            self, "cdds_transfer.rabbit.RabbitMqManager._polite_reconnect")

    def test_start_opens_connection(self):
        mock_connection = self.patch_connection()
        self.assertFalse(mock_connection.called)
        self.mgr.start()
        self.assertTrue(mock_connection.called)

    def test_start_only_opens_once(self):
        mock_connection = self.patch_connection()
        self.mgr.start()
        self.mgr.start()
        self.assertEqual(mock_connection.call_count, 1)

    def test_authentication_error_does_not_retry(self):
        exc = pika.exceptions.ProbableAuthenticationError(
            "fake authentication error")
        self.patch_connection_raises_exception(exc)
        mock_retry = self.patch_reconnect()
        # added next line to disable logging
        logging.disable(logging.CRITICAL)
        self.mgr.start()
        # re-enable to avoid affecting other tests?
        logging.disable(logging.NOTSET)
        self.assertFalse(mock_retry.called)

    def test_connection_error_does_retry(self):
        exc = pika.exceptions.AMQPConnectionError("fake connection error")
        self.patch_connection_raises_exception(exc)
        mock_retry = self.patch_reconnect()
        self.mgr.start()
        self.assertTrue(mock_retry.called)

    def test_polite_reconnect_behaves_correctly(self):
        exc = pika.exceptions.AMQPConnectionError("fake connection error")
        self.mock_returns = [exc] * 5
        self.patch_connection(util.mock_with_side_effects(self))
        mock_sleep = util.create_patch(self, "time.sleep")
        expected_calls = [
            call(15), call(30), call(60), call(120), call(240)]
        self.mgr._polite_reconnect()
        self.assertEqual(mock_sleep.mock_calls, expected_calls)


@attr("slow")
class TestRabbit(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        check_if_rabbit_test_can_run()

        cfg = config.Config(config_path())
        cls.RABBIT_MANAGER = rabbit.RabbitMqManager(cfg)
        cls.RABBIT_MANAGER.quick_start()
        if not cls.RABBIT_MANAGER._connection:
            raise unittest.SkipTest("RabbitMQ not running on localhost")

    @classmethod
    def tearDownClass(cls):
        if cls.RABBIT_MANAGER:
            cls.RABBIT_MANAGER.stop()
        return

    def setUp(self):
        self.available = "testing_available"
        self.withdrawn = "testing_withdrawn"
        self.exchange = "dds_dev"
        self.states = [self.available, self.withdrawn]

    def tearDown(self):
        # Empty out all the queues but leave the connection running.
        channel = self.RABBIT_MANAGER._connection.channel()
        for state in self.states:
            route = self._queue(state).queue_name
            while True:
                method_frame, _, _ = channel.basic_get(queue=route)
                if method_frame:
                    channel.basic_ack(
                        delivery_tag=method_frame.delivery_tag)
                else:
                    break
        channel.close()

    def test_get_first(self):
        self._publish_mixed_topics()
        before_get = self._msg_count(self.available)
        getter = rabbit.GetFirst(self._queue(self.available))
        result = self.RABBIT_MANAGER.call(getter)
        self.assertTrue(result is not None)
        self.assertEqual(self._msg_count(self.available), before_get)
        self.assertEqual(result[1], b"test message 0")

    def test_get_all(self):
        self._publish_mixed_topics()
        getter = rabbit.GetAll(self._queue(self.available))
        messages = self.RABBIT_MANAGER.call(getter)
        self.assertEqual(len(messages), 3)
        for i in range(3):
            self.assertEqual(messages[i][1], b"test message %d" % i)

    def test_publish(self):
        before_publish = self._msg_count(self.available)
        publisher = rabbit.PersistentPublish(
            self._queue(self.available), "test msg")
        result = self.RABBIT_MANAGER.call(publisher)
        self.assertTrue(result)
        after_publish = self._msg_count(self.available)
        self.assertEqual(after_publish, before_publish + 1)

    def Xtest_publish_detects_delivery_failure(self):
        # patch out queue creation methods so that rabbit.call doesn't
        # create the queue for me.
        util.create_patch(self, "pika.Channel.queue_declare")
        util.create_patch(self, "pika.Channel.queue_bind")
        publisher = rabbit.PersistentPublish("no_such_state", "test msg")
        result = self.RABBIT_MANAGER.call(publisher)
        self.assertFalse(result)

    def test_remove_message(self):
        self._publish_mixed_topics()
        self.assertEqual(self._msg_count(self.withdrawn), 1)
        ack_message = rabbit.AckMessage(self._queue(self.withdrawn), 1)
        self.RABBIT_MANAGER.call(ack_message)
        self.assertEqual(self._msg_count(self.withdrawn), 0)

    def _queue(self, state):
        return msg.Queue("moose", state)

    def _msg_count(self, state):
        logging.info("getting channel for message count")
        channel = self.RABBIT_MANAGER._connection.channel()
        routing_key = self._queue(state).queue_name
        msg_count = 0
        while True:
            method_frame, _, _ = channel.basic_get(queue=routing_key)
            if method_frame:
                msg_count += 1
            else:
                break
        logging.info("closing channel for message count")
        channel.close()
        logging.info("closed")
        return msg_count

    def _publish_mixed_topics(self):
        for message in range(3):
            publisher = rabbit.PersistentPublish(
                self._queue(self.available), "test message %d" % message)
            self.RABBIT_MANAGER.call(publisher)
        publisher = rabbit.PersistentPublish(
            self._queue(self.withdrawn), "test withdrawn")
        self.RABBIT_MANAGER.call(publisher)
        return


@attr("slow")
class TestPlainCredentials(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        check_if_rabbit_test_can_run()

    def test_start_with_plain(self):
        cfg = config.Config(config_path())
        queue_mgr = rabbit.RabbitMqManager(cfg)
        queue_mgr.quick_start()
        if queue_mgr._connection:
            self.assertTrue(True)
        else:
            self.fail("Can't open connection with plain credentials")


if __name__ == "__main__":
    logging.basicConfig(
        format="%(levelname)s %(asctime)s %(funcName)s %(message)s",
        level=logging.ERROR)
    unittest.main()
