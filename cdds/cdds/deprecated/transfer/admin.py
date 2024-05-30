# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
"""
Top level routines involved in sending admin messages to CEDA.

WARNING: This code has not been updated and WILL NOT WORK at present.
"""
import os
import sys

from cdds.deprecated.transfer import msg, config


def send_admin_message(args):
    message = make_message(args)
    cfg = read_config_send_admin_msg()
    comms = msg.Communication(cfg)
    comms.publish_message(message)


def read_config_send_admin_msg():
    script_dir = os.path.dirname(__file__)
    cfg_path = os.path.join(script_dir, "..", "config", "rabbit.cfg")
    try:
        cfg = config.Config(cfg_path)
    except config.ConfigError as exc:
        sys.exit(exc)
    return cfg


def make_message(args):
    if args.level == "c":
        message = msg.AdminMessage.critical(args.description, args.action)
    else:
        message = msg.AdminMessage.info(args.description, args.action)
    return message
