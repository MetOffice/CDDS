# (C) British Crown Copyright 2018-2022, Met Office.
# Please see LICENSE.rst for license details.
"""
Top level routines involved in archiving data to MASS, i.e. those
used by the send_to_mass script
"""
import logging

from cdds import _DEV
from cdds.common.old_request import read_request
from cdds.deprecated.transfer import state, dds
from cdds.deprecated.transfer.common import (
    cfg_from_cdds_general_config, drs_facet_builder_from_request, find_local,
    log_filesets)

from cdds.deprecated.config import CDDSConfigGeneral


REQUIRED_KEYS_SEND_TO_MASS = []
DEVELOPMENT_MASS_DIR = 'development'
PRODUCTION_MASS_DIR = 'production'


def run_send_to_mass(args):
    """
    Perform the archiving process; load the request and configuration
    information, identify files and archive them.

    Parameters
    ----------
    args : :class:`argparse.Namespace`
        Command line arguments
    """
    logger = logging.getLogger(__name__)
    if args.simulate:
        logger.info('Simulating all contact with MASS')
    # Read request, construct configs
    logger.info('Reading request from "{}"'.format(args.request))
    request = read_request(
        args.request, required_keys=REQUIRED_KEYS_SEND_TO_MASS)
    logger.info('Reading CDDS General Config')
    general_config = CDDSConfigGeneral(args.root_config, request)
    transfer_cfg = cfg_from_cdds_general_config(general_config, request,
                                                args.mass_location)
    # Construct fixed_facet DataRefSyntax object from request and config
    drs_fixed_facet_builder = drs_facet_builder_from_request(request,
                                                             transfer_cfg)
    logger.info('Using following facets to identify data sets to archive: '
                '"{}"'.format(repr(drs_fixed_facet_builder.facets)))
    # Initialise transfer service
    transfer_service = dds.DataTransfer(transfer_cfg, request.mip_era,
                                        simulation=args.simulate)
    # Find files on disk that match the fixed_facet (i.e. the information in
    # the request)
    # TODO: Shouldn't use non-public method :(
    filesets = find_local(general_config._root_data_directory,
                          drs_fixed_facet_builder, transfer_service)
    log_filesets(filesets)
    # Archive files and return success code
    try:
        logger.info('Archiving files')
        # TODO: Shouldn't use non-public method :(
        send_to_mass(general_config._root_data_directory, filesets,
                     transfer_service, state.EMBARGOED)
        logger.info('Archiving complete')
    except Exception as err:
        logger.critical('Archiving failed')
        logger.exception(err)
        raise


def send_to_mass(top_dir, filesets, transfer_service, mass_state):
    """
    Send the specified file sets located under top_dir to MASS in
    the specified state.

    Parameters
    ----------
    top_dir : str
        Top level data directory, e.g. '/project/cdds_data'
    filesets : :class:`cdds.deprecated.transfer.drs.AtomicDatasetCollection`
        Object describing the file sets found on disk
    transfer_service : :class:`cdds.deprecated.transfer.dds.DataTransfer`
        Data transfer service
    mass_state : str
        State to send data to MASS in, should be `embargoed` unless
        there is a very good reason.
    """
    destination_state = state.make_state(mass_state)
    transfer_service.send_to_mass(top_dir, filesets, destination_state)


def allowed_mass_locations():
    """
    Return the list of allowed sub-directories in MASS for archiving
    data to and the default sub-directory to use. These values are
    appended to the top directory in MASS, and are dependent on
    whether CDDS is in development mode or not.

    Returns
    -------
    : list
        List of allowed sub-directories.
    : str
        Default sub-directory.
    """
    locations = [DEVELOPMENT_MASS_DIR]
    default = DEVELOPMENT_MASS_DIR
    if not _DEV:
        locations.append(PRODUCTION_MASS_DIR)
    return locations, default
