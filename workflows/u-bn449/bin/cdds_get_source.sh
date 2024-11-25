#!/bin/bash

delete_old_sources() {
    echo "Deleting old CDDS source directory ${CDDS_SRC_DIR}"
    rm -rf ${CDDS_SRC_DIR}

    echo "Deleting old CDDS suite directory ${CDDS_SUITE_SRC_DIR}"
    rm -rf ${CDDS_SUITE_SRC_DIR}
}

create_link() {
    echo "Linking $1 to $2"
    ln -s $1 $2
}

checkout() {
    echo "Checking out $1 to $2"
    fcm co $1 $2
}

checkout_git() {
    echo "Checking out branch $2 from $(remove_quotes ${CDDS_GIT_URL}) to $3"
    git clone $1 -b $2 --single-branch $3
    GIT_EXIT_CODE=$?
    if [ ${GIT_EXIT_CODE} != 0 ]; then
        echo "Failed to clone branch $2 from $1 with git error code ${GIT_EXIT_CODE}"
        exit ${GIT_EXIT_CODE}
    fi
}

remove_quotes() {
    echo "$1" | sed -e "s/\\\'//g" -e "s/'//g"
}

get_cdds_source_git() {
    if  [ "${USE_CDDS_LOCAL}" = "True" ]; then
        echo "Use cdds local is True"
        src_path=$(remove_quotes ${CDDS_SRC_PATH})
        create_link $src_path ${CDDS_SRC_DIR}
    else
        echo "Is not True"
        checkout_git $(remove_quotes $CDDS_GIT_URL) $(remove_quotes $CDDS_BRANCH_NAME) $(remove_quotes ${CDDS_SRC_DIR})
    fi
}

get_cdds_suite_source() {
    svn_url=$(remove_quotes ${CDDS_SUITE_SVN_URL})
    checkout $svn_url ${CDDS_SUITE_SRC_DIR}
}

delete_old_sources
get_cdds_source_git
get_cdds_suite_source
