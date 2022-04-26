# (C) British Crown Copyright 2018-2021, Met Office.
# Please see LICENSE.rst for license details.
"""
Tools to construct a network describing the links within the CMIP6
data request
"""
from collections import defaultdict

from hadsdk.data_request_interface.constants import (
    DATA_REQUEST_LINKAGES, IGNORED_NODE_TYPES)


class DataRequestNode(object):
    """
    A class to allow navigation through the CMIP6 data request.
    A data request node describes a particular object and its edges;
    the links between to other objects within the data request.

    Identification of a data request object is via a unique id `uid`
    property. The edges property is a dictionary recording the unique
    ids of other objects grouped by their type.
    """
    def __init__(self, data_request_object):
        """
        Initialise node from data_request_object, and pick out the
        object type, uid and initialise the edges dictionary.

        Parameters
        ----------
        data_request_object : object
            The data request object to create node for.

        Notes
        -----
        If data_request_object is set to None, then a dummy object is
        created. This is required to cope with timeSlice objects, where
        a dummy object is added to represent requests for data from all
        years of a simulation.
        """
        if data_request_object is None:
            self.data_request_object = None
            self.type = None
            self.uid = None
        else:
            self.data_request_object = data_request_object
            self.type = self._simple_data_request_object_type(
                data_request_object)
            self.uid = data_request_object.uid
        self.edges = defaultdict(list)

    def __str__(self):
        return 'Node ({}): {}'.format(self.type, str(self.data_request_object))

    def __repr__(self):
        return str(self)

    def add_edge(self, other_data_request_object):
        """
        Add an edge to this DataRequestNode pointing at the other data
        request object.

        Parameters
        ----------
        other_data_request_object : object
            Object from the data request, e.g. a requestVar or a
            requestItem.
        """
        other_data_request_object_type = self._simple_data_request_object_type(
            other_data_request_object)
        if other_data_request_object_type not in IGNORED_NODE_TYPES:
            self.edges[other_data_request_object_type].append(
                other_data_request_object.uid)

    def create_outgoing_edges_from_data_request(self, data_request):
        """
        Set up the edges dictionary for the node based on the expected
        links between objects specified in DATA_REQUEST_LINKAGES.

        Parameters
        ----------
        data_request : \
        :class:`hasdk.data_request_interface.load.DataRequestWrapper`
            Data request object.
        """
        for att in DATA_REQUEST_LINKAGES[self.type]:
            if self.data_request_object.hasattr(att):
                target_object = data_request.get_object_by_uid(
                    getattr(self.data_request_object, att))
                self.add_edge(target_object)

    def update_incoming_edges_from_network(self, network):
        """
        Update the edges on _other_ nodes in the network dictionary
        based on the information in the edges property of this node.

        Parameters
        ----------
        network : dict
            Network dictionary to update.
        """
        failures = []
        for target_uids in list(self.edges.values()):
            for target_uid in target_uids:
                try:
                    target_node = network[target_uid]
                except KeyError:
                    failures.append('Cound not find node with uid "{}" in '
                                    'network'.format(target_uid))
                    continue
                if self.uid not in target_node.edges[self.type]:
                    target_node.edges[self.type].append(self.uid)
        return failures

    @staticmethod
    def _simple_data_request_object_type(data_request_object):
        return data_request_object.__class__.__name__.split("_")[-1]


def build_data_request_network(data_request):
    """
    Build the data request network dictionary from the data request,
    controlled by the information in DATA_REQUEST_LINKAGES.

    Parameters
    ----------
    data_request : :class:`hadsdk.data_request_tools.load.DataRequestWrapper`
        The top level data request object.

    Returns
    -------
    dict
        The network representing the data request.
    list
        A list of failure messages.
    """
    network = {}
    # go through each section (node type) and add entries to the network
    # dictionary for each node
    for node_type in DATA_REQUEST_LINKAGES:
        # Pick up the uid dictionary for the node type,
        node_type_dict = data_request.get_object_dictionary(node_type)
        for uid, data_request_object in node_type_dict.items():
            # Build a node, add outgoing edges and insert into network
            # dictionary
            node = DataRequestNode(data_request_object)
            node.create_outgoing_edges_from_data_request(data_request)
            network[uid] = node
    # Only some requestItem objects have timeSlice (tslice property)
    # information on them. Rather than deal with this constantly insert
    # one dummy node to act as the timeSlice for "all years"
    _add_dummy_timeslice(network)

    # Create inverse links, i.e where a requestVar points to a requestVarGroup
    # ensure that the requestVarGroup has a link to every requestVar object.
    # Depending on the version of the data request it is possible for target
    # objects to be missing from the data request. These are reported in the
    # failures list.
    failures = []
    for node in list(network.values()):
        node_failures = node.update_incoming_edges_from_network(network)
        failures += node_failures
    return network, failures


def _add_dummy_timeslice(network):
    """
    Construct a dummy node representing a timeSlice covering all
    years in an experiment and add it to the network dictionary.
    Link all requestItem nodes without a tslice property to the
    dummy node.

    Parameters
    ----------
    network : dict
        Network dictionary.
    """
    timeslice_all_years = DataRequestNode(None)
    timeslice_all_years.type = 'timeSlice'
    timeslice_all_years.uid = '_slice_all_years'
    network[timeslice_all_years.uid] = timeslice_all_years
    # Link up every requestItem to this dummy object if they do not
    # already have a link to a timeSlice.
    for node in list(network.values()):
        if node.type == 'requestItem':
            if 'timeSlice' not in node.edges:
                node.edges['timeSlice'] = ['_slice_all_years']
