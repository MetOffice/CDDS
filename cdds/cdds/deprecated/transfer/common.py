# (C) British Crown Copyright 2018-2021, Met Office.
# Please see LICENSE.rst for license details.
"""
Routines involved multiple tools within CDDS Transfer
"""
import logging
import os

from cdds.deprecated.transfer import config, drs, state

SYSTEMS_ALLOWED_TO_SEND_MESSAGES = ['els055', 'els056']


def load_rabbit_mq_credentials(cfg):
    """
    Attempt to add credentials information from $HOME/.cdds_credentials
    to the config object. This will be aborted if an attempt is made to
    run this from a system without visibility of the RabbitMQ server
    or if permissions on the credentials file are too loose.

    Parameters
    ----------
    cfg : :class:`cdds.deprecated.transfer.config.Config`
        Config object

    Returns
    -------
    : bool
        True if successful
    """
    logger = logging.getLogger(__name__)
    if os.uname()[1] not in SYSTEMS_ALLOWED_TO_SEND_MESSAGES:
        logger.critical(
            'Only certain the following systems are allowed to send messages: '
            '"{}"'.format('", "'.join(SYSTEMS_ALLOWED_TO_SEND_MESSAGES)))
        success = False
    else:
        credentials_file = os.path.join(
            os.environ['HOME'], '.cdds_credentials')
        logger.info('Looking for Rabbit MQ credentials file at "{}"'
                    ''.format(credentials_file))
        success = False
        if os.path.exists(credentials_file):
            unix_permissions = oct(os.stat(credentials_file).st_mode)[-3:]
            if unix_permissions[1:] == '00':
                files_read = cfg._cp.read(credentials_file)
                logger.info('Read credentials file "{}"'.format(files_read))
                success = True
            else:
                logger.critical(
                    'Credentials file must only be readable by the owner')

        if not success:
            logger.info('Credentials file not read.')
    return success


def cfg_from_cdds_general_config(general_config, request, mass_location):
    """
    Return a configuration object constructed from the supplied
    CDDSGeneralConfig plus information from the request. This is a
    nasty hack, as the actual replacement of the
    config objects within cdds.deprecated.transfer will take too much work.

    Parameters
    ----------
    general_config : :class:`hadsdk.config.CDDSGeneralConfig`
        config object
    request : :class:`cdds.common.request.Request`
        Request object
    mass_location : str
        Sub directory within MASS to use for archiving. Must be either
        `PRODUCTION_MASS_DIR` or `DEVELOPMENT_MASS_DIR` from
        :mod:`cdds.deprecated.transfer.archive`.

    Returns
    -------
    : :class:`cdds.deprecated.transfer.config.Config`
        CDDS Transfer config object
    """
    logger = logging.getLogger(__name__)
    # Initialise config
    cfg = config.Config(None)
    mip_era = request.mip_era
    # Add mip_era section and insert information from the general
    # config file
    cfg._cp.add_section(mip_era)
    for field, value in general_config.transfer_facetmaps.items():
        cfg._cp.set(mip_era, field, value)
    # Add information from transfer_mass and transfer_local section
    cfg._cp.add_section('mass')
    mass_dir = os.path.join(general_config.transfer_mass_top_dir,
                            mass_location)
    logger.debug('Setting top level MASS directory to "{}"'
                 ''.format(mass_dir))
    cfg._cp.set('mass', 'top_dir', mass_dir)
    cfg._cp.add_section('local')
    cfg._cp.set('local', 'base_dir', general_config.transfer_local_base_dir)

    # The "top_dir", or root directory for data, is obtained from the request.
    # TODO: Shouldn't use non-public method :(
    cfg._cp.set('local', 'top_dir', general_config._root_data_directory)
    # The institution_id is not present anywhere in the DRS or file names.
    # As such I've chosen to copy it in here, rather than hard coding it into
    # the config files
    cfg._cp.set(mip_era, 'institution_id', request.institution_id)
    # Message store information
    cfg._cp.add_section('msg_store')
    cfg._cp.set('msg_store', 'top_dir',
                general_config.log_directory('archive'))
    return cfg


def drs_facet_builder_from_request(request, cfg):
    """
    Return the :class:`DataRefSyntax` object constructed from the
    request and config objects

    Parameters
    ----------
    request : :class:`cdds.common.request.Request`
        Request information
    cfg : :class:`cdds.deprecated.transfer.config.Config`
        CDDS Transfer config object

    Returns
    -------
    : :class:`cdds.deprecated.transfer.drs.DataRefSyntax`
        Object describing the drs fixed facets.
    """
    logger = logging.getLogger(__name__)
    drs_fixed_facet_builder = drs.DataRefSyntax(cfg, request.mip_era)
    valid_items = {}
    for field, value in request.items.items():
        if ' ' in value:
            new_value = value.split(' ')[0]
            logger.debug('Found value "{}" for facet "{}". Using "{}"'.format(value, field, new_value))
            value = new_value
        if field in drs_fixed_facet_builder._project_config['valid']:
            valid_items[field] = value
    drs_fixed_facet_builder.fill_facets_from_dict(valid_items)
    return drs_fixed_facet_builder


def log_filesets(filesets):
    """
    Log information about the file sets supplied

    Parameters
    ----------
    filesets : :class:`cdds.deprecated.transfer.drs.AtomicDatatsetCollection`
        Data sets to log about.
    """
    logger = logging.getLogger(__name__)
    logger.info('Found "{}" filesets'.format(
        sum([len(i) for i in list(filesets._atoms.values())])))
    filesets_msg = []
    for filesetid, vardict in filesets._atoms.items():
        for varname, var_drs in vardict.items():
            filesets_msg.append('{} : {} ({})\n\t"{}"'.format(
                filesetid, varname, len(var_drs._files),
                '", "'.join(var_drs._files)
            ))
    logger.info("Filesets:\n {}".format("\n".join(filesets_msg)))


def find_local(top_dir, drs_fixed_facet_builder, transfer_service):
    """
    Return an atomic dataset collection describing the available local
    data sets that match the provided facets.

    Parameters
    ----------
    top_dir : str
        Top level data directory, e.g. `/project/cdds_data`
    drs_fixed_facet_builder : :class:`cdds.deprecated.transfer.drs.DataRefSyntax`
        Object describing the facets to match against
    transfer_service : :class:`cdds.deprecated.transfer.dds.DataTransfer`
        Data transfer service.

    Returns
    -------
    : :class:`cdds.deprecated.transfer.drs.AtomicDatasetCollection`
        Object describing the file sets found in on disk which
        match the supplied facets.

    Raises
    ------
    : RuntimeError
        If no file sets are found or the local directory does not
        exist.
    """
    # Make it clear where we are looking for files
    logger = logging.getLogger(__name__)
    local_directory = transfer_service._local_path_to_facet(
        top_dir, drs_fixed_facet_builder)
    logger.info('Searching "{}" for files.'.format(local_directory))
    if not os.path.exists(local_directory):
        message = ('Local directory "{}" does not exist.'
                   '').format(local_directory)
        raise RuntimeError(message)

    local = transfer_service.find_local_facets(top_dir,
                                               drs_fixed_facet_builder)
    number_of_local_files_found = len(local.get_drs_facet_builder_list())

    if number_of_local_files_found == 0:
        raise RuntimeError('Found no files with facets matching this request.')
    else:
        logger.info('Found "{}" local files.'.format(
            number_of_local_files_found))
    return local


def find_mass(drs_fixed_facet_builder, current_state, transfer_service):
    """
    Return an atomic dataset collection describing the available data
    sets that match the provided facets and state.

    Parameters
    ----------
    drs_fixed_facet_builder : :class:`cdds.deprecated.transfer.drs.DataRefSyntax`
        Object describing the facets to match against
    current_state : str
        Current state of the files to be found, e.g. `embargoed` or
        `available`.
    transfer_service : :class:`cdds.deprecated.transfer.dds.DataTransfer`
        Data transfer service.

    Returns
    -------
    : :class:`cdds.deprecated.transfer.drs.AtomicDatasetCollection`
        Object describing the file sets found in mass which match the
        supplied facets and state.

    Raises
    ------
    : RuntimeError
        If no file sets are found.
    """
    start_state = state.make_state(current_state)
    mass = transfer_service.find_mass_facets(drs_fixed_facet_builder,
                                             start_state)
    if len(mass.get_drs_facet_builder_list()) == 0:
        raise RuntimeError('Found no matching facets')
    return mass
