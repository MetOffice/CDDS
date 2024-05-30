# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
from datetime import date
from unittest.mock import Mock, call, patch
import os
import unittest

from cdds.deprecated.transfer import dds, drs, moo, moo_cmd, msg, state
from cdds.tests.test_deprecated.test_transfer import util
from cdds.deprecated.transfer.dds import VERSION_FORMAT


def xfer_without_starting_comms(test_case, project):
    util.create_patch(test_case, "cdds.deprecated.transfer.rabbit.RabbitMqManager.start")
    cfg = util.patch_open_config(project)
    return cfg, dds.DataTransfer(cfg, project)


class TestVarDistinctness(unittest.TestCase):

    def setUp(self):
        project = "CORDEX"
        cfg, self.xfer = xfer_without_starting_comms(self, project)
        var_base = "hfls_CAS-44_ERAINT_evaluation_r1i1p1_MOHC-HadRM3P_v1"
        var = {
            "day": "%s_day_19900101-19901231.nc" % var_base,
            "mon": "%s_mon_199001-199012.nc" % var_base}
        self.facet_day = drs.DataRefSyntax(cfg, project)
        self.facet_day.fill_facets_from_drs_name(var["day"])
        self.facet_mon = drs.DataRefSyntax(cfg, project)
        self.facet_mon.fill_facets_from_drs_name(var["mon"])
        self.available = state.make_state(state.AVAILABLE)

    def test_var_name_sufficiently_distinct_on_mass(self):
        self.assertTrue(
            self.xfer._mass_path_to_state(self.facet_day, self.available) !=
            self.xfer._mass_path_to_state(self.facet_mon, self.available))

    def test_pattern_match_sufficiently_distinct_on_local(self):
        local_day_dir = self.xfer._local_path_to_facet(
            "fake_local_top", self.facet_day)
        local_match_day = self.xfer._local_path_to_match_drs_var(
            local_day_dir, self.facet_day)
        local_mon_dir = self.xfer._local_path_to_facet(
            "fake_local_top", self.facet_mon)
        local_match_mon = self.xfer._local_path_to_match_drs_var(
            local_mon_dir, self.facet_mon)
        self.assertTrue(local_match_day != local_match_mon)


class TestMoosePut(unittest.TestCase):

    def setUp(self):
        self.project = "GEOMIP"
        self.cfg, self.xfer = xfer_without_starting_comms(self, self.project)
        util.patch_mip_parser(self)
        self.mock_inform = util.create_patch(
            self, "cdds.deprecated.transfer.dds.DataTransfer.inform")
        self.ts = date.today().strftime("%Y%m%d")
        self.embargoed = state.make_state(state.EMBARGOED)
        self.available = state.make_state(state.AVAILABLE)

    def test_single_variable_put(self):
        util.create_patch(self, "cdds.deprecated.transfer.moo.run_moo_cmd")

        expected_local = os.path.join(
            "fake_local_top", "GEOMIP", "MOHC", "HadGEM2-ES",
            "G4seaSalt", "r1i1p1", "nc")
        expected_moose = os.path.join(
            self.xfer._moo_top,
            "geomip/output/MOHC/HadGEM2-ES/G4seaSalt/mon/land/Lmon/"
            "r1i1p1/c3PftFrac/embargoed/", VERSION_FORMAT.format(self.ts))

        facets = drs.AtomicDatasetCollection()
        drs_names = [
            "c3PftFrac_Lmon_HadGEM2-ES_G4seaSalt_r1i1p1_202012-204511.nc",
            "c3PftFrac_Lmon_HadGEM2-ES_G4seaSalt_r1i1p1_204512-207011.nc"]
        for drs_name in drs_names:
            facet = drs.DataRefSyntax(self.cfg, self.project)
            facet.fill_facets_from_drs_name(drs_name)
            facets.add(facet, filename=drs_name)
        expected_facet = facets.get_drs_facet_builder(
            "geomip.output.MOHC.HadGEM2-ES.G4seaSalt.mon.land.Lmon.r1i1p1",
            "c3PftFrac")

        mock_put = util.create_patch(
            self, "cdds.deprecated.transfer.dds.DataTransfer._put_atom")
        self.xfer.send_to_mass("fake_local_top", facets, self.embargoed)
        mock_put.assert_called_once_with(
            expected_facet, expected_local, expected_moose, moo_cmd.put)
        self.mock_inform.assert_called_once_with(
            expected_facet, expected_moose, self.embargoed)

    def test_several_variables_put(self):
        util.create_patch(self, "cdds.deprecated.transfer.moo.run_moo_cmd")

        var = [
            "cLeaf_Lmon_HadGEM2-ES_G4seaSalt_r1i1p1_202012-204511.nc",
            "cLeaf_Lmon_HadGEM2-ES_G4seaSalt_r1i1p1_204512-207011.nc",
            "cdnc_aero_HadGEM2-ES_G4seaSalt_r1i1p1_202012-204511.nc",
            "cdnc_aero_HadGEM2-ES_G4seaSalt_r1i1p1_204512-207011.nc"]
        facets = drs.AtomicDatasetCollection()
        for drs_name in var:
            facet = drs.DataRefSyntax(self.cfg, self.project)
            facet.fill_facets_from_drs_name(drs_name)
            facets.add(facet, filename=drs_name)

        expected_local = os.path.join(
            "fake_local_top", "GEOMIP", "MOHC", "HadGEM2-ES",
            "G4seaSalt", "r1i1p1")
        expected_puts = []
        expected_informs = []
        for dataset_id in facets.dataset_ids():
            for drs_var in facets.drs_variables(dataset_id):
                facet = facets.get_drs_facet_builder(dataset_id, drs_var)
                expected_moose = self.xfer._mass_path_to_timestamp(
                    facet, self.embargoed, self.ts)
                expected_puts.append(
                    call(
                        facet, expected_local, expected_moose,
                        facets.get_drs_facet_builder(dataset_id, drs_var),
                        expected_local, moo_cmd.put))
                expected_informs.append(
                    call(facet, expected_moose, self.embargoed))

        mock_put = util.create_patch(
            self, "cdds.deprecated.transfer.dds.DataTransfer._put_atom")
        self.xfer.send_to_mass("fake_local_top", facets, self.embargoed)
        mock_put.has_calls(expected_puts)
        self.mock_inform.has_calls(expected_informs)

    def test_valid_put_var(self):
        # Testing low-level MASS interface, so we need to patch out
        # the calls that interact with the file system or MASS.
        mock_moo = util.create_patch(self, "cdds.deprecated.transfer.moo.run_moo_cmd")
        var_file = "bsi_Omon_HadGEM2-ES_G4seaSalt_r1i1p1_202012-209012.nc"
        expected_local = [os.path.join("dir", var_file)]
        mock_glob = util.create_patch(self, "glob.glob")
        mock_glob.return_value = expected_local
        mock_size = util.create_patch(self, "os.path.getsize")
        mock_size.return_value = 0
        facet = drs.DataRefSyntax(self.cfg, self.project)
        facet.fill_facets_from_drs_name(var_file)
        self.xfer._put_var("dir", facet, "moose/path", moo_cmd.put)
        expected_arg = expected_local + ["moose/path"]
        mock_moo.assert_called_once_with("put", expected_arg,
                                         simulation=False)

    def test_put_atom_tries_to_rollback(self):
        # We need to fake the following returns from run_moo_cmd:
        #     1. a moo test for the dir should return ['false']
        #     2. moo mkdir should appear to work ok
        #     3. moo put should raise an error and finally...
        #     4. the rmdir should appear to work ok.
        self.mock_returns = [['false'], [], moo.MassError("put failed!"), []]
        mock_moo = util.mock_with_side_effects(self)
        mock_cmd = util.create_patch(
            self, "cdds.deprecated.transfer.moo.run_moo_cmd", mock_moo)
        self.patch_local_dir_exists()
        local_path = os.path.join("local", "dir")
        expected_call = [
            call("mkdir", ["-p", "moose_dir"]),
            call("put", [os.path.join(local_path, "bsi_Oyr_*"), "moose_dir"]),
            call("rmdir", ["moose_dir"])]
        facet = drs.DataRefSyntax(self.cfg, self.project)
        facet.fill_facets_from_drs_name(
            "bsi_Oyr_HadGEM2-ES_G4seaSalt_r1i1p1_2021-2090.nc")
        self.xfer._put_atom(facet, local_path, "moose_dir", moo_cmd.put)
        mock_cmd.has_calls(expected_call)

    def patch_local_dir_exists(self):
        mock_exists = util.create_patch(
            self, "cdds.deprecated.transfer.dds.DataTransfer._local_dir_exists")
        mock_exists.return_value = True
        return


class TestRerunMoosePut(unittest.TestCase):

    def setUp(self):
        self.project = "CMIP6"
        self.cfg, self.xfer = xfer_without_starting_comms(self, self.project)
        util.patch_mip_parser(self)
        self.embargoed = state.make_state(state.EMBARGOED)
        self.ts = date.today().strftime("%Y%m%d")

    def test_rerun_when_nothing_worked(self):
        self._patch_last_successful(None, None)
        mock_send = util.create_patch(
            self, "cdds.deprecated.transfer.dds.DataTransfer.send_to_mass")
        facets = self._facets(["tas_Amon_UKESM1_historical_r1i2p3"])
        self.xfer.rerun_send_to_mass(
            "fake_local", facets, self.embargoed, self.ts)
        mock_send.assert_called_once_with("fake_local", facets, self.embargoed)

    def test_made_it_to_the_end(self):
        last_id = "CMIP6.MOHC.UKESM1.rcp45.mon.atmos.Amon.r1i2p3"
        last_var = "uo"
        self._patch_last_successful(last_id, last_var)
        mock_run_put = util.create_patch(
            self, "cdds.deprecated.transfer.dds.DataTransfer._run_put")
        drs_names = [
            "tas_Amon_UKESM1_historical_r1i2p3",
            "tas_Amon_UKESM1_rcp45_r1i2p3",
            "uo_Amon_UKESM1_rcp45_r1i2p3"]
        facets = self._facets(drs_names)
        self.xfer.rerun_send_to_mass(
            "fake_local", facets, self.embargoed, self.ts)
        expected = [self._call(facets, last_id, last_var, overwrite=True)]
        mock_run_put.assert_has_calls(expected)

    def test_finishes_off_last_id(self):
        last_id = "CMIP6.MOHC.UKESM1.rcp45.mon.atmos.Amon.r1i2p3"
        last_var = "uo"
        self._patch_last_successful(last_id, last_var)
        mock_run_put = util.create_patch(
            self, "cdds.deprecated.transfer.dds.DataTransfer._run_put")
        drs_names = [
            "tas_Amon_UKESM1_rcp45_r1i2p3",
            "uo_Amon_UKESM1_rcp45_r1i2p3",
            "vo_Amon_UKESM1_rcp45_r1i2p3"]
        facets = self._facets(drs_names)
        expected_calls = [
            self._call(facets, last_id, last_var, overwrite=True),
            self._call(facets, last_id, "vo")]
        self.xfer.rerun_send_to_mass(
            "fake_local", facets, self.embargoed, self.ts)
        mock_run_put.assert_has_calls(expected_calls)

    def test_made_it_part_way(self):
        drs_names = [
            "tas_Amon_UKESM1_rcp45_r1i2p3",
            "uo_Amon_UKESM1_rcp45_r1i2p3",
            "vo_Amon_UKESM1_rcp45_r1i2p3",
            "tas_Lmon_UKESM1_rcp45_r1i2p3",
            "uo_Lmon_UKESM1_rcp45_r1i2p3",
            "vo_Lmon_UKESM1_rcp45_r1i2p3",
            "tas_Omon_UKESM1_rcp45_r1i2p3",
            "uo_Omon_UKESM1_rcp45_r1i2p3",
            "vo_Omon_UKESM1_rcp45_r1i2p3"]
        facets = self._facets(drs_names)
        last_id = "CMIP6.MOHC.UKESM1.rcp45.mon.land.Lmon.r1i2p3"
        last_var = "uo"
        ocean_id = "CMIP6.MOHC.UKESM1.rcp45.mon.ocean.Omon.r1i2p3"
        self._patch_last_successful(last_id, last_var)
        mock_run_put = util.create_patch(
            self, "cdds.deprecated.transfer.dds.DataTransfer._run_put")
        expected_calls = [
            self._call(facets, last_id, last_var, overwrite=True),
            self._call(facets, last_id, "vo"),
            self._call(facets, ocean_id, "tas"),
            self._call(facets, ocean_id, "uo"),
            self._call(facets, ocean_id, "vo")]
        self.xfer.rerun_send_to_mass(
            "fake_local", facets, self.embargoed, self.ts)
        mock_run_put.assert_has_calls(expected_calls)

    def _facets(self, drs_names):
        facets = drs.AtomicDatasetCollection()
        for drs_name in drs_names:
            facet = drs.DataRefSyntax(self.cfg, self.project)
            facet.fill_facets_from_drs_name(drs_name)
            facets.add(facet, filename=drs_name)
        return facets

    def _patch_last_successful(self, last_id, last_var):
        mock_last_successful = util.create_patch(
            self, "cdds.deprecated.transfer.dds.DataTransfer._find_last_successful")
        mock_last_successful.return_value = (last_id, last_var)
        return

    def _call(self, facets, ds_id, drs_var, overwrite=False):
        facet = facets.get_drs_facet_builder(ds_id, drs_var)
        if overwrite:
            cmd = moo_cmd.put_safe_overwrite
        else:
            cmd = moo_cmd.put
        return call(
            "fake_local", facet, self.embargoed, cmd, timestamp=self.ts)


class TestMooseMove(unittest.TestCase):

    def setUp(self):
        self.project = "CMIP6"
        self.cfg, self.xfer = xfer_without_starting_comms(self, self.project)
        util.patch_mip_parser(self)
        self.mock_moo = util.create_patch(
            self, "cdds.deprecated.transfer.moo.run_moo_cmd")
        self.mock_inform = util.create_patch(
            self, "cdds.deprecated.transfer.dds.DataTransfer.inform")
        self.ts = date.today().strftime("%Y%m%d")
        self.embargoed = state.make_state(state.EMBARGOED)
        self.available = state.make_state(state.AVAILABLE)
        self.withdrawn = state.make_state(state.WITHDRAWN)
        self.ds_id = "CMIP6.MOHC.UKESM1.rcp45.mon.atmos.Amon.r1i1p1"

    def test_move_checks_state_transition(self):
        expected_old = self._mass_dir("available", "tas", "20150322")
        self.fake_single_ls([expected_old])
        drs_names = [self._drs("tas")]
        coll = self._coll(drs_names)
        self.assertRaises(
            ValueError, self.xfer.change_mass_state, coll,
            self.available, self.embargoed)

    def test_move_latest_version(self):
        expected_old = self._mass_dir("embargoed", "tas", "20150322")
        expected_new = self._mass_dir("available", "tas", "20150322")
        self.fake_single_ls([expected_old])
        drs_names = [self._drs("tas")]
        coll = self._coll(drs_names)
        mock_move_atom = util.create_patch(
            self, "cdds.deprecated.transfer.dds.DataTransfer._move_atom")

        self.xfer.change_mass_state(coll, self.embargoed, self.available)
        mock_move_atom.assert_called_once_with(expected_old, expected_new)
        self.mock_inform.assert_called_once_with(
            coll.get_drs_facet_builder(self.ds_id, "tas"), expected_new,
            self.available)

    def test_multi_atom_move(self):
        expected_old = [
            self._mass_dir("embargoed", "foo", "20140625"),
            self._mass_dir("embargoed", "tas", "20140626")]
        self.fake_multiple_ls_calls(expected_old)
        expected_new = [
            self._mass_dir("available", "foo", "20140625"),
            self._mass_dir("available", "tas", "20140626")]
        expected_call = [
            call(expected_old[0], expected_new[0]),
            call(expected_old[1], expected_new[1])]
        drs_names = [self._drs("foo"), self._drs("tas")]
        coll = self._coll(drs_names)
        expected_inform_call = [
            call(coll.get_drs_facet_builder(self.ds_id, "foo"),
                 expected_new[0], self.available),
            call(coll.get_drs_facet_builder(self.ds_id, "tas"),
                 expected_new[1],   self.available)]
        mock_move_atom = util.create_patch(
            self, "cdds.deprecated.transfer.dds.DataTransfer._move_atom")

        self.xfer.change_mass_state(coll, self.embargoed, self.available)
        mock_move_atom.has_calls(expected_call)
        self.mock_inform.has_calls(expected_inform_call)

    def test_move_older_version(self):
        expected_old = self._mass_dir("embargoed", "tas", "20150326")
        newer_version = self._mass_dir("embargoed", "tas", "20150625")
        self.fake_single_ls([expected_old, newer_version])
        expected_new = self._mass_dir("available", "tas", "20150326")
        drs_names = [self._drs("tas")]
        coll = self._coll(drs_names)
        mock_move_atom = util.create_patch(
            self, "cdds.deprecated.transfer.dds.DataTransfer._move_atom")

        self.xfer.change_mass_state(
            coll, self.embargoed, self.available, "20150326")
        mock_move_atom.assert_called_once_with(expected_old, expected_new)
        self.mock_inform.assert_called_once_with(
            coll.get_drs_facet_builder(self.ds_id, "tas"), expected_new,
            self.available)

    def test_find_last_successful(self):
        drs_names = [self._drs("foo"), self._drs("bar")]
        coll = self._coll(drs_names)
        self.mock_returns = [True, False]
        util.create_patch(
            self, "cdds.deprecated.transfer.moo_cmd.dir_exists",
            util.mock_with_side_effects(self))
        last_successful = self.xfer._find_last_successful(
            coll, self.embargoed, "")
        # coll will be sorted by id and var name, so our True matches
        # "bar" and False matches "foo".
        self.assertEqual(last_successful, (self.ds_id, "bar"))

    def test_rerun_move_latest_version(self):
        # We had bar_t1, bar_t2, bar_t3 and foo_t2, foo_t3. Pretend
        # that we did a "move latest" that died after the move of
        # bar_t3, so we now have: bar_t1, bar_t2, foo_t2 & foo_t3 in
        # the old state, and bar_t4 in the new state. A rerun should
        # attempt to move foo_t3.
        drs_names = [self._drs("bar"), self._drs("foo")]
        coll = self._coll(drs_names)
        mock_dir_exists = util.create_patch(
            self, "cdds.deprecated.transfer.dds.DataTransfer._find_last_successful")
        mock_dir_exists.return_value = (self.ds_id, "bar")
        fake_dir = [
            self._mass_dir("embargoed", "foo", "20140901"),
            self._mass_dir("embargoed", "foo", "20141001")]
        self.fake_single_ls(fake_dir)
        mock_move_atom = util.create_patch(
            self, "cdds.deprecated.transfer.dds.DataTransfer._move_atom")

        self.xfer.rerun_change_mass_state(
            coll, self.embargoed, self.available, "")
        new_dir = self._mass_dir("available", "foo", "20141001")
        mock_move_atom.assert_called_once_with(fake_dir[1], new_dir)

    def test_rerun_move_older_version(self):
        # We had bar_t1 and t2 and foo_t1 and t2. Pretend we tried to
        # move variables at version t1 and the job died after bar_t1.
        # A rerun should attempt to move foo_t1.
        drs_names = [self._drs("bar"), self._drs("foo")]
        coll = self._coll(drs_names)
        mock_dir_exists = util.create_patch(
            self, "cdds.deprecated.transfer.dds.DataTransfer._find_last_successful")
        mock_dir_exists.return_value = (self.ds_id, "bar")
        fake_dir = [
            self._mass_dir("embargoed", "foo", "20140901"),
            self._mass_dir("embargoed", "foo", "20141001")]
        self.fake_single_ls(fake_dir)
        mock_move_atom = util.create_patch(
            self, "cdds.deprecated.transfer.dds.DataTransfer._move_atom")

        self.xfer.rerun_change_mass_state(
            coll, self.embargoed, self.available, "", version="20140901")
        new_dir = self._mass_dir("available", "foo", "20140901")
        mock_move_atom.assert_called_once_with(fake_dir[0], new_dir)

    def test_successful_move_atom(self):
        self.xfer._move_atom("moose/old", "moose/new")
        expected_call = [
            call("mkdir", ["moose/new"]),
            call("mv", ["moose/old/*", "moose/new"])]
        self.mock_moo.has_calls(expected_call)

    def fake_single_ls(self, mock_output):
        # Mock a single ls with a single fake list of output.
        mock_ls = util.create_patch(self, "cdds.deprecated.transfer.moo_cmd.ls")
        mock_ls.return_value = mock_output
        return

    def fake_multiple_ls_calls(self, mock_output):
        # Mock a series of ls calls, each with a different list of
        # output.
        self.mock_returns = []
        for mock_out in mock_output:
            # we expect a list back from each ls call.
            self.mock_returns += [[mock_out]]
        util.create_patch(
            self, "cdds.deprecated.transfer.moo_cmd.ls",
            util.mock_with_side_effects(self))
        return

    def _mass_dir(self, current_state, var, ts=None):
        top_dir = "{top}/CMIP6/MOHC/UKESM1/rcp45/mon/atmos/Amon/r1i1p1".format(
            top=self.xfer._moo_top)
        if not ts:
            ts = self.ts
        return os.path.join(top_dir, var, current_state,
                            VERSION_FORMAT.format(ts))

    def _drs(self, var):
        return "{var}_Amon_UKESM1_rcp45_r1i1p1_202012-204511.nc".format(
            var=var)

    def _coll(self, drs_names):
        coll = drs.AtomicDatasetCollection()
        for drs_name in drs_names:
            facet = drs.DataRefSyntax(self.cfg, self.project)
            facet.fill_facets_from_drs_name(drs_name)
            coll.add(facet, filename=drs_name)
        return coll


class TestCopyFromMoose(unittest.TestCase):

    def setUp(self):
        self.project = "GEOMIP"
        self.cfg, self.xfer = xfer_without_starting_comms(self, self.project)
        util.patch_mip_parser(self)
        self.mock_moo = util.create_patch(
            self, "cdds.deprecated.transfer.moo.run_moo_cmd")
        self.mock_local_dir_exists = util.create_patch(
            self, "cdds.deprecated.transfer.dds.DataTransfer._local_dir_exists")
        facets = {
            "project": self.project, "variable": "bsi", "mip": "Omon",
            "model": "HadGEM2-ES", "experiment": "G4seaSalt",
            "ensemble": "r1i1p1"}
        self.facet = drs.DataRefSyntax(self.cfg, facets["project"])
        self.facet.fill_facets_from_dict(facets)

    def test_simple_copy_from_moose(self):
        expected_local_dir = os.path.join(
            "fake_local_top", self.project, "MOHC", "HadGEM2-ES",
            "G4seaSalt", "r1i1p1", "nc")
        self.mock_local_dir_exists.return_value = True
        self.xfer.copy_from_mass(
            "fake_local_top", "fake/moose/dir", self.facet)
        self.mock_local_dir_exists.assert_called_once_with(expected_local_dir)
        self.mock_moo.assert_called_once_with(
            "get",
            ["-f", "-j", 10, "fake/moose/dir/*", expected_local_dir],
            simulation=False, logger=None)

    def test_copy_with_missing_local_dir(self):
        expected_local_dir = os.path.join(
            "fake_local_top", self.project, "MOHC", "HadGEM2-ES",
            "G4seaSalt", "r1i1p1", "nc")
        self.mock_local_dir_exists.return_value = False
        mock_make_local_dir = util.create_patch(
            self, "cdds.deprecated.transfer.dds.DataTransfer._make_local_dir")
        self.xfer.copy_from_mass(
            "fake_local_top", "fake/moose/dir", self.facet)
        self.mock_local_dir_exists.assert_called_once_with(expected_local_dir)
        mock_make_local_dir.assert_called_once_with(expected_local_dir)
        self.mock_moo.assert_called_once_with(
            "get",
            ["-f", "-j", 10, "fake/moose/dir/*", expected_local_dir],
            simulation=False, logger=None)

    def test_default_transfer_threads(self):
        self.assertEqual(self.xfer._transfer_threads(), 10)

    def test_config_transfer_threads(self):
        fake_config = """[mass]
top_dir = fake
max_transfer_threads = 5"""
        util.create_patch(self, "cdds.deprecated.transfer.rabbit.RabbitMqManager.start")
        cfg = util.patch_open_config_with_string(fake_config)
        xfer = dds.DataTransfer(cfg, "fake")
        self.assertEqual(xfer._transfer_threads(), 5)


class TestFindLocalFacets(unittest.TestCase):

    def setUp(self):
        self.project = "CMIP6"
        self.cfg, self.xfer = xfer_without_starting_comms(self, self.project)
        self.fixed = drs.DataRefSyntax(self.cfg, self.project)

    def test_just_fixed_filter(self):
        self._prepare_simple_results()
        self._fill_fixed()
        local = self.xfer.find_local_facets(
            self.cfg.attr("local", "top_dir"), self.fixed)
        self._check_matched(local, ["tas", "uo"])

    def test_just_fixed_no_matches(self):
        self._prepare_simple_results()
        self.fixed.fill_facets_from_dict({
            "project": "CMIP6", "model": "HADCM3",
            "experiment": "rcp45", "mip": "Amon"})
        local = self.xfer.find_local_facets(
            self.cfg.attr("local", "top_dir"), self.fixed)
        self.assertEqual(len(local.dataset_ids()), 0)

    def test_single_include(self):
        self._prepare_simple_results()
        self._fill_fixed()
        include = self._facet({"variable": "tas"})
        local = self.xfer.find_local_facets(
            self.cfg.attr("local", "top_dir"), self.fixed,
            include_drs_facet_builder_list=[include])
        self._check_matched(local, ["tas"])

    def test_includes_everything(self):
        self._prepare_simple_results()
        self._fill_fixed()
        include = self._facet({"ensemble": "r1i1p1"})
        local = self.xfer.find_local_facets(
            self.cfg.attr("local", "top_dir"), self.fixed,
            include_drs_facet_builder_list=[include])
        self._check_matched(local, ["tas", "uo"])

    def test_multiple_includes(self):
        self._prepare_simple_results()
        self._fill_fixed()
        include = []
        for drs_var in ["tas", "uo"]:
            inc_facet = self._facet({"variable": drs_var})
            include.append(inc_facet)
        local = self.xfer.find_local_facets(
            self.cfg.attr("local", "top_dir"), self.fixed,
            include_drs_facet_builder_list=include)
        self._check_matched(local, ["tas", "uo"])

    def test_multiple_includes_with_overlaps(self):
        self._prepare_simple_results()
        self._fill_fixed()
        var_facet = self._facet({"variable": "tas"})
        ens_facet = self._facet({"ensemble": "r1i1p1"})
        local = self.xfer.find_local_facets(
            self.cfg.attr("local", "top_dir"), self.fixed,
            include_drs_facet_builder_list=[var_facet, ens_facet])
        self._check_matched(local, ["tas", "uo"])

    def test_single_exclude(self):
        self._prepare_simple_results()
        self._fill_fixed()
        exclude = self._facet({"variable": "tas"})
        local = self.xfer.find_local_facets(
            self.cfg.attr("local", "top_dir"), self.fixed,
            exclude_drs_facet_builder_list=[exclude])
        self._check_matched(local, ["uo"])

    def test_exclude_everything(self):
        self._prepare_simple_results()
        self._fill_fixed()
        exclude = self._facet({"ensemble": "r1i1p1"})
        local = self.xfer.find_local_facets(
            self.cfg.attr("local", "top_dir"), self.fixed,
            exclude_drs_facet_builder_list=[exclude])
        self.assertEqual(len(local.dataset_ids()), 0)

    def test_multiple_excludes(self):
        self._prepare_simple_results()
        self._fill_fixed()
        exclude = []
        for drs_var in ["tas", "uo"]:
            exc_facet = self._facet({"variable": drs_var})
            exclude.append(exc_facet)
        local = self.xfer.find_local_facets(
            self.cfg.attr("local", "top_dir"), self.fixed,
            exclude_drs_facet_builder_list=exclude)
        self.assertEqual(len(local.dataset_ids()), 0)

    def test_multiple_excludes_with_overlaps(self):
        self._prepare_simple_results()
        self._fill_fixed()
        var_facet = self._facet({"variable": "tas"})
        ens_facet = self._facet({"ensemble": "r1i1p1"})
        local = self.xfer.find_local_facets(
            self.cfg.attr("local", "top_dir"), self.fixed,
            exclude_drs_facet_builder_list=[var_facet, ens_facet])
        self.assertEqual(len(local.dataset_ids()), 0)

    def test_include_and_exclude(self):
        self._prepare_simple_results()
        self._fill_fixed()
        include = self._facet({"ensemble": "r1i1p1"})
        exclude = self._facet({"variable": "tas"})
        local = self.xfer.find_local_facets(
            self.cfg.attr("local", "top_dir"), self.fixed,
            include_drs_facet_builder_list=[include],
            exclude_drs_facet_builder_list=[exclude])
        self._check_matched(local, ["uo"])

    def test_error_if_same_facet_in_include_and_exclude(self):
        self._prepare_simple_results()
        self._fill_fixed()
        include = self._facet({"variable": "tas"})
        exclude = self._facet({"variable": "uo"})
        self.assertRaises(
            ValueError, self.xfer.find_local_facets, "local_top", self.fixed,
            include_drs_facet_builder_list=[include],
            exclude_drs_facet_builder_list=[exclude])

    def test_conditions_are_anded(self):
        self._prepare_simple_results()
        self._fill_fixed()
        include = self._facet({"ensemble": "r1i1p1", "variable": "tas"})
        local = self.xfer.find_local_facets(
            self.cfg.attr("local", "top_dir"), self.fixed,
            include_drs_facet_builder_list=[include])
        self._check_matched(local, ["tas"])

    def test_sub_fileset_filters_raise_errors(self):
        self._prepare_simple_results()
        self._fill_fixed()
        include = self._facet({"variable": "tas", "date": "185001-185412"})
        self.assertRaises(
            ValueError, self.xfer.find_local_facets, "local_top",
            self.fixed, include_drs_facet_builder_list=[include])

    def _prepare_simple_results(self):
        util.patch_mip_parser(self)
        self.expected_id = "CMIP6.MOHC.HADCM3.historical.mon.atmos.Amon.r1i1p1"
        self.coll = drs.AtomicDatasetCollection()
        self.drs_names = {
            "tas": [
                "tas_Amon_HADCM3_historical_r1i1p1_185001-185412.nc",
                "tas_Amon_HADCM3_historical_r1i1p1_185501-185912.nc"],
            "uo": ["uo_Amon_HADCM3_historical_r1i1p1_185001-185412.nc"]}
        for drs_var in self.drs_names:
            for drs_name in self.drs_names[drs_var]:
                facet = drs.DataRefSyntax(self.cfg, self.project)
                facet.fill_facets_from_drs_name(drs_name)
                self.coll.add(facet)
        # The following is hit iff there is no sublocal facet list
        mock_list = util.create_patch(self, "os.listdir")
        mock_list.return_value = self.drs_names["tas"] + self.drs_names["uo"]

        # local_top is the same for every data set here
        local_top = facet.local_dir(self.cfg.attr("local", "top_dir"))
        self.local_top = local_top
        mock_walk = util.create_patch(self, "os.walk")
        mock_walk.return_value = [
            (os.path.join(local_top, "apm"), [], self.drs_names["tas"]),
            (os.path.join(local_top, "onm"), [], self.drs_names["uo"])
        ]
        return

    def _fill_fixed(self):
        self.fixed.fill_facets_from_dict({
            "project": "CMIP6", "model": "HADCM3",
            "experiment": "historical", "mip": "Amon"})
        return

    def _check_matched(self, matched, drs_var):
        self.assertEqual(len(matched.dataset_ids()), 1)
        self.assertEqual(matched.dataset_ids()[0], self.expected_id)
        self.assertEqual(
            len(matched.drs_variables(self.expected_id)), len(drs_var))
        for var in drs_var:
            self.assertEqual(
                len(matched.filenames(self.expected_id, var)),
                len(self.drs_names[var]))
            self.assertEqual(
                sorted(matched.filenames(self.expected_id, var)),
                sorted(self.drs_names[var]))
        return

    def _facet(self, facets):
        facet = drs.DataRefSyntax(self.cfg, self.project)
        facet.fill_facets_from_dict(facets)
        return facet


class TestFindMassFacets(unittest.TestCase):

    def setUp(self):
        self.project = "CMIP6"
        self.urls = [
            self._url("historical", "mon", "atmos", "Amon", "r1i1p1", "tas"),
            self._url("rcp45", "mon", "atmos", "Amon", "r1i1p1", "tas"),
            self._url("rcp45", "mon", "ocean", "Omon", "r1i1p1", "uo")]
        self.cfg, self.xfer = xfer_without_starting_comms(self, self.project)
        self.fixed = drs.DataRefSyntax(self.cfg, self.project)
        self.embargoed = state.make_state(state.EMBARGOED)
        self.coll = drs.AtomicDatasetCollection()
        util.patch_mip_parser(self)
        util.create_patch(self, "cdds.deprecated.transfer.moo_cmd.ls_tree")

    def test_spots_duplicate_include_and_exclude(self):
        include = drs.DataRefSyntax(self.cfg, self.project)
        include.fill_facets_from_dict({"variable": "foo"})
        exclude = drs.DataRefSyntax(self.cfg, self.project)
        exclude.fill_facets_from_dict({"variable": "bar"})
        self.assertRaises(
            ValueError, self.xfer.find_mass_facets, self.fixed, self.embargoed,
            include_drs_facet_builder_list=[include],
            exclude_drs_facet_builder_list=[exclude])

    def test_just_fixed(self):
        self._fill_coll_from_urls(self.urls)
        self._patch_tree_to_facets()
        self.fixed.fill_facets_from_dict({"experiment": "rcp45"})
        filtered = self.xfer.find_mass_facets(self.fixed, self.embargoed)
        self.assertEqual(len(filtered.dataset_ids()), 2)

    def test_just_fixed_no_matches(self):
        self._fill_coll_from_urls(self.urls)
        self._patch_tree_to_facets()
        self.fixed.fill_facets_from_dict({"experiment": "rcp85"})
        filtered = self.xfer.find_mass_facets(self.fixed, self.embargoed)
        self.assertEqual(len(filtered.dataset_ids()), 0)

    def test_just_fixed_no_state_matches(self):
        self._fill_coll_from_urls(self.urls)
        self._patch_tree_to_facets()
        self.fixed.fill_facets_from_dict({"experiment": "historical"})
        available = state.make_state(state.AVAILABLE)
        filtered = self.xfer.find_mass_facets(self.fixed, available)
        self.assertEqual(len(filtered.dataset_ids()), 0)

    def test_single_include(self):
        self._fill_coll_from_urls(self.urls)
        self._patch_tree_to_facets()
        self.fixed.fill_facets_from_dict({"experiment": "rcp45"})
        include = self._facet({"variable": "tas"})
        expected = self.coll.get_drs_facet_builder(
            self._ds_id("rcp45", "mon", "atmos", "Amon"), "tas")
        filtered = self.xfer.find_mass_facets(
            self.fixed, self.embargoed,
            include_drs_facet_builder_list=[include])
        actual = filtered.get_drs_facet_builder_list()
        self.assertEqual(len(actual), 1)
        self.assertEqual(actual[0], expected)

    def test_single_include_matches_everything(self):
        self._fill_coll_from_urls(self.urls)
        self._patch_tree_to_facets()
        self.fixed.fill_facets_from_dict({"frequency": "mon"})
        include = self._facet({"ensemble": "r1i1p1"})
        filtered = self.xfer.find_mass_facets(
            self.fixed, self.embargoed,
            include_drs_facet_builder_list=[include])
        self.assertEqual(filtered.get_drs_facet_builder_list(),
                         self.coll.get_drs_facet_builder_list())

    def test_multiple_includes(self):
        self._fill_coll_from_urls(self.urls)
        self._patch_tree_to_facets()
        self.fixed.fill_facets_from_dict({"frequency": "mon"})
        include = [
            self._facet({"experiment": "historical"}),
            self._facet({"experiment": "rcp45", "variable": "tas"})]
        filtered = self.xfer.find_mass_facets(
            self.fixed, self.embargoed,
            include_drs_facet_builder_list=include)
        expected = [
            self.coll.get_drs_facet_builder(
                self._ds_id("historical", "mon", "atmos", "Amon"), "tas"),
            self.coll.get_drs_facet_builder(
                self._ds_id("rcp45", "mon", "atmos", "Amon"), "tas")]
        self.assertEqual(filtered.get_drs_facet_builder_list(), expected)

    def test_multiple_includes_with_overlaps(self):
        self._fill_coll_from_urls(self.urls)
        self._patch_tree_to_facets()
        self.fixed.fill_facets_from_dict({"experiment": "rcp45"})
        include = [
            self._facet({"frequency": "mon"}),
            self._facet({"variable": "uo"})]
        filtered = self.xfer.find_mass_facets(
            self.fixed, self.embargoed,
            include_drs_facet_builder_list=include)
        expected = [
            self.coll.get_drs_facet_builder(
                self._ds_id("rcp45", "mon", "atmos", "Amon"), "tas"),
            self.coll.get_drs_facet_builder(
                self._ds_id("rcp45", "mon", "ocean", "Omon"), "uo")]
        self.assertEqual(filtered.get_drs_facet_builder_list(), expected)

    def test_single_exclude(self):
        self._fill_coll_from_urls(self.urls)
        self._patch_tree_to_facets()
        self.fixed.fill_facets_from_dict({"experiment": "rcp45"})
        exclude = [self._facet({"variable": "uo"})]
        filtered = self.xfer.find_mass_facets(
            self.fixed, self.embargoed,
            exclude_drs_facet_builder_list=exclude)
        expected = [
            self.coll.get_drs_facet_builder(
                self._ds_id("rcp45", "mon", "atmos", "Amon"), "tas")]
        self.assertEqual(filtered.get_drs_facet_builder_list(), expected)

    def test_exclude_everything(self):
        self._fill_coll_from_urls(self.urls)
        self._patch_tree_to_facets()
        self.fixed.fill_facets_from_dict({"experiment": "rcp45"})
        exclude = [self._facet({"frequency": "mon"})]
        filtered = self.xfer.find_mass_facets(
            self.fixed, self.embargoed,
            exclude_drs_facet_builder_list=exclude)
        self.assertEqual(len(filtered.dataset_ids()), 0)

    def test_multiple_excludes(self):
        self._fill_coll_from_urls(self.urls)
        self._patch_tree_to_facets()
        self.fixed.fill_facets_from_dict({"frequency": "mon"})
        exclude = [
            self._facet({"experiment": "historical"}),
            self._facet({"variable": "tas"})]
        filtered = self.xfer.find_mass_facets(
            self.fixed, self.embargoed,
            exclude_drs_facet_builder_list=exclude)
        expected = [self.coll.get_drs_facet_builder(
            self._ds_id("rcp45", "mon", "ocean", "Omon"), "uo")]
        self.assertEqual(filtered.get_drs_facet_builder_list(), expected)

    def test_multiple_excludes_with_overlaps(self):
        self._fill_coll_from_urls(self.urls)
        self._patch_tree_to_facets()
        self.fixed.fill_facets_from_dict({"frequency": "mon"})
        exclude = [
            self._facet({"experiment": "rcp45"}),
            self._facet({"variable": "uo"})]
        filtered = self.xfer.find_mass_facets(
            self.fixed, self.embargoed,
            exclude_drs_facet_builder_list=exclude)
        expected = [self.coll.get_drs_facet_builder(
            self._ds_id("historical", "mon", "atmos", "Amon"), "tas")]
        self.assertEqual(filtered.get_drs_facet_builder_list(), expected)

    def test_include_and_exclude(self):
        self._fill_coll_from_urls(self.urls)
        self._patch_tree_to_facets()
        self.fixed.fill_facets_from_dict({"frequency": "mon"})
        include = [self._facet({"realm": "atmos"})]
        exclude = [self._facet({"experiment": "rcp45"})]
        filtered = self.xfer.find_mass_facets(
            self.fixed, self.embargoed,
            include_drs_facet_builder_list=include,
            exclude_drs_facet_builder_list=exclude)
        expected = [self.coll.get_drs_facet_builder(
            self._ds_id("historical", "mon", "atmos", "Amon"), "tas")]
        self.assertEqual(filtered.get_drs_facet_builder_list(), expected)

    def test_mass_to_facets(self):
        top = "moose:fake/moose/dir"
        tree = [
            "CMIP6",
            "CMIP6/MOHC",
            "CMIP6/MOHC/UKESM1",
            "CMIP6/MOHC/UKESM1/historical",
            "CMIP6/MOHC/UKESM1/historical/mon",
            "CMIP6/MOHC/UKESM1/historical/mon/atmos",
            "CMIP6/MOHC/UKESM1/historical/mon/atmos/Amon",
            "CMIP6/MOHC/UKESM1/historical/mon/atmos/Amon/r1i1p1",
            "CMIP6/MOHC/UKESM1/historical/mon/atmos/Amon/r1i1p1/"
            "foo",
            "CMIP6/MOHC/UKESM1/historical/mon/atmos/Amon/r1i1p1/"
            "foo/embargoed/v20160211/",
            "CMIP6/MOHC/UKESM1/historical/mon/atmos/Amon/r1i1p1/"
            "foo/embargoed/v20160211/foo_Amon_UKESM1_historical_r1i1p1.nc",
            "CMIP6/MOHC/UKESM1/historical/mon/atmos/Amon/r1i1p1/"
            "tas",
            "CMIP6/MOHC/UKESM1/historical/mon/atmos/Amon/r1i1p1/"
            "tas/embargoed",
            "CMIP6/MOHC/UKESM1/historical/mon/atmos/Amon/r1i1p1/"
            "tas/embargoed/v20160211",
            "CMIP6/MOHC/UKESM1/historical/mon/atmos/Amon/r1i1p1/"
            "tas/embargoed/v20160211/tas_Amon_UKESM1_historical_r1i1p1.nc",
        ]
        xml = ['<?xml version="1.0"?>', "<nodes>"]
        for node in tree:
            xml.append('<node url="{top}/{node}">'.format(top=top, node=node))
            xml.append('</node>')
        xml.append("</nodes>")
        facets = self.xfer._mass_to_facets(xml, self.embargoed)
        self.assertEqual(len(facets.dataset_ids()), 1)
        expected_id = self._ds_id("historical", "mon", "atmos", "Amon")
        self.assertEqual(facets.dataset_ids()[0], expected_id)
        self.assertEqual(len(facets.drs_variables(expected_id)), 2)
        self.assertEqual(facets.drs_variables(expected_id), ["foo", "tas"])
        self.assertEqual(
            facets.filenames(expected_id, "foo"),
            ["foo_Amon_UKESM1_historical_r1i1p1.nc"])

    def _url(self, expt, freq, realm, mip, realise, var):
        fixed = "moose:fake/moose/dir/CMIP6/MOHC/UKESM1"
        drs_name = "_".join([var, mip, "UKESM1", expt, "%s.nc" % realise])
        return "/".join([
            fixed, expt, freq, realm, mip, realise, var, "embargoed",
            drs_name])

    def _fill_coll_from_urls(self, urls):
        for url in urls:
            facet = drs.DataRefSyntax(self.cfg, self.project)
            facet.fill_facets_from_mass_dir(url)
            self.coll.add(facet, filename=url)
        return

    def _ds_id(self, expt, freq, realm, mip):
        return ".".join([
            "CMIP6", "MOHC", "UKESM1", expt, freq, realm, mip, "r1i1p1"])

    def _patch_tree_to_facets(self):
        mock_tree_to_facets = util.create_patch(
            self, "cdds.deprecated.transfer.dds.DataTransfer._mass_to_facets")
        mock_tree_to_facets.return_value = self.coll
        return

    def _facet(self, facets):
        facet = drs.DataRefSyntax(self.cfg, self.project)
        facet.fill_facets_from_dict(facets)
        return facet


class TestFilterFacets(unittest.TestCase):

    def setUp(self):
        self.project = "CMIP6"
        self.cfg, self.xfer = xfer_without_starting_comms(self, self.project)
        util.patch_mip_parser(self)

    def test_spots_duplicate_include_and_exclude(self):
        include = self._facet({"variable": "tas"})
        exclude = self._facet({"variable": "foo"})
        fixed = self._facet({"experiment": "historical"})
        coll = self._input_coll()
        self.assertRaises(
            ValueError, self.xfer.filter_facets, coll, fixed,
            include_drs_facet_builder_list=[include],
            exclude_drs_facet_builder_list=[exclude])

    def test_just_fixed(self):
        coll = self._input_coll()
        fixed = self._facet({"model": "UKESM1", "experiment": "historical"})
        filtered = self.xfer.filter_facets(coll, fixed)
        self.assertEqual(len(filtered.dataset_ids()), 1)
        self.assertEqual(len(filtered.get_drs_facet_builder_list()), 2)

    def test_just_fixed_no_matches(self):
        coll = self._input_coll()
        fixed = self._facet({"experiment": "rcp85"})
        filtered = self.xfer.filter_facets(coll, fixed)
        self.assertEqual(len(filtered.get_drs_facet_builder_list()), 0)

    def test_single_include(self):
        coll = self._input_coll()
        fixed = self._facet({"experiment": "historical"})
        include = [self._facet({"variable": "tas"})]
        filtered = self.xfer.filter_facets(
            coll, fixed, include_drs_facet_builder_list=include)
        self.assertEqual(len(filtered.get_drs_facet_builder_list()), 1)

    def test_single_include_matches_everything(self):
        coll = self._input_coll()
        fixed = self._facet({"experiment": "historical"})
        include = [self._facet({"model": "UKESM1"})]
        filtered = self.xfer.filter_facets(
            coll, fixed, include_drs_facet_builder_list=include)
        self.assertEqual(len(filtered.get_drs_facet_builder_list()), 2)

    def test_multiple_includes(self):
        coll = self._input_coll()
        fixed = self._facet({"model": "UKESM1"})
        include = [
            self._facet({"experiment": "historical"}),
            self._facet({"experiment": "rcp45"})]
        filtered = self.xfer.filter_facets(
            coll, fixed, include_drs_facet_builder_list=include)
        self.assertEqual(len(filtered.get_drs_facet_builder_list()), 3)

    def test_multiple_includes_with_overlaps(self):
        coll = self._input_coll()
        fixed = self._facet({"model": "UKESM1"})
        include = [
            self._facet({"variable": "tas"}),
            self._facet({"experiment": "rcp45"})]
        filtered = self.xfer.filter_facets(
            coll, fixed, include_drs_facet_builder_list=include)
        self.assertEqual(len(filtered.get_drs_facet_builder_list()), 2)

    def test_single_exclude(self):
        coll = self._input_coll()
        fixed = self._facet({"model": "UKESM1"})
        exclude = [self._facet({"variable": "tas"})]
        filtered = self.xfer.filter_facets(
            coll, fixed, exclude_drs_facet_builder_list=exclude)
        self.assertEqual(len(filtered.get_drs_facet_builder_list()), 1)

    def test_exclude_everything(self):
        coll = self._input_coll()
        fixed = self._facet({"model": "UKESM1"})
        exclude = [self._facet({"frequency": "mon"})]
        filtered = self.xfer.filter_facets(
            coll, fixed, exclude_drs_facet_builder_list=exclude)
        self.assertEqual(len(filtered.get_drs_facet_builder_list()), 0)

    def test_multiple_excludes(self):
        coll = self._input_coll()
        fixed = self._facet({"model": "UKESM1"})
        exclude = [
            self._facet({"variable": "tas"}),
            self._facet({"variable": "foo"})]
        filtered = self.xfer.filter_facets(
            coll, fixed, exclude_drs_facet_builder_list=exclude)
        self.assertEqual(len(filtered.get_drs_facet_builder_list()), 0)

    def test_multiple_excludes_with_overlaps(self):
        coll = self._input_coll()
        fixed = self._facet({"model": "UKESM1"})
        exclude = [
            self._facet({"experiment": "rcp45"}),
            self._facet({"variable": "tas"})]
        filtered = self.xfer.filter_facets(
            coll, fixed, exclude_drs_facet_builder_list=exclude)
        self.assertEqual(len(filtered.get_drs_facet_builder_list()), 1)

    def test_include_and_exclude(self):
        coll = self._input_coll()
        fixed = self._facet({"model": "UKESM1"})
        include = [self._facet({"experiment": "historical"})]
        exclude = [self._facet({"variable": "tas"})]
        filtered = self.xfer.filter_facets(
            coll, fixed, include_drs_facet_builder_list=include,
            exclude_drs_facet_builder_list=exclude)
        self.assertEqual(len(filtered.get_drs_facet_builder_list()), 1)

    def _facet(self, facets):
        facet = drs.DataRefSyntax(self.cfg, self.project)
        facet.fill_facets_from_dict(facets)
        return facet

    def _input_coll(self):
        shared = {
            "model": "UKESM1", "frequency": "mon", "realm": "atmos",
            "mip": "Amon", "ensemble": "r1i1p1"}
        coll = drs.AtomicDatasetCollection()
        input_facets = [
            {"experiment": "historical", "variable": "tas"},
            {"experiment": "rcp45", "variable": "tas"},
            {"experiment": "historical", "variable": "foo"}]
        for input_facet in input_facets:
            facet = self._facet(self._merge_dict(shared, input_facet))
            coll.add(facet)
        return coll

    def _merge_dict(self, dict_a, dict_b):
        merged = dict_a.copy()
        merged.update(dict_b)
        return merged


class TestInform(unittest.TestCase):

    def setUp(self):
        self.project = "CORDEX"
        cfg, self.dds = xfer_without_starting_comms(self, self.project)
        var = (
            "hfls_CAS-44_ERAINT_evaluation_r1i1p1_MOHC-HadRM3P_"
            "v1_mon_199001-199012.nc")
        self.facet = drs.DataRefSyntax(cfg, self.project)
        self.facet.fill_facets_from_drs_name(var)

    def test_message_for_available_var(self):
        mock_publish = util.create_patch(
            self, "cdds.deprecated.transfer.msg.Communication.publish_message")
        available = state.make_state(state.AVAILABLE)
        expected_content = {
            "mass_dir": "fake_moo", "state": available.name(),
            "facets": self.facet.facets,
            "dataset_id": self.facet.dataset_id(),
            "mip_era": self.project
        }
        expected_message = msg.MooseMessage(content=expected_content)
        self.dds.inform(self.facet, "fake_moo", available)
        mock_publish.assert_called_once_with(expected_message)

    def test_inform_handles_quiet_states(self):
        mock_publish = util.create_patch(
            self, "cdds.deprecated.transfer.msg.Communication.publish_message")
        for quiet_state in [state.Embargoed(), state.Superseded()]:
            self.dds.inform(self.facet, "fake_moo", quiet_state)
            self.assertFalse(mock_publish.called)

    def test_inform_handles_noisy_states(self):
        mock_publish = util.create_patch(
            self, "cdds.deprecated.transfer.msg.Communication.publish_message")
        for noisy_state in [state.Available(), state.Withdrawn()]:
            self.dds.inform(self.facet, "fake_moo", noisy_state)
            self.assertTrue(mock_publish.called)


class TestSerialise(unittest.TestCase):

    def setUp(self):
        self.project = "CMIP6"
        self.cfg, self.dds = xfer_without_starting_comms(self, self.project)
        util.patch_mip_parser(self)

    def test_serialise_is_reversible(self):
        drs_names = [
            "tas_Amon_UKESM1_rcp45_r1i1p1_nc",
            "tas_Omon_UKESM1_rcp45_r1i1p1.nc"]
        coll = drs.AtomicDatasetCollection()
        for drs_name in drs_names:
            facet = drs.DataRefSyntax(self.cfg, self.project)
            facet.fill_facets_from_drs_name(drs_name)
            coll.add(facet)
        serial = self.dds.serialise_facets(coll)
        deserial = self.dds.expand_facets(serial)
        self.assertEqual(deserial, coll)


class TestPrepareMessage(unittest.TestCase):

    def setUp(self):
        self.project = "GEOMIP"
        self.cfg, self.xfer = xfer_without_starting_comms(self, self.project)
        util.patch_mip_parser(self)
        self.ts = date.today().strftime("%Y%m%d")
        self.available = state.make_state(state.AVAILABLE)

    def test_prepare_message(self):
        var = "zos_Omon_HadGEM2-ES_G4seaSalt_r1i1p1_202012-209012.nc"
        facet = drs.DataRefSyntax(self.cfg, self.project)
        facet.fill_facets_from_drs_name(var)
        moo_dir = (
            "%s/geomip/output/MOHC/HadGEM2-ES/G4seaSalt/mon/ocean/Omon/"
            "r1i1p1/available/zos_%s" % (self.xfer._moo_top, self.ts))
        message = self.xfer._prepare_message(
            facet, moo_dir, self.available)
        self.assertEqual(moo_dir, message.content["mass_dir"])
        self.assertEqual("available", message.content["state"])
        self.assertIn("facets", message.content)
        self.assertEqual("ocean", message.content["facets"]["realm"])


class TestVersionList(unittest.TestCase):

    def setUp(self):
        project = "GEOMIP"
        cfg, self.xfer = xfer_without_starting_comms(self, project)
        util.patch_mip_parser(self)
        self.xfer = dds.DataTransfer(cfg, project)
        self.facet = drs.DataRefSyntax(cfg, project)
        self.facet.fill_facets_from_drs_name(
            "bsi_Omon_HadGEM2-ES_G4seaSalt_r1i1p1_202012-209012.nc")
        self.mock_moo_ls = util.create_patch(self, "cdds.deprecated.transfer.moo_cmd.ls")
        self.fake_top = (
            "%s/geomip/output/MOHC/HadGEM2-ES/G4seaSalt/mon/ocean/"
            "Omon/r1i1p1/embargoed" % self.xfer._moo_top)
        self.embargoed = state.make_state(state.EMBARGOED)

    def test_latest_when_we_only_have_one(self):
        self.mock_moo_ls.return_value = [
            os.path.join(self.fake_top, "bsi/v20140213")]
        latest = self.xfer._latest_ts_for_state(self.facet, self.embargoed)
        self.assertEqual(latest, "20140213")

    def test_latest_when_we_have_several(self):
        self.mock_moo_ls.return_value = [
            os.path.join(self.fake_top, "bsi", "v20140213"),
            os.path.join(self.fake_top, "bsi", "v20131215"),
            os.path.join(self.fake_top, "bsi", "v20140328")]
        latest = self.xfer._latest_ts_for_state(self.facet, self.embargoed)
        self.assertEqual(latest, "20140328")

    def test_latest_when_we_have_none(self):
        self.mock_moo_ls.return_value = []
        self.assertRaises(
            ValueError, self.xfer._latest_ts_for_state,
            self.facet, self.embargoed)


class TestSearchLocalDirectories(unittest.TestCase):

    def setUp(self):
        self.project = "ScenarioMIP"
        self.cfg, _ = xfer_without_starting_comms(self, self.project)

    @patch("os.walk")
    def test_simple(self, mock_walk):
        expected_files = {
            'tntrl_AERmon_HadGEM3-GC31-LL_ssp245_r1i1p1f1_gn_'
            '{}.nc'.format(i): 'local_path/apu/AERmon/tntrl'
            for i in ['185001-186912', '187001-188912', '189001-190012']
        }
        mock_walk.return_value = [
            ('local_path/apu', ('AERmon',), ()),
            ('local_path/apu/AERmon', ('tntrl'), ()),
            ('local_path/apu/AERmon/tntrl', (), expected_files)
        ]
        expected_streams = {'AERmon,tntrl': 'apu'}

        fixed_facet = drs.DataRefSyntax(self.cfg, self.project)
        result_files, result_streams = dds.search_local_directories(
            fixed_facet, 'local_path')
        self.assertDictEqual(result_files, expected_files)
        self.assertDictEqual(result_streams, expected_streams)


if __name__ == "__main__":
    unittest.main()
