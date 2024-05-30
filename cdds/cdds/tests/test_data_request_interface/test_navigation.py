# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
"""
Tests for :mod:`cdds.data_request_interface.navigation` and
:mod:`cdds.data_request_interface.network`
"""
from copy import deepcopy
import unittest
import warnings

from cdds.data_request_interface.network import (
    DataRequestNode, DATA_REQUEST_LINKAGES, IGNORED_NODE_TYPES)
from cdds.data_request_interface.navigation import (
    MAX_ENSEMBLE_SIZE, get_cmorvar_for_experiment,
    get_ensemble_sizes_for_variable, get_experiments_for_cmorvar,
    get_priorities_for_variable, get_timeslice_for_cmorvar_experiment)

DUMMY_NETWORK = {
    'CMORvar': [
        {'uid': 'var1'}
    ],
    'requestVar': [
        {'uid': 'rva1a', 'vid': 'var1', 'vgid': 'rvga', 'priority': 3},
        {'uid': 'rva1b', 'vid': 'var1', 'vgid': 'rvgb', 'priority': 1},
        {'uid': 'rva1c', 'vid': 'var1', 'vgid': 'rvgc', 'priority': 2},
    ],
    'requestVarGroup': [
        {'uid': 'rvga'},
        {'uid': 'rvgb'},
        {'uid': 'rvgc'},
    ],
    'requestLink': [
        {'uid': 'rla', 'refid': 'rvga', 'mip': 'MIP1'},
        {'uid': 'rlb', 'refid': 'rvgb', 'mip': 'MIP2'},
        {'uid': 'rlc', 'refid': 'rvgc', 'mip': 'MIP3'},
    ],
    # Note that 'nenmax' = -1 is use in the data request to indicate that
    # the variables linked are wanted from *all* ensemble members
    'requestItem': [
        {'uid': 'ria', 'rlid': 'rla', 'esid': 'expt', 'nenmax': -1,
         'tslice': 'tslice1', 'mip': 'MIP1'},
        {'uid': 'rib', 'rlid': 'rlb', 'esid': 'eg2', 'nenmax': 1,
         'mip': 'MIP2'},
        {'uid': 'ric', 'rlid': 'rlc', 'esid': 'MIP3', 'nenmax': 2,
         'mip': 'MIP3'},
    ],
    'timeSlice': [{'uid': 'tslice1'}],
    'mip': [{'uid': 'MIP1'}, {'uid': 'MIP2'}, {'uid': 'MIP3'}],
    'exptgroup': [{'uid': 'eg2'}],
    'experiment': [
        {'uid': 'expt', 'mip': 'MIP3', 'egid': 'eg2'},
    ]
}
ADDITIONAL_NETWORK_OBJECTS = {
    # Adding this request variable should change the priority at which the
    # variable is wanted by MIP3 from 2 to 1
    'requestVar': [
        {'uid': 'rva1d', 'vid': 'var1', 'vgid': 'rvgd', 'priority': 1},
    ],
    'requestVarGroup': [
        {'uid': 'rvgd'},
    ],
    'requestLink': [
        {'uid': 'rld', 'refid': 'rvgd', 'mip': 'MIP3'},
    ],
    # Adding this request item should change the number of ensemble
    # members requested by MIP3 from 2 to 4
    'requestItem': [
        {'uid': 'rid', 'rlid': 'rld', 'esid': 'MIP3', 'nenmax': 4,
         'mip': 'MIP3'},
    ],
}


def target_type(object_id):
    """
    Return the type of dummy data request object

    Parameters
    ----------
    object_id : str
        Object id (from DUMMY_NETWORK

    Returns
    -------
    : str
        Object type
    """
    object_types = {
        'var': 'CMORvar', 'rva': 'requestVar', 'rvg': 'requestVarGroup',
        'rl': 'requestLink', 'ri': 'requestItem', 'tslice': 'timeSlice',
        'MIP': 'mip', 'eg': 'exptgroup', 'ex': 'experiment'}

    for prefix, data_request_object_type in list(object_types.items()):
        if object_id.startswith(prefix):
            return data_request_object_type


def _dummy_object_type(x):
    return x.type


class DummyDataRequestObject(object):
    def __init__(self, objtype, properties):
        self.type = objtype
        for attrib, value in list(properties.items()):
            setattr(self, attrib, value)


class DummyDataRequestNode(DataRequestNode):

    def __init__(self, data_request_object):
        super(DummyDataRequestNode, self).__init__(data_request_object)

    def add_edge(self, other_data_request):
        other_data_request_type = self._simple_data_request_object_type(other_data_request)
        if other_data_request_type not in IGNORED_NODE_TYPES:
            self.edges[other_data_request_type].append(other_data_request.uid)

    @staticmethod
    def _simple_data_request_object_type(data_request_object):
        return _dummy_object_type(data_request_object)


def build_dummy_network(network_items):
    """
    Return a dummy data request network built from the information in
    DUMMY_NETWORK.

    Parameters
    ----------
    network_items : dict
        Information needed to build a dummy network

    Returns
    -------
    : dict
        Dictionary describing the network.
    """
    # create empty network
    dummy_network = {}

    # go through entries in network_items and build network
    for node_type, descriptions in list(network_items.items()):
        for node_description in descriptions:
            # create a data request node
            node = DummyDataRequestNode(None)
            # set the type, data_request_object and uid
            node.type = node_type
            node.data_request_object = DummyDataRequestObject(
                node_type, node_description)
            node.uid = node_description['uid']
            # build the outgoing links (would be done by
            # DreqNode.create_outgoing_edges_from_data_request)
            for link_type in DATA_REQUEST_LINKAGES[node_type]:
                if link_type in node_description:
                    target_uid = node_description[link_type]
                    node.edges[target_type(target_uid)].append(target_uid)
            # add to network
            dummy_network[node.uid] = node

    # update incoming edges:
    for node in list(dummy_network.values()):
        node.update_incoming_edges_from_network(dummy_network)

    return dummy_network


class TestNavigation(unittest.TestCase):
    def setUp(self):
        self.network = build_dummy_network(DUMMY_NETWORK)
        # build a second network with additional routes through for MIP3.
        dummy_network_2 = deepcopy(DUMMY_NETWORK)
        for node_type, entries in list(ADDITIONAL_NETWORK_OBJECTS.items()):
            dummy_network_2[node_type] += entries
        self.network_2 = build_dummy_network(dummy_network_2)

    def test_get_var_for_experiment(self):
        result = get_cmorvar_for_experiment('expt', self.network)
        expected = {'var1'}
        self.assertEqual(result, expected)

    def test_get_experiment_for_var(self):
        result = get_experiments_for_cmorvar('var1', self.network)
        expected = {'expt'}
        self.assertEqual(result, expected)

    def test_get_priorities(self):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            result = get_priorities_for_variable(
                'var1', 'expt', self.network)
        expected = {'MIP1': 3, 'MIP2': 1, 'MIP3': 2}
        self.assertEqual(result, expected)

    def test_get_priorities_with_multiple_mip3_routes(self):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            result = get_priorities_for_variable(
                'var1', 'expt', self.network_2)
        expected = {'MIP1': 3, 'MIP2': 1, 'MIP3': 1}
        self.assertEqual(result, expected)

    def test_get_ensemble_sizes(self):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            result = get_ensemble_sizes_for_variable(
                'var1', 'expt', self.network)
        expected = {'MIP1': MAX_ENSEMBLE_SIZE, 'MIP2': 1, 'MIP3': 2}
        self.assertEqual(result, expected)

    def test_get_ensemble_sizes_with_multiple_mip3_routes(self):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            result = get_ensemble_sizes_for_variable(
                'var1', 'expt', self.network_2)
        expected = {'MIP1': MAX_ENSEMBLE_SIZE, 'MIP2': 1, 'MIP3': 4}
        self.assertEqual(result, expected)

    def test_timeslice(self):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            result = get_timeslice_for_cmorvar_experiment(
                'var1', 'expt', self.network)
        # Only MIP1 has a timeslice, attached to requestItem `ria`
        expected = {'MIP1': ['tslice1'], 'MIP2': [], 'MIP3': []}
        self.assertEqual(result, expected)


class TestDreqNode(unittest.TestCase):
    def setUp(self):
        self.network = build_dummy_network(DUMMY_NETWORK)

    def test_add_edge(self):
        node = DummyDataRequestNode(None)
        dummy_object = DummyDataRequestObject('thing', {'uid': 'random'})
        node.add_edge(dummy_object)
        expected_edges = {'thing': [dummy_object.uid]}
        self.assertDictEqual(expected_edges, node.edges)

    def test_update_incoming_edges_from_network(self):
        # Pick a node; request variable with uid = `rva1a`
        node = self.network['rva1a']
        # Clear out the edges dictionary in all nodes in the network
        # other than our chosen one
        other_uids = list(self.network.keys())
        other_uids.remove(node.uid)
        for other_uid in other_uids:
            other_node = self.network[other_uid]
            edge_types_to_remove = list(other_node.edges.keys())
            for edge_type in edge_types_to_remove:
                del other_node.edges[edge_type]

        # Nodes that we know rva1a links to ('vid' and 'vgid' properties)
        cmorvar_node = self.network['var1']
        rvg_node = self.network['rvga']
        # Confirm they have no links before we update them
        self.assertDictEqual(cmorvar_node.edges, {})
        self.assertDictEqual(rvg_node.edges, {})
        # update the network with information in this node
        node.update_incoming_edges_from_network(self.network)
        # Confirm that the links point at our node
        self.assertDictEqual(cmorvar_node.edges, {'requestVar': ['rva1a']})
        self.assertDictEqual(rvg_node.edges, {'requestVar': ['rva1a']})

    def test_create_outgoing_edges_from_data_request(self):
        # This cannot be tested without a mocked up data request
        pass


if __name__ == '__main__':
    unittest.main()
