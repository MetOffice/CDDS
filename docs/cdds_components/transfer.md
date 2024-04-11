The following is from the CDDS Trac pages and relate to the construction of queues on the RabbitMQ server  at CEDA


## Adding a Queue

### Description

We need to add a new type of queue (to the existing set of "moose" and "admin"), or an additional queue to the original set ("moose.available", "moose.withdrawn", "admin.critical", "admin.info").

We have agreed with CEDA to set up queues per project, e.g. CMIP6_available and CMIP6_withdrawn. There is also a testing set of queues to avoid functional unit tests in cdds_transfer from nuking the queues.

### Implementation
There's no method in the API to create queues directly, although invoking message methods (e.g. publishing a message) will create durable queues automatically.

If you want to create the queues in advance, you can do so using pika calls.

### Example code

```python
import os
import pika
from cdds_transfer import config
credentials_file = os.path.expandvars('$HOME/.cdds_credentials')
cfg = config.Config([credentials_file])
# get rabbit connection details from the rabbit section of the 
# cdds credentials file
rabbit_cfg = dict(cfg._cp.items('rabbit'))
# Prefix to use to construct queue names
mip_era = 'CMIP6'
# Name of the exchange on the rabbit server that directs
# messages to queues.
exchange = 'dds' 
credentials = pika.PlainCredentials(rabbit_cfg['userid'], 
                                    rabbit_cfg['password'])
connection_parameters = pika.ConnectionParameters(
    rabbit_cfg['host'], rabbit_cfg['port'], rabbit_cfg['vhost'],
    credentials=credentials, ssl=False)
connection = pika.BlockingConnection(connection_parameters)
channel = connection.channel()
channel.exchange_declare(
    exchange=exchange, exchange_type="direct", durable=True)
for queue in ["available", "withdrawn"]:
    queue_name = 'moose.{}_{}'.format(mip_era, queue)
    channel.queue_declare(queue=queue_name, durable=True)
    channel.queue_bind(exchange=exchange, queue=queue_name,
                       routing_key=queue_name)
channel.close()
connection.close()
```

## Clearing a Queue

### Description

You need to connect to a remote queue and clear out all the messages it contains, optionally keeping back-up copies of the messages you remove in the local message store.

### Implementation

Note: this page describes how to use the API to clear a queue. You can also use RabbitMQ's web management interface to purge messages from a queue, if you have the necessary access permissions.

create a cdds_transfer.config.Config object to wrap your local configuration. You will need to configure Rabbit, and you may also need to configure your local directories (if you want to save copies of messages to the local message store).

create a cdds_transfer.msg.Queue object to point to the remote queue

create a cdds_transfer.msg.Communication object

loop over all the messages returned by get_all_messages in reverse order1:

invoke the remove_message method

(optional) invoke the store_message method to save a copy of the message in the local message store

Note: if you don't keep a back-up copy of a message that you delete, there is no way it can be recovered. If you accidentally delete a message without a back-up copy, you will need to regenerate and resend the message.

1 Messages are identified by their delivery_tag, but this is not a unique identifier for a message it is just the position in the queue, so if you attempt to remove delivery_tag 1 then 2 then 3 the change of delivery_tag following each removal will result in the removal of the first, third and fifth messages from the original queue state. Performing the removals in reverse order avoids this problem. This highlights an issue with using the delivery_tag for message identification.

### Example code

```python
from cdds_transfer import config, msg
cfg = config.Config(['.cdds_credentials'])
queue = msg.Queue('moose', 'CMIP6_available')
comm = msg.Communication(cfg)
for message in comm.get_all_messages(queue)[::-1]:  # reverse order
    comm.remove_message(queue, message)
    # comm.store_message(message)  # optional
```

## Removing a queue

### Description
A queue needs to be deleted, either because one with a new name and the same function has been created, or because the queue was created by mistake.

### Implementation
The API does not provide a method for deleting a queue. Instead, you will either need to use the RabbitMQ web API, or use the delete_queue method provided by pika to delete the queue.

### Example code

```python
import os
import pika
from cdds_transfer import config
credentials_file = os.path.expandvars('$HOME/.cdds_credentials')
cfg = config.Config([credentials_file])
# get rabbit connection details from the rabbit section of the 
# cdds credentials file
rabbit_cfg = dict(cfg._cp.items('rabbit'))
# Name of the queue to be deleted
queue_name = 'queue_to_be_deleted'
# Set up and open connection
credentials = pika.PlainCredentials(rabbit_cfg['userid'], 
                                    rabbit_cfg['password'])
connection_parameters = pika.ConnectionParameters(
    rabbit_cfg['host'], rabbit_cfg['port'], rabbit_cfg['vhost'],
    credentials=credentials, ssl=False)
connection = pika.BlockingConnection(connection_parameters)
channel = connection.channel()
# Delete the queue
channel.queue_delete(queue=queue_name)
# Close down the connection
channel.close()
connection.close()
```
