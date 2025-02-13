# (C) British Crown Copyright 2018-2021, Met Office.
# Please see LICENSE.md for license details.
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
