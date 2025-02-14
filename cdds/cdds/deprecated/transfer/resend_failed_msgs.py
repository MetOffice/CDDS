#!/usr/bin/env python3.6
# (C) British Crown Copyright 2021-2025, Met Office.
# Please see LICENSE.md for license details.

import os

from cdds.deprecated.transfer import config, msg


def resend_failed_msgs(delete_msgs):
    """
    The message store file should contain the section `msg_store` with the key `top_dir`
    pointing at the location to store messages in. Alternatively this information could be
    placed in the .cdds_credentials file.

    PARAMETERS
    ----------
    delete_msgs : bool
        Delete the messages from disk after sending if True.
    """
    cdds_credentials_file = os.path.expandvars('$HOME/.cdds_credentials')

    cfg = config.Config([cdds_credentials_file])
    comm = msg.Communication(cfg)
    msg_store = msg.MessageStore(cfg)
    stored_msgs = msg_store.saved_messages()

    for stored_msg in stored_msgs:
        message = msg_store.load_message(stored_msg)
        comm.publish_message(message)
        if delete_msgs:
            msg_store.remove_saved_message(stored_msg)
