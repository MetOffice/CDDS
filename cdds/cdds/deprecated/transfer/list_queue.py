#!/usr/bin/env python3.6
# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
"""
Print a list of messages in the CMIP6 queues
"""
import json
import os

from cdds.deprecated.transfer import config, msg


def print_queue(queue_name, full=False):
    """
    Obtain and print the messages in the relevant queue.

    PARAMETERS
    ----------
    queue_name : str
        Queue to print messages from.
    full : bool
        Whether to print fill message output
    """
    cfg = config.Config([os.path.expandvars('$HOME/.cdds_credentials')])
    queue = msg.Queue('moose', queue_name)
    comm = msg.Communication(cfg)

    for i, message in enumerate(comm.get_all_messages(queue)):
        print(i, message.dataset_id)
        if full:
            message_data = vars(message)
            message_data['body'] = message_data['body'].decode('utf-8')
            print(json.dumps(message_data, indent=2, sort_keys=True).replace('\\"', '"'))
