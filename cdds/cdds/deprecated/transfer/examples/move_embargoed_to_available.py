# (C) British Crown Copyright 2016-2021, Met Office.
# Please see LICENSE.rst for license details.
import glob
import logging
import os.path

import config
import dds
import state


def main():
    config = load_config()
    setup_log()
    cordex_xfer = dds.DataTransfer(config, "CORDEX")
    drs = find_var()
    embargoed = state.make_state(state.EMBARGOED)
    available = state.make_state(state.AVAILABLE)
    cordex_xfer.change_mass_state(drs, embargoed, available)


def load_config():
    my_path = os.path.realpath(__file__)
    cfg_dir = os.path.dirname(my_path)
    cfg = []
    for cfg_file in ["mohc_global.cfg", "rabbit_localhost.cfg", "cordex.cfg"]:
        cfg.append(os.path.join(cfg_dir, cfg_file))
    return config.Config(cfg)


def find_var():
    drs_full = glob.glob(
        "<LOCAL_TOP_DIR>/"
        "clt_CAS-44_ERAINT_evaluation_r1i1p1_MOHC-HadRM3P_v1_mon_*")
    drs_base = [os.path.basename(drs) for drs in drs_full]
    return drs_base


def setup_log():
    logging.basicConfig(
        format="%(levelname)s %(asctime)s %(message)s",
        level=logging.INFO)
    return


if __name__ == "__main__":
    main()
