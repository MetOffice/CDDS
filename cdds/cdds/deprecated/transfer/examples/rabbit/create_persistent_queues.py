# (C) British Crown Copyright 2016-2021, Met Office.
# Please see LICENSE.rst for license details.
import pika

""" This program will create a persistent topic exchange called "dds"
and two persistent queues bound to it called "moose" and "log". The
"moose" queue will get messages with routing tag "moose" followed by
anything, and the "log" queue will get messages with "log" followed by
anything.

It is also possible to add the exchange and the queues using either
rabbitmq-ctl commands, or by using the web api.
"""

credentials = pika.PlainCredentials("<USERID>", "<PASSWORD>")
connection_param = pika.ConnectionParameters(
    "<RABBIT-HOST>", 5672, "/", credentials)
connection = pika.BlockingConnection(connection_param)

channel = connection.channel()

channel.exchange_declare(exchange="dds", type="topic", durable=True)

channel.queue_declare(queue="moose", durable=True)
channel.queue_declare(queue="log", durable=True)

channel.queue_bind(exchange="dds", queue="moose", routing_key="moose.#")
channel.queue_bind(exchange="dds", queue="log", routing_key="log.#")

channel.close()
connection.close()
