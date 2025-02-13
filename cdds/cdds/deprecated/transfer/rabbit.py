# (C) British Crown Copyright 2016-2021, Met Office.
# Please see LICENSE.md for license details.
import abc
import logging
import pika
import ssl
import time


class RabbitMqManager(object):

    """Maintains a single connection to a RabbitMQ server and provides
    fail-safe communication interfaces.

    Note: the methods follow the "fail safe" communication design
    adopted for the DDS system. Sending messages isn't the top prority
    for the system, and we should expect to run into communication
    problems from time to time. As a result, the methods will trap
    esceptions (with logging calls at appropriate levels) and
    either attempt retries, or return None or void if they fail.

    Public methods:
    call -- run supplied operation on a configured channel
    quick_start -- try to start a connection without retrying if errors occur
    start -- try to start a connection to the RabbitMQ server
    stop -- try to stop a connection to the RabbitMQ server
    """

    def __init__(self, cfg):
        """Create a new configured wrapper to RabbitMQ.

        Note: creating an object does not start a connection to the
        RabbitMQ server - you must run the start method to do that.

        Arguments:
        cfg -- (config.Config) wrapper to Rabbit configuration file
        """
        self._config = cfg
        self._section = "rabbit"
        self._exchange = "dds"
        self._connection = None

    def start(self):
        """Try to start a connection to the RabbitMQ server.

        This method will attempt to open a blocking connection to the
        RabbitMQ server specified in the configuration. If a temporary
        communication problem prevents the connection from being
        opened, the program will enter a retry loop. After a number of
        failed attempts, (or in the event of a problem that cannot be
        fixed by a retry) the method will quietly return.
        """
        try:
            self._start_connection()
        except pika.exceptions.ProbableAuthenticationError:
            # This error is a sub-class of AMQPConnectionError, so we
            # need to check for it first.
            logging.warning("authentication error from rabbit server")
        except pika.exceptions.AMQPConnectionError:
            # server down or other problem that may be temporary.
            logging.info("connection error, attempting reconnect")
            self._polite_reconnect()
        except Exception as exc:
            logging.warning("exception during connection: %s" % exc)
        return

    def quick_start(self):
        """Try to start a connection to the RabbitMQ server.

        This method will attempt to open a blocking connection to the
        RabbitMQ server specified in the configuration. In the event
        of any errors, it will immediately return without opening a
        connection.
        """
        try:
            self._start_connection()
        except Exception as exc:
            logging.warning("exception during connection: %s" % exc)
        return

    def call(self, channel_callable):
        """Run supplied channel callable on a configured channel.

        If a connection is available, this method will attempt to
        create a channel (with appropriate bound queues) and will
        invoke the "call" method on the supplied callable on the
        configured channel.

        Argument
        channel_callable -- (rabbit.ChannelCallable)
        """
        if not self._connection:
            logging.warning("no connection so immediately returning")
            return None
        if not channel_callable.queue:
            logging.warning("no valid queue provided, immediately returning")
            return None
        try:
            channel = self._configured_channel(channel_callable.queue)
            result = channel_callable.call(channel, self._exchange)
        except pika.exceptions.ConnectionClosed:
            logging.warning(
                "connection closed during call, attempting reconnect")
            self._polite_reconnect()
            return None
        except Exception as exc:
            logging.warning("exception during call: %s" % exc)
            return None
        self._close_channel(channel)
        return result

    def stop(self):
        """Close the current RabbitMQ connection."""
        if not self._connection:
            return
        try:
            self._connection.close()
        except Exception as exc:
            logging.warning("exception from connection close: %s" % exc)
        self._connection = None
        return

    def _start_connection(self):
        if self._connection:
            return
        connection_param = self._connection_parameters()
        logging.info("start: trying to connect")
        self._connection = pika.BlockingConnection(connection_param)
        logging.info("successfully connected to rabbit server")
        return

    def _connection_parameters(self):
        use_plain = self._config.optional_attr(self._section, "use_plain")
        if use_plain:
            return self._plain_connection_config()
        else:
            return self._secure_connection_config()

    def _plain_connection_config(self):
        user = self._config.attr(self._section, "userid")
        password = self._config.attr(self._section, "password")
        (host, port, vhost) = self._common_connection_config()
        credentials = pika.credentials.PlainCredentials(user, password)
        params = pika.ConnectionParameters(
            host, port, vhost, credentials=credentials)
        return params

    def _secure_connection_config(self):
        ca_cert = self._config.attr(self._section, "cacert")
        client_cert = self._config.attr(self._section, "client_cert")
        client_key = self._config.attr(self._section, "client_key")
        ssl_options = ({
            "ca_certs": ca_cert, "certfile": client_cert,
            "keyfile": client_key, "cert_reqs": ssl.CERT_REQUIRED,
            "server_side": False})
        (host, port, vhost) = self._common_connection_config()
        credentials = pika.credentials.ExternalCredentials()
        params = pika.ConnectionParameters(
            host, port, vhost, credentials=credentials,
            ssl=True, ssl_options=ssl_options)
        return params

    def _common_connection_config(self):
        host = self._config.attr(self._section, "host")
        port = int(self._config.attr(self._section, "port"))
        vhost = self._config.attr(self._section, "vhost")
        return host, port, vhost

    def _polite_reconnect(self):
        attempt = 1
        wait = 15
        connection_param = self._connection_parameters()
        while not self._connection and attempt <= 5:
            logging.debug("connection retry %d" % attempt)
            try:
                self._connection = pika.BlockingConnection(connection_param)
                logging.debug("successfully connected")
            except pika.exceptions.AMQPConnectionError:
                time.sleep(wait)
                wait *= 2
                attempt += 1
            except Exception as exc:
                logging.warning(
                    "exception while trying to reconnect: %s" % exc)
                break
        return

    def _configured_channel(self, queue):
        channel = self._connection.channel()
        channel.exchange_declare(
            exchange=self._exchange, exchange_type="direct", durable=True)
        queue_name = queue.queue_name
        channel.queue_declare(queue=queue_name, durable=True)
        channel.queue_bind(
            exchange=self._exchange, queue=queue_name, routing_key=queue_name)
        return channel

    def _close_channel(self, channel):
        try:
            channel.close()
        except Exception as exc:
            logging.warning("exception from channel close: %s" % exc)
        return


class ChannelCallable(object, metaclass=abc.ABCMeta):

    """Abstract base class for channel callable classes. Child classes
    must implement the "call" method.

    Properly-configured channels are created and passed to the "call"
    method by RabbitMqManager's call method. The name of the exchange
    is also passed so it is available if necessary.
    """

    @abc.abstractmethod
    def call(self, channel, exchange):
        raise NotImplementedError


class GetFirst(ChannelCallable):

    def __init__(self, queue):
        """Creates a new GetFirst object.

        Arguments:
        queue -- (msg.Queue) queue to get from
        """
        self.queue = queue
        self._queue_name = queue.queue_name

    def call(self, channel, exchange):
        """Run basic_get to retrieve a message from the channel.

        Arguments:
        channel -- (pika.Channel) configured channel
        exchange -- (str) exchange to use if necessary
        """
        logging.info("basic_get with route %s" % self._queue_name)
        method_frame, _, body = channel.basic_get(queue=self._queue_name)
        if method_frame:
            return method_frame, body
        else:
            return None


class GetAll(ChannelCallable):

    def __init__(self, queue):
        """Create a new GetAll object.

        Arguments:
        queue -- (msg.Queue) queue to get messages from
        """
        self.queue = queue
        self._queue_name = queue.queue_name

    def call(self, channel, exchange):
        """Run basic get to retrieve all messages from the channel.

        Arguments:
        channel -- (pika.Channel) configured channel
        exchange -- (str) exchange to use if necessary
        """
        messages = []
        logging.info("basic_get (all) with route %s" % self._queue_name)
        while True:
            method_frame, _, body = channel.basic_get(queue=self._queue_name)
            if method_frame:
                messages.append((method_frame, body))
            else:
                break
        return messages


class PersistentPublish(ChannelCallable):

    def __init__(self, queue, body):
        """Create a new PersistentPublish object.

        Arguments:
        queue -- (msg.Queue) queue to publish to
        body -- (str) body of the message to publish
        """
        self.queue = queue
        self._queue_name = queue.queue_name
        self._body = body

    def call(self, channel, exchange):
        """Run basic_publish to publish our message on the channel.

        The message will be published with delivery mode 2 which means
        that it will be copied to disk.

        Return True if we receive confirm that the message was
        published successfully, False if not.

        Arguments:
        channel -- (pika.Channel) configured channel
        exchange -- (str) exchange to use if necessary
        """
        logging.info("basic_publish, route %s, body %s" % (
            self._queue_name, self._body))
        channel.confirm_delivery()
        try:
            channel.basic_publish(
                exchange=exchange, routing_key=self._queue_name, body=self._body,
                properties=pika.BasicProperties(delivery_mode=2), mandatory=True)
            confirmed = True
        except pika.exceptions.UnroutableError:
            confirmed = False
        return confirmed


class AckMessage(ChannelCallable):

    def __init__(self, queue, delivery_tag):
        """Create a new AckMessage object.

        Note: delivery_tag must be obtained from a message object. You
        should never need to set it explicitly yourself.

        Arguments:
        queue -- (msg.Queue) queue to look for message on
        delivery_tag -- (int) message's internal delivery tag
        """
        self.queue = queue
        self._queue_name = queue.queue_name
        self._delivery_tag = delivery_tag

    def call(self, channel, exchange):
        """Try to send an ACK to a message.

        Search our queue for a message that matches our delivery tag.
        If one is found, run basic_ack on the channel to remove that
        message from the queue.

        Arguments:
        channel -- (pika.Channel) configured channel
        exchange -- (str) exchange to use if necessary
        """
        while True:
            method_frame, _, _ = channel.basic_get(queue=self._queue_name)
            if method_frame:
                if method_frame.delivery_tag == self._delivery_tag:
                    logging.info(
                        "basic_ack, delivery tag %s" %
                        method_frame.delivery_tag)
                    channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                    break
            else:
                break
        return
