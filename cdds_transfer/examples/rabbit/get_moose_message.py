# (C) British Crown Copyright 2016-2021, Met Office.
# Please see LICENSE.rst for license details.
import pika

""" This program pulls messages from the "moose" queue until there are
none left. The messages will be removed from the queue when
"basic_ack" is called.
"""

credentials = pika.PlainCredentials("<USERID>", "<PASSWORD>")
connection_param = pika.ConnectionParameters(
    "<RABBIT-HOST>", 5672, "/", credentials)
connection = pika.BlockingConnection(connection_param)

channel = connection.channel()

while True:
    method_frame, header_frame, body = channel.basic_get("moose")
    if method_frame:
        print(method_frame, header_frame, body)
        channel.basic_ack(method_frame.delivery_tag)
    else:
        break
