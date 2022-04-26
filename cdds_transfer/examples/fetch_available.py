# (C) British Crown Copyright 2016-2021, Met Office.
# Please see LICENSE.rst for license details.
import os.path
import logging

import config
import dds
import drs
import msg
import state


def main():
    setup_log()
    config = find_config()
    comm = msg.Communication(config)
    facet = drs.DataRefSyntax(config, "CORDEX")
    xfer = dds.DataTransfer(config, "CORDEX")
    available = state.make_state(state.AVAILABLE)

    for message in comm.get_all_messages(available):
        facet.fill_facets_from_message(message)
        xfer.copy_from_mass(message.moose_dir, facet)
        comm.remove_from_queue(message)


def find_config():
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


if __name__ == "__main__":
    main()
