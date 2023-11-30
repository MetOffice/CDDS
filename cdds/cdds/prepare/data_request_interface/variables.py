# (C) British Crown Copyright 2018-2023, Met Office.
# Please see LICENSE.rst for license details.
import logging

from typing import Dict, Tuple, List

from cdds.data_request_interface.navigation import (get_cmorvar_for_experiment, get_priorities_for_variable,
                                                    get_ensemble_sizes_for_variable)
from cdds.prepare.data_request_interface.data_request_wrapper import DataRequestWrapper
from cdds.prepare.data_request_interface.network import build_data_request_network, DataRequestNode


# Metadata to record in 'retrieve_data_request_variables'.
# {data request property name: key to record information under}
EXPERIMENT_METADATA_TO_RECORD = {
    'description': 'experiment description',
    'endy': 'end year',
    'ensz': 'ensemble size',
    'mip': 'mip',
    'nstart': 'number of start dates',
    'starty': 'start year',
    'tier': 'tier',
    'title': 'experiment title',
    'uid': 'experiment_uid',
    'yps': 'years per start',
}

CMORVAR_ATTR_MAPPINGS = {
    'comment': 'description',
    'variable_name': 'label',
    'default_priority': 'defaultPriority',
    'frequency': 'frequency',
    'long_name': 'title',
    'mip_table': 'mipTable',
    'modeling_realm': 'modeling_realm',
    'positive': 'positive',
    'type': 'type',
    'vid': 'vid',
}

STRUCTURE_ATTR_MAPPINGS = {
    'cell_measures': 'cell_measures',
    'cell_methods': 'cell_methods',
}
VARIABLE_ATTR_MAPPINGS = {
    'output_variable_name': 'label',
    'description': 'description',
    'standard_name': 'sn',
    'units': 'units',
}


class DataRequestVariable(object):
    """
    Class to hold useful information on a |MIP requested variable| from the data request
    """

    def __init__(self, data_request: DataRequestWrapper, uid: str = None,
                 mip_table: str = None, var_name: str = None) -> None:
        """
        Construct a object representing a variable from the data request, either via
        its uid or via its |MIP| table and |MIP requested variable| name.

        :param data_request:
        :type data_request: DataRequestWrapper
        :param uid: Unique ID of a |MIP requested variable|. (Optional)
        :type uid: str
        :param mip_table: |MIP table| for the variable (only if uid not specified).
        :type mip_table: str
        :param var_name: |MIP requested variable name| (only if uid not specified).
        :type var_name: str
        """
        self.data_request = data_request
        if sum([uid is not None, mip_table is not None and var_name is not None]) != 1:
            raise RuntimeError('Either uid or mip_table and var_name must be specified')

        if uid is None:
            # If specifying variable by mip table and variable name look up
            # the unique id here and set the uid attribute.
            self._set_uid_for_variable(mip_table, var_name)
        else:
            self.uid = uid

        # Attach data request object
        self.data_request_object = self.data_request.get_object_by_uid(self.uid)
        # build up attributes from connected data request objects
        self._set_attributes_from_cmorvar()
        self._set_attributes_from_variable()
        self._set_attributes_from_structure()
        self._set_dimensions()
        # The following can be populated later
        self.priorities = None
        self.ensemble_sizes = None

    def _set_attributes_from_cmorvar(self) -> None:
        for name, data_request_name in CMORVAR_ATTR_MAPPINGS.items():
            setattr(self, name, _blank_to_none(getattr(self.data_request_object, data_request_name)))

    def _set_attributes_from_variable(self) -> None:
        variable_object = self.data_request.get_object_by_uid(self.data_request_object.vid)
        for name, data_request_name in VARIABLE_ATTR_MAPPINGS.items():
            setattr(self, name, _blank_to_none(getattr(variable_object, data_request_name)))

    def _set_attributes_from_structure(self) -> None:
        structure_object = self.data_request.get_object_by_uid(self.data_request_object.stid)
        for name, data_request_name in STRUCTURE_ATTR_MAPPINGS.items():
            setattr(self, name, _blank_to_none(getattr(structure_object, data_request_name)))

    def _set_dimensions(self) -> None:
        structure_object = self.data_request.get_object_by_uid(self.data_request_object.stid)
        spatial_structure_object = self.data_request.get_object_by_uid(structure_object.spid)
        temporal_structure_object = self.data_request.get_object_by_uid(structure_object.tmid)
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
                self.dimensions += [i.replace('dim:', '') for i in structure_object.cids]
            if isinstance(structure_object.dids, tuple):
                self.dimensions += [i.replace('dim:', '') for i in structure_object.dids]

        if temporal_structure_object.dimensions:
            self.dimensions.append(temporal_structure_object.dimensions)

    def get_priorities(self, experiment_uid: str, network: Dict[str, DataRequestNode]) -> None:
        """
        Construct a dictionary describing the priorities for this variable in the specified experiment.
        This dictionary is added to the `priorities` property

        :param experiment_uid: The unique id for the |experiment|.
        :type experiment_uid: str
        :param network: The network representing the data request.
        :type network: Dict[str, DataRequestNode]
        """
        self.priorities = get_priorities_for_variable(self.uid, experiment_uid, network)

    def get_ensemble_sizes(self, experiment_uid: str, network: Dict[str, DataRequestNode]) -> None:
        """
        Construct a dictionary describing the ensemble sizes requested for this variable in the
        specified experiment. This dictionary is added to the `ensemble_sizes` property

        :param experiment_uid: The unique id for the |experiment|.
        :type experiment_uid: str
        :param network: The network representing the data request.
        :type network: Dict[str, DataRequestNode]
        """
        self.ensemble_sizes = get_ensemble_sizes_for_variable(self.uid, experiment_uid, network)

    def _set_uid_for_variable(self, mip_table: str, var_name: str) -> None:
        """
        Obtain the uid of the |MIP requested variable| from the data request corresponding to
        the mip_table and cmor_name attributes and set the `uid` property on this object.

        :param mip_table: The |MIP table|.
        :type mip_table: str
        :param var_name: The |MIP requested variable name|.
        :type var_name: str
        """
        uids = []
        for cmorvar in self.data_request.get_object_by_label('CMORvar', var_name):
            if cmorvar.mipTable == mip_table:
                uids.append(cmorvar.uid)
        if len(uids) != 1:
            error_msg = 'Did not find one UID for CMORvar: mip_table = "{}", var_name = "{}", uids = "{}"'
            raise RuntimeError(error_msg.format(mip_table, var_name, repr(uids)))
        self.uid = uids[0]


def _blank_to_none(value: str) -> None:
    result = value
    if value == '':
        result = None
    return result


def retrieve_data_request_variables(
        experiment_id: str, data_request: DataRequestWrapper) -> Tuple[List[DataRequestVariable], Dict[str, str]]:
    """
    Return the list of |MIP requested variables| for the required |experiment| at
    the specified data request version.

    *Note:*
    Errors are logged when failures are identified when building the data request network.
    These errors occur if a data request object references another object which does not exist.

    :param experiment_id: The |experiment identifier|.
    :type experiment_id: str
    :param data_request: The |data request|.
    :type data_request: DataRequestWrapper
    :return: Data request variables, Metadata associated with this list of |MIP requested variables|.
    :rtype: Tuple[List[DataRequestVariable], Dict[str, str]]
    """
    logger = logging.getLogger(__name__)

    logger.info('Building data request network')
    network, failures = build_data_request_network(data_request)
    if failures:
        logger.error('Failures from data request network creation: "{}"'.format('", "'.join(failures)))
    try:
        experiment_uid = data_request.get_experiment_uid(experiment_id)
    except RuntimeError as err:
        logger.exception(err)
        raise err

    logger.info('Retrieving CMOR variables for experiment "{}", uid "{}'.format(experiment_id, experiment_uid))
    cmorvar_uids = get_cmorvar_for_experiment(experiment_uid, network)

    requested_variables = []
    for cmorvar_uid in cmorvar_uids:
        variable = DataRequestVariable(data_request, cmorvar_uid)
        variable.get_priorities(experiment_uid, network)
        variable.get_ensemble_sizes(experiment_uid, network)
        requested_variables.append(variable)

    logger.info('Found "{}" requested variables'.format(len(requested_variables)))
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


def describe_differences(
        variable: DataRequestVariable, other_variable: DataRequestVariable, check_variable_comparability: bool = True
) -> Dict[str, str]:
    """
    Return a dictionary describing the differences between this and another data request variable.

    :param variable: The |MIP requested variable| to compare.
    :type variable: DataRequestVariable
    :param other_variable: The |MIP requested variable| to compare to.
    :type other_variable: DataRequestVariable
    :param check_variable_comparability: If set to False do not raise a RuntimeError if the |MIP table|
        or |MIP requested variable| name are different in the two variables.
    :type check_variable_comparability: bool
    :return: The differences found organised by attribute.
    :rtype: Dict[str, str]
    """
    if check_variable_comparability:
        if variable.mip_table != other_variable.mip_table or variable.variable_name != other_variable.variable_name:
            error_msg = ('Should not compare two completely different variables;'
                         '{0.mip_table}/{0.variable_name} != {1.mip_table}/{1.variable_name}')
            raise RuntimeError(error_msg.format(variable, other_variable))

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
