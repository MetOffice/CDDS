# (C) British Crown Copyright 2016-2021, Met Office.
# Please see LICENSE.rst for license details.
import copy
from datetime import date
import glob
import json
import logging
import os
import re
import xml.sax

from cdds_transfer import drs, moo, moo_cmd, msg

VERSION_FORMAT_DATETIME = "v%Y%m%d"
VERSION_FORMAT = "v{}"
VERSION_TIMESTAMP_REGEX = r"^v(\d{8})"


class DataTransfer(object):

    """Provide data transfer services.

    Public methods:
    change_mass_state -- move facets in MASS to a new state
    copy_from_ass -- copy data sets from MASS
    expand_facets -- expand serialised facets back into objects
    find_local_facets -- search local directories for matching facets
    find_mass_facets -- search MASS directories for matching facets
    inform -- inform BADC of significant MASS state changes
    rerun_change_mass_state -- complete a move that failed part-way through
    rerun_send_to_mass -- complete a send that failed part-way through
    send_to_mass -- copy facets from local directory to MASS
    serialise_facets -- serialise facets to a form that can be saved
    """

    def __init__(self, config, project, simulation=False):
        """Create a data transfer object with a communications connection to
        Rabbit (if a connection can be made).

        Arguments:
        config -- (config.Config object) configuration file wrapper
        project -- (str) project name
        simulation -- (bool) print moose commands rather than run them
        """
        self._config = config
        self._project = project
        self._comm = None  # msg.Communication(self._config)
        self._moo_top = self._config.attr("mass", "top_dir")
        self._simulation = simulation
        self._stream = {}

    def send_to_mass(self, local_top, filesets, state):
        """Send facet(s) to MASS in the specified state.

        Locates filesets on local disk, deduces their path on MASS and
        copies them across. If the specified state is one that BADC
        are informed about, messages will be sent.

        Arguments:
        local_top -- (str) path to top of local directory
        filesets -- (drs.AtomicDatasetCollection) fileset(s) to send
        state -- (state.State) state the filesets should be placed in
        """
        if not state.can_be_put():
            raise ValueError("Cannot send files to MASS in state \"{}\""
                             "".format(state))
        for fileset in filesets:
            self._run_put(local_top, fileset, state, moo_cmd.put)
        return

    def rerun_send_to_mass(self, local_top, filesets, state, timestamp):
        """Re-run a MASS send that failed part way through.

        Locates facets on local disk, deduces their path on MASS and
        copies them across if necessary. If the specified state is one
        that BADC are informed about, messages will be sent.

        You need to specify the date that the original "send_to_mass"
        was run so that the code can identify the directories that
        should exist on MASS for the supplied facets.

        Arguments:
        local_top -- (str) path to top of local directory
        filesets -- (drs.AtomicDatasetCollection) fileset(s) to send
        state -- (state.State) state the filesets should be placed in
        timestamp -- (str) date the initial "send" method was run
        """
        if not state.can_be_put():
            raise ValueError("Cannot send files to MASS in state \"{}\""
                             "".format(state))
        (last_id, last_var) = self._find_last_successful(
            filesets, state, timestamp)
        if last_id is None and last_var is None:
            # We didn't successfully run anything, so we can just run
            # a normal send.
            self.send_to_mass(local_top, filesets, state)
            return
        # Last successful data set may have died partway through.
        self._run_put(
            local_top, filesets.get_drs_facet_builder(last_id, last_var),
            state, moo_cmd.put_safe_overwrite, timestamp=timestamp)
        # Finish off any remaining vars in the last successful id...
        drs_vars = filesets.drs_variables(last_id)
        if last_var != drs_vars[-1]:
            last_loc = drs_vars.index(last_var)
            for drs_var in drs_vars[last_loc + 1:]:
                self._run_put(
                    local_top,
                    filesets.get_drs_facet_builder(last_id, drs_var),
                    state, moo_cmd.put, timestamp=timestamp)
        dataset_ids = filesets.dataset_ids()
        if last_id == dataset_ids[-1]:
            # We have nothing else left to put.
            return
        # and then send any remaining data sets.
        last_loc = dataset_ids.index(last_id)
        for dataset_id in dataset_ids[last_loc + 1:]:
            for drs_var in filesets.drs_variables(dataset_id):
                self._run_put(
                    local_top,
                    filesets.get_drs_facet_builder(dataset_id, drs_var),
                    state, moo_cmd.put, timestamp=timestamp)
        return

    def change_mass_state(
            self, filesets, old_state, new_state, timestamp=None):
        """Change the state of facet(s) in MASS.

        Locates the fileset(s) on MASS and moves them from their current
        state to the specified new state. If the new state is one that
        BADC is informed about, messages will be sent.

        By default, the latest available version of a facet in MASS
        will be moved. If you wish to move and earlier version,
        specify the timestamp (str, YYYYMMDD format).

        Arguments:
        filesets -- (drs.AtomicDatasetCollection) fileset(s) to move
        old_state -- (state.State) current state of filesets in MASS
        new_state -- (state.State) new state of facets in MASS

        Keyword arguments:
        timestamp -- (str) version of facet to move (YYYYMMDD)
        """
        if not old_state.can_move_to(new_state):
            raise ValueError(
                "Cannot move from {old} to {new}".format(
                    old=old_state, new=new_state))
        for fileset in filesets:
            new_dir = self._run_move(
                fileset, old_state, new_state, timestamp=timestamp)
            self.inform(fileset, new_dir, new_state)
        return

    def rerun_change_mass_state(
            self, filesets, old_state, new_state, cmd_timestamp, version=None):
        """Rerun a MASS state change that failed part way through.

        Locates the fileset(s) in MASS and moves them from their current
        state to the specified new state, if necessary. If the new
        state is one that BADC is informed about, send messages to
        them.

        You must specify the date the original change state was
        attempted so that the program can deduce the expected
        directory names on MASS and check to see how far through the
        command got.

        By default, the latest available version of a facet in MASS
        will be moved. If you want to move an earlier version, specify
        the version datestamp (str, YYYYMMDD format).

        Arguments:
        filesets -- (drs.AtomicDatasetCollection) fileset(s) to move
        old_state -- (state.State) current state in MASS
        new_state -- (state.State) new state in MASS
        cmd_timestamp -- (str) date the original move was run (YYYYMMDD)

        Keyword arguments:
        version -- (str) version of facet(s) to move (YYYYMMDD format)
        """
        if not old_state.can_move_to(new_state):
            raise ValueError(
                "Cannot move from {old} to {new}".format(
                    old=old_state, new=new_state))
        (last_id, last_var) = self._find_last_successful(
            filesets, new_state, cmd_timestamp)
        # Finish off any remaining vars in the last successful id...
        drs_vars = filesets.drs_variables(last_id)
        if last_var != drs_vars[-1]:
            last_loc = drs_vars.index(last_var)
            for drs_var in drs_vars[last_loc + 1:]:
                facet = filesets.get_drs_facet_builder(last_id, drs_var)
                new_dir = self._run_move(
                    facet, old_state, new_state, timestamp=version)
                self.inform(facet, new_dir, new_state)
        dataset_ids = filesets.dataset_ids()
        if last_id == dataset_ids[-1]:
            # We have nothing else left to put.
            return
        last_loc = dataset_ids.index(last_id)
        for dataset_id in dataset_ids[last_loc + 1:]:
            for drs_var in filesets.drs_variables(dataset_id):
                drs_facet_builder = filesets.get_drs_facet_builder(
                    last_id, drs_var)
                new_dir = self._run_move(
                    drs_facet_builder, old_state, new_state, timestamp=version)
                self.inform(drs_facet_builder, new_dir, new_state)
        return

    def copy_from_mass(self, local_top, mass_dir, drs_facet_builder):
        """Copy a data set from MASS to local disk.

        Copies the specified facet from MASS to local disk. The
        expected location on local disk will be deduced using the DRS
        facets and your configuration.

        Arguments:
        local_top -- (str) path to top level directory on local disk
        mass_dir -- (str) path to directory containing data set
        drs_facet_builder -- (drs.DataRefSyntax) atomic data set to
        copy
        """
        mass_path = self._mass_path_to_match_drs_var(
            mass_dir, drs_facet_builder.facet_var)
        dest_dir = self._local_path_to_facet(local_top, drs_facet_builder)
        self._get_atom(mass_path, dest_dir)
        return

    def find_local_facets(self, local_directory, drs_fixed_facet_builder,
                          include_drs_facet_builder_list=None,
                          exclude_drs_facet_builder_list=None):
        """Search local directory tree for matching facets.

        Given a top-level directory and some fixed facets, searches
        the directory tree to find all the facets that match the fixed
        facet values. All the defined facets must match for a facet to
        be included in the results. You must define enough facets to
        enable a path to a local directory containing files to be
        deduced.

        If a list of "include_drs_facet_builder_list" facets is
        supplied, only facets that match one (or more) of the supplied
        "include_drs_facet_builder_list" facets will be included in the
        results.

        If a list of "exclude_drs_facet_builder_list" facets is
        supplied, any facet that matches one (or more) of the supplied
        "exclude_drs_facet_builder_list" facets will be removed from
        the results.

        You can supply both include_drs_facet_builder_list and
        exclude_drs_facet_builder_list lists, but you can't
        specify "include_drs_facet_builder_list" and
        "exclude_drs_facet_builder_list" matches against the same
        facet. For example, if you want to
        "include_drs_facet_builder_list" where "variable" is "tas" you
        can't exclude_drs_facet_builder_list facets using the DRS
        "variable" attribute.

        Returns a drs.AtomicDatasetCollection object.

        Arguments:
        local_directory -- (str) path to top-level local directory
        drs_fixed_facet_builder -- (drs.DataRefSyntax) facets to match

        Keyword arguments:
        include_drs_facet_builder_list -- (list of
        drs.DataRefSyntax objects) facet builder(s) to include
        exclude_drs_facet_builder_list -- (list of
        drs.DataRefSyntax objects) facet builder(s) to exclude
        """
        self._check_constraints_valid(drs_fixed_facet_builder,
                                      include_drs_facet_builder_list,
                                      exclude_drs_facet_builder_list)
        filesets_in_directory = self._find_all_local_facets(
            local_directory, drs_fixed_facet_builder)
        filtered_filesets = filesets_in_directory
        if include_drs_facet_builder_list:
            filtered_filesets = self._find_matches(
                filesets_in_directory, include_drs_facet_builder_list)
        if exclude_drs_facet_builder_list:
            filtered_filesets = self._remove_excluded(
                filtered_filesets, exclude_drs_facet_builder_list)
        return filtered_filesets

    def find_mass_facets(self, drs_fixed_facet_builder, state,
                         include_drs_facet_builder_list=None,
                         exclude_drs_facet_builder_list=None):
        """Search MASS directory tree for matching facet(s).

        Given some fixed DRS facets and a state, deduces the MASS
        directory tree to search and does a recursive listing, finding
        all the facets that match the fixed values and (optionally)
        filtering further using include and/or exclude facets. All the
        facets defined in the fixed facet object must match for a
        facet to be included in the results.

        If a list of "include" facets is supplied, only facets that
        match one (or more) of the supplied "include" facets will be
        included in the results.

        If a list of "exclude" facets is supplied, any facet that
        matches one (or more) of the supplied "exclude" facets will be
        removed from the results.

        You can supply both include and exclude lists, but you can't
        use the same DRS facet in both. For example, if you "include"
        facets by specifying the DRS "variable" to match, you can't
        also "exclude" facets by DRS variable.

        Returns a drs.AtomicDatasetCollection object.

        Arguments:
        drs_fixed_facet_builder -- (drs.DataRefSyntax) facets to match
        state -- (state.State) state to match

        Keyword arguments:
        include_drs_facet_builder_list -- (list of drs.DataRefSyntax
        objects) facet(s) to include
        exclude_drs_facet_builder_list -- (list of drs.DataRefSyntax
        objects) facet(s) to exclude
        """
        self._check_constraints_valid(drs_fixed_facet_builder,
                                      include_drs_facet_builder_list,
                                      exclude_drs_facet_builder_list)
        facets_in_directory = self._find_all_mass_facets(
            drs_fixed_facet_builder, state)
        filtered = facets_in_directory
        if include_drs_facet_builder_list:
            include_with_state = self._add_state(
                include_drs_facet_builder_list, state)
            filtered = self._find_matches(
                facets_in_directory, include_with_state)
        if exclude_drs_facet_builder_list:
            exclude_with_state = self._add_state(
                exclude_drs_facet_builder_list, state)
            filtered = self._remove_excluded(filtered, exclude_with_state)
        return filtered

    def filter_facets(self, filesets, drs_fixed_facet_builder,
                      include_drs_facet_builder_list=None,
                      exclude_drs_facet_builder_list=None):
        """Filter filesets.

        Filter supplied filesets to find all the filesets that match
        the supplied fixed facets.
        All the fixed facets must match for a fileset to be included in
        the output.

        If a list of "include" facet builders is supplied, only
        filesets that match one (or more) of the supplied "include"
        facet builders will be included in the results.

        If a list of "exclude" facet builders is supplied, any fileset
        that matches one (or more) of the supplied "exclude" facet
        builders will be removed from the results.

        You can supply both include and exclude lists, but you can't
        use the same DRS facet builder in both. For example, if you
        "include" filesets by specifying the DRS "variable" to match,
        you can't also "exclude" filesets by DRS variable.

        Returns a drs.AtomicDatasetCollection object.

        Arguments:
        filesets -- (drs.AtomicDatasetCollection) filesets to filter
        drs_fixed_facet_builder -- (drs.DataRefSyntax) facets to match

        Keyword arguments:
        include_drs_facet_builder_list -- (list of drs.DataRefSyntax
        objects) facet_builder(s) to include
        exclude_drs_facet_builder_list -- (list of drs.DataRefSyntax
        objects) facet_builder(s) to exclude
        """
        self._check_constraints_valid(drs_fixed_facet_builder,
                                      include_drs_facet_builder_list,
                                      exclude_drs_facet_builder_list)
        results = drs.AtomicDatasetCollection()
        for fileset in filesets:
            if fileset.matches(drs_fixed_facet_builder):
                results.add(fileset)
        if include_drs_facet_builder_list:
            results = self._find_matches(results,
                                         include_drs_facet_builder_list)
        if exclude_drs_facet_builder_list:
            results = self._remove_excluded(results,
                                            exclude_drs_facet_builder_list)
        return results

    def inform(self, drs_facet_builder, mass_dir, state):
        """Sends a message to BADC, if necessary.

        Constructs and sends a message to BADC to inform them that
        facet has gone into MASS in the specified state. Note: if
        state is one that BADC aren't interested in, no message is
        sent.

        Arguments:
        drs_facet_builder -- (drs.DataRefSyntax) facet to send message
        about
        mass_dir -- (str) path to facet in MASS
        state -- (state.State) state of facet in MASS
        """
        if state.inform():
            message = self._prepare_message(drs_facet_builder, mass_dir,
                                            state)
            if self._simulation:
                logging.info("Simulating publishing message changing state "
                             "to \"{}\". Message contents: \"{}\""
                             "".format(state, repr(message.content)))
            else:
                if self._comm is None:
                    self._comm = msg.Communication(self._config)
                message_sent = self._comm.publish_message(message)
                logging.info(
                    "State change to \"{}\", message published \"{}\"".format(
                        state, message_sent))
        return

    def serialise_facets(self, filesets):
        """Convert filesets to a simpler form that can be saved to a file.

        Returns a representation of the supplied facets as a str in
        JSON format.

        Arguments:
        filesets -- (drs.AtomicDatasetCollection) filesets to serialise
        """
        serialisable = []
        for fileset in filesets:
            serial = fileset.serialisable_form()
            serialisable.append(serial)
        return json.dumps(serialisable)

    def expand_facets(self, serialised):
        """Convert serialised JSON back into fileset(s).

        Returns a drs.AtomicDatasetCollection object representing the
        fileset(s) contained in the input JSON string.

        Arguments:
        serialised -- (str) Serialised facets in JSON format
        """
        filesets = drs.AtomicDatasetCollection()
        serialisable_filesets = json.loads(serialised)
        for serial in serialisable_filesets:
            drs_facet_builder = drs.DataRefSyntax(self._config, self._project)
            drs_facet_builder.fill_facets_from_serialisable(serial)
            filesets.add(drs_facet_builder)
        return filesets

    def _find_files(self, local_directory, drs_fixed_facet_builder):
        """
        Return a dictionary of file names : path name found in the
        local directory using
        the sublocal structure defined in the configuration file.
        At the same time build up a dictionary relating the
        table_id,variable combination to the stream.

        Arguments:
        local_directory -- (str) local directory to search
        drs_fixed_facet_builder -- (drs.DataRefSyntax) Fixed facets to
        use.
        """
        local_path = drs_fixed_facet_builder.local_dir(local_directory)
        if 'sublocal' not in drs_fixed_facet_builder._project_config:
            return os.listdir(local_path)
        files, sub_local_facets_for_stream = search_local_directories(
            drs_fixed_facet_builder, local_path)
        self._stream.update(sub_local_facets_for_stream)
        return files

    def _find_all_local_facets(self, local_directory, drs_fixed_facet_builder):
        """
        Return an AtomicDatasetCollection built from the files found
        in local_directory that match the fixed facet provided.
        """
        results = drs.AtomicDatasetCollection()
        filenames = self._find_files(local_directory, drs_fixed_facet_builder)
        for filename, filepath in filenames.items():
            drs_facet_builder = drs.DataRefSyntax(self._config, self._project)
            drs_facet_builder.fill_facets_from_local_path(filepath)
            if drs_facet_builder.is_drs_name(filename):
                drs_facet_builder.fill_facets_from_drs_name(filename,
                                                            update=True)
                if drs_facet_builder.matches(drs_fixed_facet_builder):
                    results.add(drs_facet_builder, filename=filename)
        return results

    def _find_all_mass_facets(self, drs_fixed_facet_builder, state):
        results = drs.AtomicDatasetCollection()
        fixed_with_state = copy.deepcopy(drs_fixed_facet_builder)
        fixed_with_state._state = state
        mass_path = self._mass_join([
            self._moo_top, drs_fixed_facet_builder.mass_max_path()])
        mass_tree = moo_cmd.ls_tree(mass_path, simulation=self._simulation)
        facets = self._mass_to_facets(mass_tree, state)
        for facet in facets:
            if facet.matches(fixed_with_state):
                results.add(facet)
        return results

    def _find_matches(self, filesets_to_filter,
                      include_drs_facet_builder_list):
        results = drs.AtomicDatasetCollection()
        for fileset in filesets_to_filter:
            for drs_facet_builder in include_drs_facet_builder_list:
                if fileset.matches(drs_facet_builder):
                    results.add(fileset)
        return results

    def _remove_excluded(self, filesets, exclude_drs_facet_builder_list):
        filtered = copy.deepcopy(filesets)
        for fileset in filesets:
            for drs_facet_builder in exclude_drs_facet_builder_list:
                if fileset.matches(drs_facet_builder):
                    filtered.discard(fileset)
        return filtered

    def _prepare_message(self, drs_facet_builder, mass_dir, state):
        """
        Construct the message to be sent.

        Parameters
        ----------
        drs_facet_builder : :class:`cdds_transfer.drs.DataRefSyntax`
            Facets
        mass_dir : str
            MASS URI to send in message
        state : :class:`cdds_transfer.state.State`
            New state of data set

        Returns
        -------
        : :class:`cdds_transfer.msg.MooseMessage`
            Message to be sent.
        """
        msg_content = {
            "mass_dir": mass_dir, "state": state.name(),
            "facets": drs_facet_builder.facets,
            "dataset_id": drs_facet_builder.dataset_id()
        }
        # The following is not ideal, but a signficant amount of effort
        # is needed to force all tests to use the facet "mip_era" rather than
        # "project". This should be picked up when we look at rewriting
        # cdds_transfer.
        if "mip_era" in drs_facet_builder.facets:
            msg_content["mip_era"] = drs_facet_builder.facets["mip_era"]
        else:
            msg_content["mip_era"] = drs_facet_builder.facets["project"]
        message = msg.MooseMessage(content=msg_content)
        return message

    def _latest_ts_for_state(self, drs_facet_builder, state):
        mass_dir = self._mass_path_to_state(drs_facet_builder, state)
        available = self._list_atoms(mass_dir, drs_facet_builder.facet_var)
        if len(available) == 0:
            raise ValueError("No directories found for \"{}/{}\""
                             "".format(state, drs_facet_builder.facet_var))
        sorted_ts = self._sorted_ts(available)
        return str(sorted_ts[-1])

    def _mass_to_facets(self, mass_tree, state):
        urls = self._parse_urls_from_xml(mass_tree)
        filesets = drs.AtomicDatasetCollection()
        for url in urls:
            drs_facet_builder = drs.DataRefSyntax(self._config, self._project)
            if not drs_facet_builder.mass_dir_contains_var_dir(url):
                # We're looking at a higher-level directory, so skip.
                continue
            drs_facet_builder.fill_facets_from_mass_dir(url)
            if drs_facet_builder.state != state:
                continue
            if drs_facet_builder.mass_dir_includes_file(url):
                filesets.add(drs_facet_builder, filename=url)
            else:
                filesets.add(drs_facet_builder)
        return filesets

    def _parse_urls_from_xml(self, mass_tree):
        content_handler = LsHandler()
        moo.parse_xml_output(mass_tree, content_handler)
        return content_handler.url

    def _run_put(self, local_top, drs_facet_builder, state, putter,
                 timestamp=None):
        (local_dir, mass_dir) = self._dirs_for_facet(
            local_top, drs_facet_builder, state, timestamp=timestamp)
        self._put_atom(drs_facet_builder, local_dir, mass_dir, putter)
        self.inform(drs_facet_builder, mass_dir, state)
        return

    def _run_move(self, drs_facet_builder, old_state, new_state,
                  timestamp=None):
        if timestamp:
            ts_to_move = timestamp
        else:
            ts_to_move = self._latest_ts_for_state(drs_facet_builder,
                                                   old_state)
        old_dir = self._mass_path_to_timestamp(drs_facet_builder, old_state,
                                               ts_to_move)
        new_dir = self._mass_path_to_timestamp(drs_facet_builder, new_state,
                                               ts_to_move)
        self._move_atom(old_dir, new_dir)
        return new_dir

    def _find_last_successful(self, filesets, state, timestamp):
        last_successful = (None, None)
        for fileset in filesets:
            mass_dir = self._mass_path_to_timestamp(
                fileset, state, timestamp=timestamp)
            if moo_cmd.dir_exists(mass_dir, simulation=self._simulation):
                last_successful = (fileset.dataset_id(), fileset.facet_var)
            else:
                break
        return last_successful

    def _put_atom(self, drs_facet_builder, local_dir, mass_dir, put_cmd):
        # Puts a set of files to a MOOSE directory. Tries to rollback
        # any MASS actions if commands fail and rollback is
        # appropriate.
        if not self._local_dir_exists(local_dir):
            raise IOError("Local directory \"{}\" doesn't exist"
                          "".format(local_dir))
        if not moo_cmd.dir_exists(mass_dir, simulation=self._simulation):
            # If mkdir fails, there isn't anything to tidy up and we
            # can't proceed, so we let the MassError ripple up if it
            # occurs.
            moo_cmd.mkdir(mass_dir, simulation=self._simulation)
        try:
            self._put_var(local_dir, drs_facet_builder, mass_dir, put_cmd)
        except moo.MassError:
            # If put fails mass_dir might be empty so we can try to
            # remove it to tidy up.
            moo_cmd.rmdir(mass_dir, simulation=self._simulation)
        return

    def _get_atom(self, mass_path, dest_dir):
        if not self._local_dir_exists(dest_dir):
            self._make_local_dir(dest_dir)
        transfer_threads = self._transfer_threads()
        logging.info("Starting moo get of \"{}\"".format(mass_path))
        moo_cmd.get(mass_path, dest_dir, transfer_threads,
                    simulation=self._simulation)
        self._log_get_files(mass_path, dest_dir)
        return

    def _move_atom(self, old_atom, new_atom):
        # Moves the files contained in directory old_atom on MASS to
        # new_atom. Tidies away (now empty) directory old_atom after
        # successful move.
        if not moo_cmd.dir_exists(new_atom, simulation=self._simulation):
            moo_cmd.mkdir(new_atom, simulation=self._simulation)
        moo_cmd.mv("{}/*".format(old_atom), new_atom,
                   simulation=self._simulation)
        moo_cmd.rmdir(old_atom, simulation=self._simulation)
        return

    def _list_atoms(self, mass_base, drs_var):
        # Lists all available directories under mass_base that match
        # drs_var.
        moo_pattern = self._mass_path_to_match_drs_var(mass_base, drs_var)
        dirs = moo_cmd.ls(moo_pattern, simulation=self._simulation)
        return dirs

    def _put_var(self, local_dir, drs_facet_builder, mass_dir, cmd_to_run):
        # Finds local files associated with facet and sends them to
        # MASS.
        local_pattern = self._local_path_to_match_drs_var(local_dir,
                                                          drs_facet_builder)
        to_put_file_list = glob.glob(local_pattern)
        self._log_put_files(to_put_file_list, local_dir, mass_dir)
        cmd_to_run(to_put_file_list, mass_dir, simulation=self._simulation)
        return

    def _dirs_for_facet(self, local_top, drs_facet_builder, state,
                        timestamp=None):
        local_dir = self._local_path_to_facet(local_top, drs_facet_builder)
        mass_dir = self._mass_path_to_timestamp(
            drs_facet_builder, state, timestamp=timestamp)
        return local_dir, mass_dir

    def _check_constraints_valid(self, drs_fixed_facet_builder,
                                 include_drs_facet_builder_list,
                                 exclude_drs_facet_builder_list):
        if self._constraints_overlap(drs_fixed_facet_builder,
                                     include_drs_facet_builder_list,
                                     exclude_drs_facet_builder_list):
            raise ValueError(
                "Include and exclude cannot contain the same facet")
        if self._filter_within_fileset(drs_fixed_facet_builder,
                                       include_drs_facet_builder_list,
                                       exclude_drs_facet_builder_list):
            raise ValueError("Cannot filter within a file-set")

    def _constraints_overlap(self, drs_fixed_facet_builder,
                             include_drs_facet_builder_list,
                             exclude_drs_facet_builder_list):
        include_constraints = self._distinct_constraints(
            drs_fixed_facet_builder, include_drs_facet_builder_list)
        exclude_constraints = self._distinct_constraints(
            drs_fixed_facet_builder, exclude_drs_facet_builder_list)
        return len(include_constraints & exclude_constraints) > 0

    def _filter_within_fileset(self, drs_fixed_facet_builder,
                               include_drs_facet_builder_list,
                               exclude_drs_facet_builder_list):
        return (drs_fixed_facet_builder.contains_sub_atomic_facet() or
                self._is_any_facet_sub_atomic(include_drs_facet_builder_list)
                or
                self._is_any_facet_sub_atomic(exclude_drs_facet_builder_list))

    def _distinct_constraints(self, drs_fixed_facet_builder,
                              constraining_drs_facet_builders_list):
        constraints = set([])
        if not constraining_drs_facet_builders_list:
            return constraints
        for drs_facet_builder in constraining_drs_facet_builders_list:
            for constraint in list(drs_facet_builder.facets.keys()):
                constraints.add(constraint)
        for constraint in list(drs_fixed_facet_builder.facets.keys()):
            constraints.discard(constraint)
        return constraints

    def _is_any_facet_sub_atomic(self, drs_facet_builder_list):
        if drs_facet_builder_list is None:
            return False
        for drs_facet_builder in drs_facet_builder_list:
            if drs_facet_builder.contains_sub_atomic_facet():
                return True
        return False

    def _add_state(self, drs_facet_builder_list, state):
        drs_facet_builder_with_state_list = []
        for drs_facet_builder in drs_facet_builder_list:
            drs_facet_builder_with_state = copy.deepcopy(drs_facet_builder)
            drs_facet_builder_with_state._state = state
            drs_facet_builder_with_state_list.append(
                drs_facet_builder_with_state)
        return drs_facet_builder_with_state_list

    # Private methods for building up MASS paths. They are build from
    # the following pieces:
    #
    # local config [mass] top_dir attribute (e.g. mass:/adhoc/projects/dds2)
    # facet.mass_base_dir() (e.g. geomip/output/MOHC/.../r1i1p1)
    # state.mass_dir() (e.g. "embargoed")
    # DRS variable name and timestamp (e.g. vo_20150324)
    #
    # The following methods build up paths to these various levels.
    #
    # MASS paths use "/" as a separator by definition, so we use
    # simple splits and joins on "/" rather than os.path.

    def _mass_join(self, path_elements):
        return "/".join(path_elements)

    def _mass_basename(self, mass_path):
        return mass_path.split("/")[-1]

    def _mass_path_to_facet(self, drs_facet_builder):
        return self._mass_join([self._moo_top, drs_facet_builder.mass_dir()])

    def _mass_path_to_state(self, drs_facet_builder, state):
        return self._mass_join(
            [self._mass_path_to_facet(drs_facet_builder), state.mass_dir()])

    def _mass_path_to_timestamp(self, drs_facet_builder, state,
                                timestamp=None):
        """
        Return the mass path including the timestamp component.

        Parameters
        ----------
        drs_facet_builder : :class:`cdds_transfer.drs.DataRefSyntax`
            Facets to interpolate into mass path.
        state : :class:`cdds_transfer.state.State`
            State, e.g. embargoed or available.
        timestamp : str, optional
            Timestamp to use. If not specified use today's date in form
            YYYYMMDD.

        Returns
        -------
        :str
            mass path including timestamp
        """
        if not timestamp:
            # Default to today's date.
            timestamp = date.today().strftime(VERSION_FORMAT_DATETIME)
        else:
            timestamp = VERSION_FORMAT.format(timestamp)
        path_to_var = self._mass_join(
            [self._mass_path_to_state(drs_facet_builder, state)])
        return os.path.join(path_to_var, timestamp)

    def _mass_path_to_match_drs_var(self, mass_dir, drs_var_name):
        return os.path.join(mass_dir, "*")

    def _ts_from_dir(self, dir_path):
        """
        Retrieve the timestamp string from the directory path supplied.

        Parameters
        ----------
        dir_path : str
            Directory path to search

        Returns
        -------
        : str
            time stamp

        Raises
        ------
        RuntimeError
            If a time stamp cannot be found.
        """
        directories = os.path.split(dir_path)
        timestamp = None
        for directory in directories:
            result = re.search(VERSION_TIMESTAMP_REGEX, directory)
            if result:
                timestamp = result.groups()[0]
        if timestamp is None:
            raise RuntimeError('Could not retrieve timestamp from dir_path '
                               '"{}"'.format(dir_path))
        return timestamp

    def _transfer_threads(self):
        try:
            max_transfer_threads = int(self._config.attr(
                "mass", "max_transfer_threads"))
        except Exception as exc:
            max_transfer_threads = 10
        return max_transfer_threads

    # Methods for deducing local paths.

    def _local_path_to_facet(self, local_top, drs_facet_builder):
        # Deduce the local directory path to the supplied facet.
        local_path = drs_facet_builder.local_dir(local_top)
        return local_path

    def _local_path_to_match_drs_var(self, local_dir, drs_facet_builder):
        # Builds a wildcard pattern match that will match all the
        # files in a local directory.
        facet_match = drs_facet_builder.pattern_for_var()
        if ('table_id' not in drs_facet_builder.facets or
                'variable' not in drs_facet_builder.facets):
            return os.path.join(local_dir, facet_match)
        sublocal_dirs = []
        stream_key = '{table_id},{variable}'.format(**drs_facet_builder.facets)
        for i in drs_facet_builder._project_config['sublocal'].split('|'):
            if i == 'stream':
                sublocal_dirs.append(self._stream[stream_key])
            else:
                sublocal_dirs.append(drs_facet_builder.facets[i])

        return os.path.join(local_dir,
                            os.path.join(*sublocal_dirs), facet_match)

    def _local_dir_exists(self, local_dir):
        return os.path.exists(local_dir)

    def _make_local_dir(self, local_dir):
        os.makedirs(local_dir)

    def _sorted_ts(self, ts_dir):
        mass_base = [self._mass_basename(d) for d in ts_dir]
        sortable_ts = [int(self._ts_from_dir(base)) for base in mass_base]
        return sorted(sortable_ts)

    # Logging.

    def _log_put_files(self, put_files, local_dir, mass_dir):
        logging.info(
            "Sending \"{}\" files from \"{}\" to \"{}\"".format(
                len(put_files), local_dir, mass_dir))
        for to_put in put_files:
            logging.info("  file \"{}\" size \"{}\"".format(
                to_put, os.path.getsize(to_put)))
        return

    def _log_get_files(self, mass_path, local_dir):
        mass_dir = os.path.dirname(mass_path)
        pattern = os.path.basename(mass_path)
        local_files = glob.glob(os.path.join(local_dir, pattern))
        logging.info(
            "Got \"{}\" files from \"{}\" to \"{}\"".format(
                len(local_files), mass_dir, local_dir))
        for got in local_files:
            logging.info("  file \"{}\" size \"{}\"".format(
                got, os.path.getsize(got)))
        return


class LsHandler(xml.sax.ContentHandler):

    def __init__(self):
        self._url = []

    @property
    def url(self):
        return self._url

    def startElement(self, name, attr):
        if name == "node":
            mass_url = attr.get("url", None)
            self._url.append(mass_url)


def search_local_directories(drs_fixed_facet_builder, local_path):
    """
    Return a dictionary describing files in the local directory that
    match the fixed facets and a dictionary relating the of the
    "sublocal" facets to the corresponding stream.

    Parameters
    ----------
    drs_fixed_facet_builder : :class:`cdds_transfer.drs.DataRefSyntax`
        Facets to match.
    local_path : str
        Local directory to search

    Returns
    -------
    : dict
        {filename : directory}
    : dict
        {comma separated sublocal facets : stream}
    """
    logger = logging.getLogger(__name__)
    sublocal_facet_names = drs_fixed_facet_builder._project_config[
        'sublocal'].split('|')
    files = {}
    sub_local_facets_for_stream = {}
    for dir_name, _, filenames in os.walk(local_path):
        if not filenames:
            # Only interested in files here
            continue
        sublocal_dir_names = os.path.relpath(dir_name, local_path).split('/')
        if len(sublocal_dir_names) != len(sublocal_facet_names):
            # If we don't have the right number of directory names skip on
            # after warning.
            logger.warning(
                'Could not match sub local facets "{}" with sub local '
                'directories "{}"'.format(
                    repr(sublocal_facet_names), repr(sublocal_dir_names)))
            continue
        sublocal_facets = {
            i: j for i, j in zip(sublocal_facet_names,
                                 sublocal_dir_names)}
        for filename in filenames:
            files[filename] = dir_name

        non_stream_sublocal_facets = ','.join(
            [sublocal_facets[i] for i in sublocal_facet_names
             if i != 'stream'])

        sub_local_facets_for_stream[non_stream_sublocal_facets] = \
            sublocal_facets['stream']
    return files, sub_local_facets_for_stream
