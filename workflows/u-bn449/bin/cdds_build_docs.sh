#!/bin/bash

rm -rf ${DOC_BUILD_DIR}
mkdir ${DOC_BUILD_DIR}

export CDDS_COMPONENTS="cdds mip_convert"

for COMPONENT in $CDDS_COMPONENTS
do
    mkdir ${DOC_BUILD_DIR}/$COMPONENT/
    cd ${CDDS_SRC_DIR}/$COMPONENT/
    python setup.py build_sphinx -Ea --build-dir=${DOC_BUILD_DIR}/$COMPONENT/
done
