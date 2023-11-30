# (C) British Crown Copyright 2018-2023, Met Office.
# Please see LICENSE.rst for license details.
"""
Tools to construct a network describing the links within the project data request, e.g. CMIP6 data request
"""
from collections import defaultdict
from typing import Dict, List, Tuple

from cdds.prepare.data_request_interface.data_request_wrapper import DataRequestWrapper


# Remarks objects appear in various places, presumably as place holders.
# These must be ignored.
IGNORED_NODE_TYPES = ['remarks']


# The 'DATA_REQUEST_LINKAGES' dictionary connects the data request object types with the properties
# they have that links them to other data request objects. This is used to build the network of DreqNodes.
DATA_REQUEST_LINKAGES = {
    'experiment': ['egid', 'mip'],
    'exptgroup': [],
    'mip': [],
    'requestItem': ['esid', 'rlid', 'tslice'],
    'timeSlice': [],
    'requestLink': ['refid'],
    'requestVarGroup': [],
    'requestVar': ['vid', 'vgid'],
    'CMORvar': [],
}


class DataRequestNode(object):
    """
    A class to allow navigation through the CMIP6 data request.
    A data request node describes a particular object and its edges; the links between to other objects
    within the data request.

    Identification of a data request object is via a unique id `uid` property.
    The edges property is a dictionary recording the unique ids of other objects grouped by their type.
    """
    def __init__(self, data_request_object: object) -> None:
        """
        Initialise node from data_request_object, and pick out the object type, uid and
        initialise the edges dictionary.

        *Note:* If data_request_object is set to None, then a dummy object is created.
        This is required to cope with timeSlice objects, where a dummy object is added
        to represent requests for data from all years of a simulation.

        :param data_request_object: The data request object to create node for.
        :type data_request_object: object
        """
        if data_request_object is None:
            self.data_request_object = None
            self.type = None
            self.uid = None
        else:
            self.data_request_object = data_request_object
            self.type = self._simple_data_request_object_type(data_request_object)
            self.uid = data_request_object.uid
        self.edges = defaultdict(list)

    def __str__(self):
        return 'Node ({}): {}'.format(self.type, str(self.data_request_object))

    def __repr__(self):
        return str(self)

    def add_edge(self, other_data_request_object: object) -> None:
        """
        Add an edge to this DataRequestNode pointing at the other data request object.

        :param other_data_request_object: Object from the data request, e.g. a requestVar or a
            requestItem.
        :type other_data_request_object: object
        """
        other_data_request_object_type = self._simple_data_request_object_type(other_data_request_object)
        if other_data_request_object_type not in IGNORED_NODE_TYPES:
            self.edges[other_data_request_object_type].append(other_data_request_object.uid)

    def create_outgoing_edges_from_data_request(self, data_request: DataRequestWrapper) -> None:
        """
        Set up the edges dictionary for the node based on the expected links between objects specified
        in DATA_REQUEST_LINKAGES.

        :param data_request: Data request object.
        :type data_request: DataRequestWrapper
        """
        for att in DATA_REQUEST_LINKAGES[self.type]:
            if self.data_request_object.hasattr(att):
                target_object = data_request.get_object_by_uid(getattr(self.data_request_object, att))
                self.add_edge(target_object)

    def update_incoming_edges_from_network(self, network: Dict[str, 'DataRequestNode']) -> List[str]:
        """
        Update the edges on _other_ nodes in the network dictionary based on the information
        in the edges property of this node.

        :param network: Network dictionary to update.
        :type network: dict
        :return: A list of failure messages.
        :rtype: List[str]
        """
        failures = []
        for target_uids in list(self.edges.values()):
            for target_uid in target_uids:
                try:
                    target_node = network[target_uid]
                except KeyError:
                    failures.append('Cound not find node with uid "{}" in network'.format(target_uid))
                    continue
                if self.uid not in target_node.edges[self.type]:
                    target_node.edges[self.type].append(self.uid)
        return failures

    @staticmethod
    def _simple_data_request_object_type(data_request_object: object) -> str:
        return data_request_object.__class__.__name__.split("_")[-1]


def build_data_request_network(data_request: DataRequestWrapper) -> Tuple[Dict[str, DataRequestNode], List[str]]:
    """
    Build the data request network dictionary from the data request, controlled by
    the information in DATA_REQUEST_LINKAGES.

    :param data_request: The top level data request object.
    :type data_request: DataRequestWrapper
    :return: Tuple of the network dictionary and a list of failure messages.
    :rtype: Tuple[Dict[str, DataRequestNode], List[str]]
    """
    network = {}
    # go through each section (node type) and add entries to the network dictionary for each node
    for node_type in DATA_REQUEST_LINKAGES:
        # Pick up the uid dictionary for the node type,
        node_type_dict = data_request.get_object_dictionary(node_type)
        for uid, data_request_object in node_type_dict.items():
            # Build a node, add outgoing edges and insert into network dictionary
            node = DataRequestNode(data_request_object)
            node.create_outgoing_edges_from_data_request(data_request)
            network[uid] = node
    # Only some requestItem objects have timeSlice (tslice property) information on them. Rather than
    # deal with this constantly insert one dummy node to act as the timeSlice for "all years"
    _add_dummy_timeslice(network)

    # Create inverse links, i.e where a requestVar points to a requestVarGroup ensure that the requestVarGroup
    # has a link to every requestVar object. Depending on the version of the data request it is possible for
    # target objects to be missing from the data request. These are reported in the failures list.
    failures = []
    for node in list(network.values()):
        node_failures = node.update_incoming_edges_from_network(network)
        failures += node_failures
    return network, failures


def _add_dummy_timeslice(network: Dict[str, DataRequestNode]) -> None:
    """
    Construct a dummy node representing a timeSlice covering all years in an experiment and
    add it to the network dictionary. Link all requestItem nodes without a tslice property
    to the dummy node.

    :param network: Network dictionary
    :type network: Dict[str, DataRequestNode]
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
