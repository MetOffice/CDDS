# (C) British Crown Copyright 2018-2023, Met Office.
# Please see LICENSE.rst for license details.
"""
Tools to navigate the network representing the data request.

Note that in these tools the term `cmorvar` is used to reflect the
`CMORvar` objects within the data request. In the rest of CDDS we use
the term |MIP requested variable| for this same concept.

The `MIP Variable` term used within the data request refers to an
object that may be quite different in different |MIP tables|, e.g. the
`MIP Variable for `ta` appears in 18 different |MIP tables| with
different sampling, averaging and spatial shapes.
"""
import warnings

from typing import Dict, Set, List

from cdds.prepare.data_request_interface.network import DataRequestNode


MAX_ENSEMBLE_SIZE = 1000
# Routes for walking the data request.
WALK_ROUTE_MAIN = ['CMORvar', 'requestVar', 'requestVarGroup', 'requestLink', 'requestItem']
WALK_ROUTE_A = WALK_ROUTE_MAIN + ['mip', 'experiment']
WALK_ROUTE_B = WALK_ROUTE_MAIN + ['exptgroup', 'experiment']
WALK_ROUTE_C = WALK_ROUTE_MAIN + ['experiment']


def get_cmorvar_for_experiment(experiment_uid: str, network: Dict[str, DataRequestNode]) -> Set[str]:
    """
    Return the set of CMOR variables for the experiment.

    :param experiment_uid: The uid of the experiment.
    :type experiment_uid: str
    :param network: The network representing the data request.
    :type network: Dict[str, DataRequestNode]
    :return: Unique ids (uids) for the corresponding CMORvar objects in the data request.
    :rtype: Set[str]
    """
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        uids = experiment_to_something(experiment_uid, 'CMORvar', network)
    return uids


def experiment_to_something(experiment_uid: str, something_type: str, network: Dict[str, DataRequestNode]) -> Set[str]:
    """
    Navigate the data request from |experiment| to an object of a specified type.

    :param experiment_uid: uid of the |experiment|
    :type experiment_uid: str
    :param something_type: type of object required
    :type something_type: str
    :param network: The network representing the data request
    :type network: Dict[str, DataRequestNode]
    :return:
    :rtype: Set[str]
    """
    result_set = set()
    for route in [WALK_ROUTE_A, WALK_ROUTE_B, WALK_ROUTE_C]:
        route = route[::-1]
        if something_type not in route:
            continue
        last_index = route.index(something_type)
        route = route[1:last_index + 1]
        route_set = walk_network([experiment_uid], route, network)
        result_set = result_set.union(route_set)
    return result_set


def walk_network(starting_uids: List[str], steps: List[str], network: Dict[str, DataRequestNode]) -> Set[str]:
    """
    Walk a route through the network from starting_uids, taking a step to nodes of the specified types in turn.

    :param starting_uids: uids to start stepping from
    :type starting_uids: List[str]
    :param steps: steps to take
    :type steps: List[str]
    :param network: The network representing the data request
    :type network: Dict[str, DataRequestNode]
    :return: The set of uids reached after taking the steps
    :rtype: Set[str]
    """
    working_uids = starting_uids
    for step in steps:
        working_uids = step_through_network_from_nodes(working_uids, network, step)
    return working_uids


def step_through_network_from_nodes(source_uids: List[str], network: Dict[str, DataRequestNode],
                                    node_type: str) -> Set[str]:
    """
    Return the set of nodes that can be reached starting from the set source_ids following an edge to
    an object of type "node_type".

    :param source_uids: The list of uids for nodes to start from
    :type source_uids: List[str]
    :param network: The network representing the data request
    :type network: Dict[str, DataRequestNode]
    :param node_type: The type of node you want to get to
    :type node_type: str
    :return: Of uids for desired node types known in the network
    :rtype: Set[str]
    """
    wrong_instance_msg = 'Expecting a set or list of source_uids, received type "{}": "{}"'
    not_all_in_network = 'Not all source_uids in network: \nsource_uids: "{}"'
    # TODO: why do we check for set? We always call the method with a list!
    assert isinstance(source_uids, (set, list)), wrong_instance_msg.format(type(source_uids), repr(source_uids))
    assert all(i in network for i in source_uids), not_all_in_network.format(repr(source_uids))

    return_ids = set()
    for i in source_uids:
        node = network[i]
        if node_type not in node.edges:
            warnings.warn('Node does not have any edges of type {}: {} ({})'.format(node_type, node, node.uid))
            continue
        for j in node.edges[node_type]:
            return_ids.add(j)
    return return_ids
