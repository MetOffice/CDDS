# (C) British Crown Copyright 2018-2021, Met Office.
# Please see LICENSE.md for license details.
"""
Tools for obtaining information on CMOR variables from the data request
"""
import logging

from cdds.data_request_interface.constants import (
    CMORVAR_ATTR_MAPPINGS, EXPERIMENT_METADATA_TO_RECORD,
    STRUCTURE_ATTR_MAPPINGS, VARIABLE_ATTR_MAPPINGS)
from cdds.data_request_interface.load import ExperimentNotFoundError
from cdds.data_request_interface.network import build_data_request_network
from cdds.data_request_interface.navigation import (
    get_cmorvar_for_experiment, get_priorities_for_variable,
    get_ensemble_sizes_for_variable)


class DataRequestVariable(object):
    """
    Class to hold useful information on a |MIP requested variable| from
    the data request
    """

    def __init__(self, data_request, uid=None, mip_table=None, var_name=None):
        """
        Construct a object representing a variable from the data
        request, either via its uid or via its |MIP| table and
        |MIP requested variable| name.

        Parameters
        ----------
        data_request : \
            :class:`cdds.data_request_interface.load.DataRequestWrapper`
            The data request object.
        uid : str, optional
            Unique ID of a |MIP requested variable|.
        mip_table : str, optional
            |MIP table| for the variable (only if uid not specified).
        var_name : str, optional
            |MIP requested variable name| (only if uid not specified).
        """
        self.data_request = data_request
        if sum([uid is not None,
                mip_table is not None and var_name is not None]) != 1:
            raise RuntimeError(
                'Either uid or mip_table and var_name must be specified')

        if uid is None:
            # If specifying variable by mip table and variable name look up
            # the unique id here and set the uid attribute.
            self._set_uid_for_variable(mip_table, var_name)
        else:
            self.uid = uid

        # Attach data request object
        self.data_request_object = self.data_request.get_object_by_uid(
            self.uid)
        # build up attributes from connected data request objects
        self._set_attributes_from_cmorvar()
        self._set_attributes_from_variable()
        self._set_attributes_from_structure()
        self._set_dimensions()
        # The following can be populated later
        self.priorities = None
        self.ensemble_sizes = None

    def _set_attributes_from_cmorvar(self):
        for name, data_request_name in CMORVAR_ATTR_MAPPINGS.items():
            setattr(self, name, _blank_to_none(
                getattr(self.data_request_object, data_request_name)))

    def _set_attributes_from_variable(self):
        variable_object = self.data_request.get_object_by_uid(
            self.data_request_object.vid)
        for name, data_request_name in VARIABLE_ATTR_MAPPINGS.items():
            setattr(self, name, _blank_to_none(
                getattr(variable_object, data_request_name)))

    def _set_attributes_from_structure(self):
        structure_object = self.data_request.get_object_by_uid(
            self.data_request_object.stid)
        for name, data_request_name in STRUCTURE_ATTR_MAPPINGS.items():
            setattr(self, name, _blank_to_none(
                getattr(structure_object, data_request_name)))

    def _set_dimensions(self):
        structure_object = self.data_request.get_object_by_uid(
            self.data_request_object.stid)
        spatial_structure_object = self.data_request.get_object_by_uid(
            structure_object.spid)
        temporal_structure_object = self.data_request.get_object_by_uid(
            structure_object.tmid)
        # Need to allow for cases such as global means where the spatial
        # structure object has no dimensions
        if spatial_structure_object.dimensions:
            self.dimensions = spatial_structure_object.dimensions.split('|')
        else:
            self.dimensions = []

        # The following is to deal with coordinate variables that have become
        # common since a change in the data request at version 01.00.09
        if float(self.data_request.version[3:7]) < 0.09:
            if structure_object.odims is not None:
                self.dimensions += structure_object.odims.split('|')
        else:
            if isinstance(structure_object.cids, tuple):
                self.dimensions += [i.replace('dim:', '')
                                    for i in structure_object.cids]
            if isinstance(structure_object.dids, tuple):
                self.dimensions += [i.replace('dim:', '')
                                    for i in structure_object.dids]
        if temporal_structure_object.dimensions:
            self.dimensions.append(temporal_structure_object.dimensions)

    def get_priorities(self, experiment_uid, network):
        """
        Construct a dictionary describing the priorities for this
        variable in the specified experiment. This dictionary is added
        to the `priorities` property

        Parameters
        ----------
        experiment_uid : str
            The unique id for the |experiment|.
        network : dict
            The network representing the data request.
        """
        self.priorities = get_priorities_for_variable(
            self.uid, experiment_uid, network)

    def get_ensemble_sizes(self, experiment_uid, network):
        """
        Construct a dictionary describing the ensemble sizes requested
        for this variable in the specified experiment. This dictionary
        is added to the `ensemble_sizes` property

        Parameters
        ----------
        experiment_uid : str
            The unique id for the |experiment|.
        network : dict
            The network representing the data request.
        """
        self.ensemble_sizes = get_ensemble_sizes_for_variable(
            self.uid, experiment_uid, network)

    def _set_uid_for_variable(self, mip_table, var_name):
        """
        Obtain the uid of the |MIP requested variable| from the data
        request corresponding to the mip_table and cmor_name attributes
        and set the `uid` property on this object.

        Parameters
        ----------
        mip_table : str
            The |MIP table|.
        var_name : str
            The |MIP requested variable name|.

        Raises
        ------
        RuntimeError
            If more than one uid is found.
        """
        uids = []
        for cmorvar in self.data_request.get_object_by_label(
                'CMORvar', var_name):
            if cmorvar.mipTable == mip_table:
                uids.append(cmorvar.uid)
        if len(uids) != 1:
            raise RuntimeError(
                'Did not find one UID for CMORvar: mip_table = "{}", '
                'var_name = "{}", uids = "{}"'
                ''.format(mip_table, var_name, repr(uids)))
        self.uid = uids[0]


def _blank_to_none(value):
    result = value
    if value == '':
        result = None
    return result


def retrieve_data_request_variables(experiment_id, data_request):
    """
    Return the list of |MIP requested variables| for the required
    |experiment| at the specified data request version.

    Parameters
    ----------
    experiment_id : str
        The |experiment identifier|.
    data_request : \
        :class:`cdds.data_request_interface.load.DataRequestWrapper`
        The |data request|.

    Returns
    -------
    : list
        Data request variables
        (:class:`cdds.data_request_interface.variables.DataRequestVariable`)
        found.
    : dict
        Metadata associated with this list of |MIP requested variables|.

    Raises
    ------
    KeyError
        If the |experiment identifier| cannot be found in the specified
        version of the |data request|.

    Notes
    -----
    Errors are logged when failures are identified when building the
    data request network. These errors occur if a data request object
    references another object which does not exist.
    """
    logger = logging.getLogger(__name__)

    logger.info('Building data request network')
    network, failures = build_data_request_network(data_request)
    if failures:
        logger.error('Failures from data request network creation: "{}"'
                     ''.format('", "'.join(failures)))
    try:
        experiment_uid = data_request.get_experiment_uid(experiment_id)
    except RuntimeError as err:
        logger.exception(err)
        raise err
    logger.info('Retrieving CMOR variables for experiment "{}", uid "{}'
                ''.format(experiment_id, experiment_uid))
    cmorvar_uids = get_cmorvar_for_experiment(experiment_uid, network)

    requested_variables = []
    for cmorvar_uid in cmorvar_uids:
        variable = DataRequestVariable(data_request, cmorvar_uid)
        variable.get_priorities(experiment_uid, network)
        variable.get_ensemble_sizes(experiment_uid, network)
        requested_variables.append(variable)

    logger.info('Found "{}" requested variables'
                ''.format(len(requested_variables)))
    experiment_obj = data_request.get_object_by_uid(experiment_uid)
    metadata = {
        'data_request_files': data_request.files_loaded,
        'data_request_version': data_request.version,
        'data_request_code_version': data_request.code_version,
        'experiment_id': experiment_id,
    }
    for obj_attr, metadata_name in EXPERIMENT_METADATA_TO_RECORD.items():
        metadata[metadata_name] = getattr(experiment_obj, obj_attr, None)

    return requested_variables, metadata


def describe_differences(variable, other_variable,
                         check_variable_comparability=True):
    """
    Return a dictionary describing the differences between this
    and another data request variable.

    Parameters
    ----------
    variable : :class:`DataRequestVariable`
        The |MIP requested variable| to compare.
    other_variable : :class:`DataRequestVariable`
        The |MIP requested variable| to compare to.
    check_variable_comparability : bool, optional
        If set to False do not raise a RuntimeError if the |MIP table|
        or |MIP requested variable| name are different in the two
        variables.

    Returns
    -------
    : dict
        The differences found organised by attribute.

    Raises
    ------
    : RuntimeError
        If an attempt is made to compare different
        |MIP requested variables|, e.g. compare ``pr`` with ``tas`` or
        |MIP requested variables| in different |mip tables| without
        explicitly setting ``check_variable_comparability`` to
        ``False``.
    """
    if (check_variable_comparability and
            (variable.mip_table != other_variable.mip_table or
             variable.variable_name != other_variable.variable_name)):
        raise RuntimeError(
            'Should not compare two completely different variables; '
            '{0.mip_table}/{0.variable_name} != '
            '{1.mip_table}/{1.variable_name}'
            ''.format(variable, other_variable))

    result = {}
    for attr in vars(variable):
        # don't compare any data_request items
        if attr.startswith('data_request'):
            continue
        self_value = getattr(variable, attr)
        other_value = getattr(other_variable, attr)
        if self_value != other_value:
            result[attr] = '"{}" -> "{}"'.format(self_value, other_value)

    return result
