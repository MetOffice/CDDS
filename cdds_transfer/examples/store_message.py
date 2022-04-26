# (C) British Crown Copyright 2016-2021, Met Office.
# Please see LICENSE.rst for license details.
import glob
import os.path

import config
import dds
import msg


def main():
    config = load_config()
    cordex_xfer = dds.DataTransfer(config, "CORDEX")
    msg_store = msg.MessageStore(config)
    drs = find_var()
    facets = cordex_xfer.split_into_facets(drs)
    for facet in list(facets.values()):
        available_dir = cordex_xfer.moose_path_to_timestamp(facet, "available")
        msg_content = cordex_xfer.prepare_message(
            facet, available_dir, "available")
        message = msg.Message(content=msg_content)
        msg_store.store_message(message)


def load_config():
    my_path = os.path.realpath(__file__)
    cfg_dir = os.path.dirname(my_path)
    cfg_path = os.path.join(cfg_dir, "localhost.cfg")
    return config.Config(cfg_path)


def find_var():
    drs_full = glob.glob(
        "<LOCAL_TOP_DIR>/"
        "clt_CAS-44_ERAINT_evaluation_r1i1p1_MOHC-HadRM3P_v1_mon_*")
    drs_base = [os.path.basename(drs) for drs in drs_full]
    return drs_base


if __name__ == "__main__":
    main()
