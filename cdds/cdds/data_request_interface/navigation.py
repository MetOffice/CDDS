# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
"""
Tools to navigate the network representing the CMIP6 data request.

Note that in these tools the term `cmorvar` is used to reflect the
`CMORvar` objects within the data request. In the rest of CDDS we use
the term |MIP requested variable| for this same concept.

The `MIP Variable` term used within the data request refers to an
object that may be quite different in different |MIP tables|, e.g. the
`MIP Variable for `ta` appears in 18 different |MIP tables| with
different sampling, averaging and spatial shapes.
"""
from copy import deepcopy as copy
from collections import defaultdict
import warnings

from cdds.data_request_interface.constants import (
    MAX_ENSEMBLE_SIZE, WALK_ROUTE_A, WALK_ROUTE_B, WALK_ROUTE_C)


def step_through_network_from_nodes(source_uids, network, node_type):
    """
    Return the set of nodes that can be reached starting from the set
    source_ids following an edge to an object of type "node_type".

    Parameters
    ----------
    source_uids : set
        The set of uids for nodes to start from.
    network : dict
        The network representing the data request.
    node_type : str
        The type of node you want to get to.

    Returns
    -------
    set
        Of uids for desired node types known in the network.
    """
    assert isinstance(source_uids, (set, list)), (
        'Expecting a set or list of source_uids, received type "{}": "{}" '
        ''.format(type(source_uids), repr(source_uids)))
    assert all(i in network for i in source_uids), (
        'Not all source_uids in network: \nsource_uids: "{}"'
        '').format(repr(source_uids))
    return_ids = set()
    for i in source_uids:
        node = network[i]
        if node_type not in node.edges:
            warnings.warn(
                'Node does not have any edges of type {}: {} ({})'
                ''.format(node_type, node, node.uid))
            continue
        for j in node.edges[node_type]:
            return_ids.add(j)
    return return_ids


def get_cmorvar_for_experiment(experiment_uid, network):
    """
    Return the set of CMOR variables for the experiment.

    Parameters
    ----------
    experiment_uid : str
        The uid of the experiment.
    network : dict
        The network representing the data request.

    Returns
    -------
    set
        Unique ids (uids) for the corresponding CMORvar objects in the
        data request.
    """
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        uids = experiment_to_something(experiment_uid, 'CMORvar', network)

    return uids


def get_experiments_for_cmorvar(cmorvar_uid, network):
    """
    Return the set of experiment uids for the specified CMOR variable.

    Parameters
    ----------
    cmorvar_uid : str
        The uid of the CMOR variable.
    network : dict
        The network representing the data request.

    Returns
    -------
    set
        Unique ids (uids) for the corresponding experiment objects in
        the data request.
    """
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        uids = cmorvar_to_something(cmorvar_uid, 'experiment', network)

    return uids


def get_priorities_for_variable(cmorvar_uid, experiment_uid, network):
    """
    Return the priority for a particular experiment, cmor variable
    combination for each requesting |MIP|. This involves walking to the
    requestVar objects (from both experiment and CMORvar) and picking
    up the priority for each requesting |MIP|.

    Parameters
    ----------
    cmorvar_uid : str
        The uid of the CMOR variable to obtain the time slices for.
    experiment_uid : str
        The uid of the experiment.
    network : dict
        The network representing the data request.

    Returns
    -------
    dict
        Entries for |MIP|: priority.
    """
    subnetwork = subset_network_for_cmorvar_experiment(cmorvar_uid,
                                                       experiment_uid,
                                                       network)
    requestvars = [i.uid for i in list(subnetwork.values())
                   if i.type == 'requestVar']
    priorities = {}
    for rv in requestvars:
        rv_request_links = walk_network([rv],
                                        ['requestVarGroup', 'requestLink'],
                                        subnetwork)
        rv_request_items = walk_network(rv_request_links, ['requestItem'],
                                        subnetwork)
        mips = set([subnetwork[i].data_request_object.mip for i in
                    rv_request_links.union(rv_request_items)])
        priority = network[rv].data_request_object.priority
        for m in mips:
            if m in priorities:
                priorities[m] = min(priority, priorities[m])
            else:
                priorities[m] = priority

    return priorities


def get_ensemble_sizes_for_variable(cmorvar_uid, experiment_uid, network):
    """
    Return the number of ensemble members a variable is requested for
    from particular |experiment| for each requesting |MIP|. This
    information is extracted from the `nensmax` attribute of the
    requestItems that link the CMORvar and |experiment| objects.
    Note that if the data request records `nensmax` as `-1` then the
    value in MAX_ENSEMBLE_SIZE will be used.

    Parameters
    ----------
    cmorvar_uid : str
        The uid of the CMOR variable to obtain the time slices for.
    experiment_uid : str
        The uid of the |experiment|.
    network : dict
        The network representing the data request.

    Returns
    -------
    dict
        Entries for |MIP|: num of ensemble members requested.
    """
    subnetwork = subset_network_for_cmorvar_experiment(
        cmorvar_uid, experiment_uid, network)
    requestitems = [i.uid for i in list(subnetwork.values())
                    if i.type == 'requestItem']
    nensemble_members = {}
    for ri in requestitems:
        ri_obj = network[ri].data_request_object
        if ri_obj.nenmax == -1:
            nensemble_members[ri_obj.mip] = MAX_ENSEMBLE_SIZE
        else:
            # Allow for VIACSAB where different communities may have separate
            # requests for ensemble size. Just pick the largest number
            # requested
            if ri_obj.mip in nensemble_members:
                nensemble_members[ri_obj.mip] = max(
                    ri_obj.nenmax, nensemble_members[ri_obj.mip])
            else:
                nensemble_members[ri_obj.mip] = ri_obj.nenmax

    return nensemble_members


def get_timeslice_for_cmorvar_experiment(cmorvar_uid, experiment_uid,
                                         network):
    """
    Obtain the timeslices corresponding to a particular variable,
    |experiment| combination by |MIP|. Note that a dummy timeSlice object
    `_slice_all_years` is added to every requestItem that does not
    explicitly link to a timeSlice object.

    Parameters
    ----------
    cmorvar_uid : str
        The uid of the CMOR variable to obtain the time slices for.
    experiment_uid : str
        The uid of the |experiment|.
    network : dict
        The network representing the data request.

    Returns
    -------
    dict
        Entries for |MIP|: time slice object.
    """
    subnetwork = subset_network_for_cmorvar_experiment(cmorvar_uid,
                                                       experiment_uid,
                                                       network)
    requestitems = [i.uid for i in list(subnetwork.values())
                    if i.type == 'requestItem']
    timeslices = {}
    for ri in requestitems:
        ri_obj = network[ri].data_request_object
        timeslices[ri_obj.mip] = network[ri].edges['timeSlice']

    return timeslices


def get_rvg_for_cmorvar_experiment(cmorvar_uid, experiment_uid, network):
    """
    Obtain the uids of the request variable groups linked to a
    particular |experiment|, cmor variable combination.

    Parameters
    ----------
    cmorvar_uid : str
        The uid of the CMOR variable to obtain the time slices for.
    experiment_uid : str
        The uid of the |experiment|.
    network : dict
        The network representing the data request.

    Returns
    -------
    dict
        Entries for |MIP|: uid of corresponding request variable group.
    """
    subnetwork = subset_network_for_cmorvar_experiment(cmorvar_uid,
                                                       experiment_uid,
                                                       network)
    requestvargroups = [i.uid for i in list(subnetwork.values())
                        if i.type == 'requestVarGroup']
    rvg_dict = defaultdict(list)
    for rvg in requestvargroups:
        rvg_request_links = walk_network([rvg], ['requestLink'],
                                         subnetwork)
        rvg_request_items = walk_network(rvg_request_links, ['requestItem'],
                                         subnetwork)
        mips = set([subnetwork[i].data_request_object.mip for i in
                    rvg_request_links.union(rvg_request_items)])
        for m in mips:
            rvg_dict[m].append(rvg)

    return rvg_dict


def walk_network(starting_uids, steps, network):
    """
    Walk a route through the network from starting_uids, taking a step
    to nodes of the specified types in turn.

    Parameters
    ----------
    starting_uids : list or set
        uids to start stepping from.
    steps : list
        steps to take.
    network: dict
        The network representing the data request.

    Returns
    -------
    set
        The set of uids reached after taking the steps.
    """
    working_uids = starting_uids
    for step in steps:
        working_uids = step_through_network_from_nodes(
            working_uids, network, step)
    return working_uids


def cmorvar_to_something(cmorvar_uid, something_type, network):
    """
    Navigate the data request from cmor variable to an object of
    a specified type.

    Parameters
    ----------
    cmorvar_uid :  str
       uid of the CMOR variable.
    something_type : str
       type of object required.
    network : dict
        The network representing the data request.

    Returns
    -------
    set
        uids corresponding to data request objects linked to the cmor
        variable specified.
    """
    result_set = set()
    for route in [WALK_ROUTE_A, WALK_ROUTE_B, WALK_ROUTE_C]:
        if something_type not in route:
            continue
        last_index = route.index(something_type)
        route = route[1:last_index + 1]
        route_set = walk_network([cmorvar_uid], route, network)
        result_set = result_set.union(route_set)
    return result_set


def experiment_to_something(experiment_uid, something_type, network):
    """
    Navigate the data request from |experiment| to an object of
    a specified type.

    Parameters
    ----------
    experiment_uid :  str
        uid of the |experiment|.
    something_type : str
        type of object required.
    network : dict
        The network representing the data request.

    Returns
    -------
    set
        uids corresponding to data request objects linked to the
        |experiment| specified.
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


def describe_route(cmorvar_uid, experiment_uid, network):
    """
    Return a dictionary describing the route through the network
    between the CMORvar and |experiment|.

    Parameters
    ----------
    cmorvar_uid : str
        UID of the CMORvar acting as one end of the route.
    experiment_uid : str
        UID of the |experiment| acting as the other end of the route.
    network : dict
        The network representing the data request.

    Returns
    -------
    dict:
        Unique ids (uids) for each node type on the route.
    """
    intermediates = WALK_ROUTE_A[1:-1] + WALK_ROUTE_B[-2:-1]
    result = {'CMORvar': [cmorvar_uid],
              'experiment': [experiment_uid]}
    for stage in intermediates:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            from_cmorvar = cmorvar_to_something(cmorvar_uid, stage, network)
            from_experiment = experiment_to_something(experiment_uid, stage,
                                                      network)
            result[stage] = list(from_cmorvar.intersection(from_experiment))

    result['timeSlice'] = {}
    for request_item in result['requestItem']:
        result['timeSlice'][request_item] = list(walk_network([request_item],
                                                              ['timeSlice'],
                                                              network))
    return result


def subset_network_for_cmorvar_experiment(cmorvar_uid, experiment_uid,
                                          network):
    """
    Return a stripped down copy of the network, where only the elements
    linking the cmor variable to the |experiment| remain. Note that all
    links to timeSlices are maintained.

    Parameters
    ----------
    cmorvar_uid : str
        UID of the CMORvar acting as one end of the route.
    experiment_uid : str
        UID of the |experiment| acting as the other end of the route.
    network : dict
        The network representing the data request.

    Returns
    -------
    dict:
        Cut down network.
    """

    network_subset = {}
    route = describe_route(cmorvar_uid, experiment_uid, network)
    allowed_uids = set()
    for uids in list(route.values()):
        allowed_uids = allowed_uids.union(set(uids))

    for uid in allowed_uids:
        node_copy = copy(network[uid])
        for edge_type, edge_list in node_copy.edges.items():
            allowed_edge_uids = set(edge_list).intersection(allowed_uids)
            node_copy.edges[edge_type] = sorted(list(allowed_edge_uids))
            if edge_type == 'timeSlice':
                node_copy.edges['timeSlice'] = network[uid].edges['timeSlice']
        network_subset[uid] = node_copy

    return network_subset
