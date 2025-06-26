# (C) British Crown Copyright 2016-2025, Met Office.
# Please see LICENSE.md for license details.
"""Classes to interact with RabbitMQ and its messages.

The design philosophy of the communicate classes is to "fail safe".
The assumption is that communication problems (connection failures,
dropouts or message send failurs) can reasonably be expected to happen
but they shouldn't stop the main tasks of sending, moving and getting
data. As a result, communication exceptions are trapped and
appropriate fallback actions are taken (such as saving copies of
messages that couldn't be sent so they can be redelivered later).

Public classes:
    Message -- represents messages to/from RabbitMQ
    MooseMessage -- represents messages about MASS state changes
    AdminMessage -- represents admin messages
    Queue -- represents RabbitMQ message queues
    Communication -- provides RabbitMQ communication services
    MessageStore -- interface to safe backup copies of messages
"""
from datetime import datetime
import glob
import logging
import json
import os

from cdds.deprecated.transfer import rabbit
from cdds.deprecated.transfer.constants import KNOWN_RABBITMQ_QUEUES


class Message(object):

    """Create and interact with RabbitMQ messages.

    Abstract methods:
    queue_prefix -- override to return queue prefix for message
    queue_suffix -- override to return queue suffix for message

    Public methods:
    sort_messages -- sort messages by publication date
    sortable -- return sort key for message
    queue -- return queue name
    add_published_ts -- add a published timestamp to message
    timeless_content -- return a copy of message without published timestamp

    Property:
    published -- return published date (if available)
    """
    TYPE: str | None = None
    TS_FMT = "%Y%m%dT%H%M%SZ"

    @staticmethod
    def sort_messages(unsorted, *more_unsorted):
        """Sort messages by published timestamp and returns a sorted
        list. Raises a ValueError if any of the input messages is
        missing a "published" date.

        Arguments:
        unsorted -- (list of Message objects) message(s) to be sorted
        more_unsorted -- (optional) further lists to merge sort
        """
        if more_unsorted:
            to_add = []
            for extra in more_unsorted:
                to_add += extra
            unsorted += to_add
        return sorted(unsorted, key=Message.sortable)

    @staticmethod
    def sortable(message):
        """Return a sort key for the supplied message. Raises a
        ValueError if the sort key (published date) isn't defined.

        Arguments:
        message -- (msg.Message) message object
        """
        key = message.published
        if key is None:
            raise ValueError(
                "Message must have been published to be sortable")
        return key

    def __init__(self, content=None, body=None):
        """Create a new Message object.

        Messages can be created either using a content dict, or using
        a body (str in JSON format). You must supply one of the
        arguments, and can't supply both.

        Keyword arguments:
        content -- (dict) message content
        body -- (str) message content in JSON format
        """
        if content and body:
            raise ValueError("Need only one of content or body")
        if not content and not body:
            raise ValueError("Need content or body")
        if content:
            self._initialise_from_content(content)
        if body:
            self._initialise_from_body(body)
        self.delivery_tag = None

    def queue_prefix(self):
        """Return queue prefix for messages of my type."""
        raise NotImplementedError

    def queue_suffix(self):
        """Return queue suffix for my message."""
        raise NotImplementedError

    def queue(self):
        """Return a queue for my message."""
        return Queue(self.queue_prefix(), self.queue_suffix())

    def add_published_ts(self):
        """Add a publication timestamp to my message. Timestamps are
        UTC.
        """
        self.content["published"] = Message._utc_now_timestamp()
        self.body = self._body_from_content(self.content)

    def timeless_content(self):
        """Return a copy of my message with publication date removed."""
        timeless = self.content.copy()
        try:
            del timeless["published"]
        except KeyError:
            pass
        timeless["type"] = self.type
        return timeless

    @property
    def type(self):
        return self.TYPE

    @property
    def published(self):
        """Return publication date (if set) or None if message has not
        been published.
        """
        ts = self._get_from_content("published")
        if ts:
            return datetime.strptime(ts, Message.TS_FMT)
        else:
            return None

    @staticmethod
    def _utc_now_timestamp():
        now = datetime.utcnow()
        return now.strftime(Message.TS_FMT)

    @staticmethod
    def _body_from_content(content):
        return json.dumps(content)

    @staticmethod
    def _content_from_body(body):
        return json.loads(body)

    def _initialise_from_content(self, content):
        self.content = content
        self.body = self._body_from_content(content)
        return

    def _initialise_from_body(self, body):
        self.body = body
        self.content = self._content_from_body(body)
        return

    def _get_from_content(self, attr_name):
        try:
            val = self.content[attr_name]
        except KeyError:
            val = None
        return val

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.timeless_content() == other.timeless_content()
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return "content: %s, delivery_tag: %s" % (
            self.content, self.delivery_tag)


class MooseMessage(Message):

    """Represents a message to send to or that has been read from the
    moose.# queues.

    Public methods:
    queue_prefix -- Return queue prefix for MOOSE queues
    queue_suffix -- Return queue suffix for MOOSE message

    Properties:
    facets -- Return DRS facets contained in message
    moose_dir -- Return MOOSE directory path contained in message
    project -- Return project facet
    """

    TYPE = "moose"

    def __init__(self, content=None, body=None):
        """Create a MOOSE message object.

        You must supply one (and only one) of either content or body
        to create a message.

        Keyword arguments:
        content -- (dict) message content
        body -- (str) message content in JSON format
        """
        # self.type = MooseMessage.TYPE
        super(MooseMessage, self).__init__(content, body)
        self.dataset_id = self.content.get('dataset_id', None)

    def queue_prefix(self):
        """Return the queue prefix for MOOSE messages (str)."""
        return MooseMessage.TYPE

    def queue_suffix(self):
        """Return the queue suffix for this message (str)."""
        suffix = '{}_{}'.format(self._get_from_content("mip_era"),
                                self._get_from_content("state"))
        return suffix

    @property
    def facets(self):
        """Return the DRS facets contained in the message (dict)."""
        return self._get_from_content("facets")

    @property
    def moose_dir(self):
        """Return the MASS directory path contained in the message (str)."""
        return self._get_from_content("mass_dir")

    @property
    def mip(self):
        """Return the |MIP| (str) if defined or None."""
        my_facets = self.facets
        try:
            mip = my_facets["mip"]
        except KeyError:
            mip = None
        return mip


class AdminMessage(Message):

    """Represents a message to send to or that has been read from the
    admin.# message queues.

    Public methods:
    critical -- create a new critical admin message
    info -- create a new info admin message
    is_critical -- return True if message is a critical admin message
    is_info -- return True if message is an info admin message
    queue_prefix -- return the queue prefix for admin messages
    queue_suffix -- return the queue suffix for my message

    Properties:
    action -- return the action that should be taken to fix the admin issue
    description -- return a description of the admin issue
    level -- return the seriousness of the admin issue
    """

    TYPE = "admin"

    @staticmethod
    def critical(description, action):
        """Create a critical-level admin message.

        Arguments:
        description -- (str) a description of the admin issue
        action -- (str) action that should be taken to fix the issue
        """
        message = AdminMessage._build_message(description, action)
        message.content["level"] = "critical"
        return message

    @staticmethod
    def info(description, action):
        """Create an info-level admin message.

        Arguments:
        description -- (str) a description of the admin issue
        action -- (str) action that should be taken to fix the issue
        """
        message = AdminMessage._build_message(description, action)
        message.content["level"] = "info"
        return message

    @staticmethod
    def queue_prefix(self):
        """Return queue prefix (str) for admin messages."""
        return AdminMessage.TYPE

    def __init__(self, content=None, body=None):
        """Create a new admin message object.

        You must supply one (and only one) of content or body to
        create the message.

        Keyword arguments:
        content -- (dict) message content
        body -- (str) message content in JSON format
        """
        # self.type = AdminMessage.TYPE
        super(AdminMessage, self).__init__(content, body)

    def queue_suffix(self):
        """Return the queue suffix (str) for this message."""
        return self.level

    def is_critical(self):
        """Return True if this message is a critical-level message."""
        return self.level == "critical"

    def is_info(self):
        """Return True if this message is an info-level message."""
        return self.level == "info"

    @property
    def description(self):
        """Return a description of the admin issue (str)."""
        return self._get_from_content("description")

    @property
    def action(self):
        """Return the action required to fix the admin issue (str)."""
        return self._get_from_content("action")

    @property
    def level(self):
        """Return the level of the admin message (str)."""
        return self._get_from_content("level")

    @staticmethod
    def _build_message(description, action):
        content = {"description": description, "action": action}
        return AdminMessage(content=content)


class Queue(object):

    """Provides interfaces to Rabbit queues.

    Note: valid queue names are kept in the source code - the class
    does not communicate with the RabbitMQ server to list known
    queues.

    Public methods:
    is_valid -- return True if queue name is a valid queue name
    known -- determine whether a queue is known
    known_type -- determine whether a queue is a valid type
    message_class -- return message type for current queue
    msg_type -- return message type for supplied queue prefix, if known
    queue_name -- return name of queue
    """

    KNOWN_QUEUES = {
        "moose": {"suffix": ["CMIP6_available_test", "CMIP6_withdrawn_test",
                             "testing_available", "testing_withdrawn",
                             "available", "withdrawn"] + KNOWN_RABBITMQ_QUEUES,
                  "message": MooseMessage},
        "admin": {"suffix": ["critical", "info"],
                  "message": AdminMessage}}

    @staticmethod
    def known(prefix, suffix):
        """Return True if supplied prefix and suffix generate a known
        queue name.

        Arguments:
        prefix -- (str) queue prefix
        suffix -- (str) queue suffix
        """
        try:
            is_known = (
                Queue.known_type(prefix) and
                suffix in Queue.KNOWN_QUEUES[prefix]["suffix"])
        except KeyError:
            is_known = False
        return is_known

    @staticmethod
    def known_type(prefix):
        """Return True if the queue prefix is known.

        Arguments:
        prefix -- (str) queue prefix.
        """
        if prefix in Queue.KNOWN_QUEUES:
            return True
        else:
            return False

    @staticmethod
    def msg_type(prefix):
        """Return the class to use to create a message that will match
        the supplied queue prefix. If the queue is not known, return
        None.

        Arguments:
        prefix -- (str) queue prefix.
        """
        if Queue.known_type(prefix):
            return Queue.KNOWN_QUEUES[prefix]["message"]
        else:
            return None

    @staticmethod
    def is_valid(queue_name):
        """Return True if queue name is known.

        Arguments:
        queue_name -- (str) queue name
        """
        try:
            (prefix, suffix) = queue_name.split(".")
            valid = Queue.known(prefix, suffix)
        except ValueError:
            valid = False
        return valid

    def __init__(self, prefix, suffix):
        """Create a new object to represent a RabbitMQ queue.

        Arguments:
        prefix -- (str) queue prefix
        suffix -- (str) queue suffix
        """
        self.prefix = prefix
        self.suffix = suffix

    @property
    def queue_name(self):
        """Return my queue name (if valid) or None if not."""
        if Queue.known(self.prefix, self.suffix):
            name = ".".join([self.prefix, self.suffix])
        else:
            name = None
        return name

    def message_class(self):
        """Return the message class to use to represent messages
        obtained from queues of my type.
        """
        return Queue.msg_type(self.prefix)


class Communication(object):

    """Provide communications with RabbitMQ.

    This class provides methods for sending and reading messages from
    the RabbitMQ queues. When an object is created, a single,
    persistent connection to the RabbitMQ host specified in the
    configuration is created, if possible.

    Public methods:
    get_all_messages -- get all messages from a queue
    get_first_matching_message -- get the first message from a queue
    publish_message -- send a message to the appropriate queue
    remove_message -- remove a message from a queue
    store_message -- save a copy of a message to the message store
    """

    def __init__(self, config):
        """Create a new communication object.

        The object will attempt to start a single, persistent
        connection to the configured RabbitMQ server. If communication
        problems occur, the message will "fail safe" rather than
        raising errors.

        Arguments:
        config -- (config.Config) wrapper around Rabbit configuration file
        """
        self._config = config
        self._rabbit_mgr = rabbit.RabbitMqManager(self._config)
        self._rabbit_mgr.start()

    def publish_message(self, message, queue=None):
        """Publish the supplied message on an appropriate queue.

        Messages will be published using flags that will make them
        persist on the message queues. If any communication failures
        occur, a copy of the message will be saved to the message
        store.

        Arguments:
        message -- (msg.Message) message to be published
        queue -- (msg.Queue) (optional) override queue specified in
        message to write to.

        Raises:
        RutimeError -- If the message is about some data (i.e.
        availability, withdrawal) and the dataset id has been omitted.
        """
        logger = logging.getLogger(__name__)
        if isinstance(message, MooseMessage) and message.dataset_id is None:
            raise RuntimeError('Cannot send message about data without a '
                               'dataset_id')
        message.add_published_ts()
        if queue is None:
            queue = message.queue()
        else:
            logger.debug('Publishing message to queue "{}" rather than "{}"'
                         ''.format(queue.queue_name,
                                   message.queue().queue_name))
        published = False
        channel_callable = rabbit.PersistentPublish(queue, message.body)
        if self._rabbit_mgr.call(channel_callable):
            published = True
        if not published:
            logger.critical('Publication of message to queue "{}" failed. '
                            'Saving locally'.format(queue.queue_name))
            self.store_message(message)
        return message

    def get_first_matching_message(self, queue):
        """Return the first message on the queue (or None).

        The message will be of a type appropriate to the queue (e.g. a
        Queue object representing a moose.#  queue will return a
        MooseMessage object).

        Note: getting a message is a copy operation. The message will
        remain visible on the queue until is has been explicitly
        deleted by a "remove_message" call.

        Argument:
        queue -- (msg.Queue) queue to search for messages
        """
        message = None
        channel_callable = rabbit.GetFirst(queue)
        result = self._rabbit_mgr.call(channel_callable)
        if result:
            (method_frame, body) = result
            message = self._make_message(queue, method_frame, body)
        return message

    def get_all_messages(self, queue):
        """Return all the messages available on queue (or an empty
        list if no messages are available, or communications fail).

        Note that the messages will be of a type appropriate to the
        queue (e.g. a Queue object representing a moose.#  queue will
        return a list of MooseMessage objects).

        Note: getting messages is a copy operation. Messages will be
        left on the queue until they are explicitly deleted with a
        remove_message call.

        Argument:
        queue -- (msg.Queue) queue to search for messages.
        """
        messages = []
        channel_callable = rabbit.GetAll(queue)
        result = self._rabbit_mgr.call(channel_callable)
        if result:
            for msg in result:
                (method_frame, body) = msg
                message = self._make_message(queue, method_frame, body)
                messages.append(message)
        return messages

    def remove_message(self, queue, message):
        """Remove a message from a queue.

        Successfully invoking this method will cause the message to be
        removed from the message queue. Note that you need a copy of a
        message to delete it from a queue, so you will have the
        message and its contents available to you for the duration of
        the program that calls this method.

        Arguments:
        queue -- (msg.Queue) queue to remove the message from
        message -- (msg.Message) message to be deleted
        """
        channel_callable = rabbit.AckMessage(queue, message.delivery_tag)
        result = self._rabbit_mgr.call(channel_callable)
        return result

    def store_message(self, message):
        """Save a copy of a message to the local message store.

        Arguments:
        message -- (msg.Message) message to save
        """
        message_store = MessageStore(self._config)
        message_store.store_message(message)
        return

    def _make_message(self, queue, method_frame, body):
        msg_type = queue.message_class()
        if msg_type:
            message = msg_type(body=body)
            message.delivery_tag = method_frame.delivery_tag
        else:
            message = None
        return message


class MessageStore(object):

    """Interface to the local message store.

    Messages can be saved to and restored from files on a local
    directory. This will happen automatically in the event of
    communication problems so that messages can be re-sent later.

    Public methods:
    store_message -- save a message to the store
    saved_messages -- find all the messages currently in the store
    load_message -- load a message from the store
    remove_saved_message -- remove a message from the store
    """

    def __init__(self, config):
        """Create a new MessageStore object.

        Arguments:
        config -- (config.Config) interface to configuration files
        """
        self._msg_dir = config.attr("msg_store", "top_dir")

    def store_message(self, message):
        """Save a copy of the message to the message store.

        Note: messages saved to the store are (most likely) being
        saved because they could not be published. To avoid including
        potentially misleading "published" metadata, a copy of the
        message without any "published" datestamp is saved.

        Arguments:
        message -- (msg.Message) message to save
        """
        to_store = message.timeless_content()
        msg_base = self._msg_file()
        self._save_message(msg_base, to_store)
        return

    def saved_messages(self):
        """Return a list of message files currently in the store.

        Search the local message store and a return a list of any
        saved message files found there in a form (list of message
        file basenames) suitable for use in load_message calls.
        """
        # Match YYYYMMDDHHMMSS_nn files
        match = "2" + "[0-9]" * 13 + "_[0-9][0-9]"
        messages = glob.glob("%s/%s" % (self._msg_dir, match))
        return [os.path.basename(msg_file) for msg_file in messages]

    def load_message(self, msg_base):
        """Load a message from a saved copy.

        If the message is created and contains the expected content,
        return a message object of appropriate type. Otherwise return
        None.

        Arguments:
        msg_base -- (str) File name containing the stored message
        """
        content = self._read_message(msg_base)
        try:
            message_type = Queue.msg_type(content["type"])
            message = message_type(content=content)
            return message
        except (KeyError, TypeError):
            return None

    def remove_saved_message(self, msg_base):
        """Delete a saved message from the message store.

        Arguments:
        msg_base -- (str) file name containing the stored message
        """
        msg_file = self._msg_full_path(msg_base)
        os.remove(msg_file)
        return

    def _msg_file(self):
        now = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        already_stored = glob.glob(
            os.path.join(self._msg_dir, "%s_*" % now))
        suffix = "%2.2d" % len(already_stored)
        return "%s_%s" % (now, suffix)

    def _save_message(self, msg_base, content):
        logger = logging.getLogger(__name__)
        msg_file = self._msg_full_path(msg_base)
        if os.path.exists(msg_file):
            raise IOError("Message file %s already exists" % msg_file)

        logger.debug('Writing message to file "{}"'.format(msg_file))

        fh = open(msg_file, "w")
        json.dump(content, fh)
        fh.close()
        return

    def _read_message(self, msg_base):
        msg_file = self._msg_full_path(msg_base)
        if not os.path.exists(msg_file):
            raise IOError("No message file %s" % msg_file)
        fh = open(msg_file)
        content = json.load(fh)
        fh.close()
        return content

    def _msg_full_path(self, msg_base):
        return os.path.join(self._msg_dir, msg_base)
