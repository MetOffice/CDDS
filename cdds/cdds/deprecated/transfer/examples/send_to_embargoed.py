# (C) British Crown Copyright 2016-2021, Met Office.
# Please see LICENSE.rst for license details.
import glob
import logging
import os.path
import sys

import config
import dds
from drs import DrsException
import state


def main():
    config = load_config()
    setup_log()
    cordex_xfer = dds.DataTransfer(config, "CORDEX")
    drs = find_var()
    try:
        cordex_xfer.send_to_mass(drs, state.make_state(state.EMBARGOED))
    except DrsException as exc:
        sys.exit("Configuration error: %s" % exc)


def load_config():
    my_path = os.path.realpath(__file__)
    cfg_dir = os.path.dirname(my_path)
    cfg = []
    for cfg_file in ["mohc_global.cfg", "rabbit_localhost.cfg", "cordex.cfg"]:
        cfg.append(os.path.join(cfg_dir, cfg_file))
    return config.Config(cfg)


def setup_log():
    logging.basicConfig(
        format="%(levelname)s %(asctime)s %(message)s",
        level=logging.INFO)
    return


def find_var():
    drs_full = glob.glob("<LOCAL_TOP_DIR>/*")
    drs_base = [os.path.basename(drs) for drs in drs_full]
    return drs_base


if __name__ == "__main__":
    main()
