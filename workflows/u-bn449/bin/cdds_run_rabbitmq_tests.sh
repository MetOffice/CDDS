#!/bin/bash

cd ${CDDS_SRC_DIR}
# Discard any PYTHONPATH entries set by the rose suite
unset PYTHONPATH
. setup_env_for_devel
/usr/bin/time ./run_rabbitmq_tests -v
