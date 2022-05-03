# (C) British Crown Copyright 2016-2021, Met Office.
# Please see LICENSE.rst for license details.
import pika

""" This program can be run on the remote client to publish a message
to the pre-configured persistent exchange and queues.

The choice of routing key means that the message will get sent to the
"moose" queue. delivery_mode=2 means that the message will be stored
on disk, so it will survive even if the RabbitMQ server is stopped and
restarted.

After this program is run, you can use the RabbitMQ web management
plugin to see that there is a message waiting in the "moose" queue.
"""

credentials = pika.PlainCredentials("<USERID>", "<PASSWORD>")
connection_param = pika.ConnectionParameters(
    "<RABBIT-HOST>", 5672, "/", credentials)
connection = pika.BlockingConnection(connection_param)

channel = connection.channel()

channel.basic_publish(
    exchange="dds", routing_key="moose.available", body="foo bar baz",
    properties=pika.BasicProperties(delivery_mode=2))

connection.close()
