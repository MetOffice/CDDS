# (C) British Crown Copyright 2016-2025, Met Office.
# Please see LICENSE.md for license details.
import importlib
import os
import logging
import re

from cdds.deprecated.transfer import config, state


class DrsException(Exception):
    """Raise when an error is found with data ref syntax
    configuration.
    """
    pass


class DataRefSyntax(object):

    """Represents data reference syntax facets for a particular
    project.

    DRS facets are stored in a private dict. The keys are specified in
    the project's configuration file. Some facets may have fixed
    values (such as project name), some may be specified in file
    names, and some may be deduced using special handlers.

    You do not have to set values for all the possible facets in the
    object. For example, you may wish to create a DataRefSyntax object
    to use in a search and filter method, so you will only set the
    values you want to filter on and leave the other values free.

    Freshly-created objects have no facets defined. Facets can be set
    in various ways - see the "fill_facets_from_dict" methods below.
    The core method is "fill_facets_from_dict" which takes a dictionary
    as input. The other methods build the dictionary and call
    fill_facets_from_dict.

    The following may no longer be true;
    All the fill_facets_from_dict methods will first clean out any
    defined facets before doing a fill, so you can safely re-use a
    DataRefSyntax object inside a loop if you wish.

    Public methods:
    add_file -- adds a file to our atomic dataset
    basename -- return (system-independent) basename
    contains_sub_atomic_facet -- check if we have a "within dataset"
    facet
    dataset_id -- return DRS dataset id
    fill_facets_from_dict -- set facet values from an input dict
    fill_facets_from_drs_name -- set facet values from DRS-format file
    name
    fill_facets_from_local_path -- set facet values from a local path
    fill_facets_from_mass_dir -- set facet values from a MASS path
    fill_facets_from_message -- set facet values from a message
    fill_facets_from_serialisable -- set facet values from serialised
    facet
    is_drs_name -- check if supplied name is a DRS name for our project
    local_dir -- return path to facet on local directory
    local_list_pattern -- return wildcard pattern match for facets
    mass_dir -- return path to facet on MASS
    mass_dir_contains_var_dir -- check if MASS path contains DRS
    variable
    mass_dir_includes_file -- check if MASS path contains file
    mass_max_path -- build maximum possible MASS wildcard from facets
    matches -- check if supplied facet matches our facets
    mip_path_builder -- make a callable to return paths to MIP tables
    not_in_max_path -- find facets that aren't in maximum possible MASS
    path
    pattern_for_var -- return wildcard pattern match for atomic dataset
    remove_file -- removes a file from our atomic dataset
    serialisable_form -- return simple representation of object

    Properties:
    facet_var -- return the DRS variable name
    facets -- return all the defined facets
    state -- return the state in MASS
    files -- return the files in the atomic dataset
    """

    def __init__(self, cfg, project):
        """Create a DRS syntax object for the specified project.

        The configuration for the project is read and checked for
        consistency issues. No facets are defined at this point,

        Arguments:
        cfg: config.Config) 
            wrapper for configuration file(s)
        project: str
            Project name, must match section in configuration
        """
        self._cfg = cfg
        self._project = project
        self._facets = {}
        self._state = None
        self._files = []
        self._project_config = self._mandatory_section(project)
        self._option = self._optional_section("options")
        self._check_config_consistency()
        self._handlers = self._define_handlers()

    def mip_path_builder(self):
        """Return a callable that builds a path to a MIP table.

        If our project needs to parse MIP tables to deduce facet
        values, this method uses values supplied in the configuration
        file to create and return a callable that can build the path
        to a MIP table. If our project does not need MIP tables, a
        callable is built that returns None.
        """
        def no_mip(table_name):
            return None
        mip_config = self._optional_section("mip")
        if not mip_config:
            return no_mip
        try:
            top_dir = mip_config["top_dir"]
            sub_dir_template = mip_config["sub_dir"].split("|")
            sub_path = os.path.join(*sub_dir_template)
            table_file = mip_config["table_file"]

            def builder(table_name):
                return os.path.join(
                    top_dir, sub_path, table_file % table_name)
        except KeyError:
            builder = no_mip
        return builder

    def fill_facets_from_dict(self, facets_dict, update=False):
        """Fill DRS facets using values supplied in a dict by
        1. define any hard-coded facets (such as project name) and
        2. set facets using values supplied

        Parameters
        ----------
        facets_dict : dict
            facet values
        update : bool (optional)
            update rather than overwrite facets.

        Raises
        ------
        DrsException
            If invalid facets supplied
        """
        # There are cases where two different functions need to add to
        # the facets in this object without losing prior data
        if not update:
            self._init_facets()
        # Check facets supplied are valid
        valid_facets_set = self._valid_facets()
        for facet in facets_dict:
            if facet not in valid_facets_set:
                raise DrsException(
                    "Facet \"{}\" not in valid facet list".format(facet))
        # update facets
        self._facets.update(facets_dict)
        # Handle member id (sub_experiment_id-variant_label)
        if ('sub_experiment_id' in self._facets and (self._facets['sub_experiment_id'] != 'none')
                and (self._facets['sub_experiment_id'] not in self._facets['variant_label'])):
            new_variant_label = '{sub_experiment_id}-{variant_label}'.format(**self._facets)
            logger = logging.getLogger(__name__)
            logger.debug('Sub-experiment id found updating variant lable to "{}"'.format(new_variant_label))
            self._facets['variant_label'] = new_variant_label

        # Handlers are something that I do not believe are used in CDDS
        for handler in self._handlers:
            facets_dict = self._handlers[handler](
                self._facets, self.mip_path_builder())
            self._facets.update(facets_dict)
        # Again I do not believe that this code does anything.
        if self._check_vocab():
            if not self._passes_cv_check():
                raise DrsException("Fails CV check")
        return

    def fill_facets_from_drs_name(self, name, update=False):
        """Fill DRS facets using the values in a DRS-format file name.

        The supplied name will be split apart (on underscores) and the
        project-specific DRS name template will be used to associate
        values with facets.

        Parameters
        ----------
        name: str
            File name in DRS format.
        update: bool, optional
            update rather than overwrite facets

        Raises
        ------
        DrsException
            If mandatory facets appear to be missing from the supplied name.
        """
        if not self.is_drs_name(name):
            raise DrsException(
                "DRS name %s missing mandatory facets from template %s" % (
                    name, self._project_config["name"]))
        # remove extension
        name = os.path.splitext(name)[0]
        facets_in_name = name.split("_")
        template, _ = self._drs_file_template()
        facets = dict(list(zip(template, facets_in_name)))
        self.fill_facets_from_dict(facets, update=update)
        return


    def fill_facets_from_mass_dir(self, mass_dir, update=False):
        """Fill facets using values contained in a MASS path.

        The supplied MASS path is split into facets using "/" as a
        field separator and the project configuration to associate
        fields with facets.

        If the path includes a DRS variable name, the variable's state
        will also be deduced and set.

        Parameters
        ----------
        mass_dir: str
            MOOSE path.
        update: bool, optional
            update rather than overwrite facets
        """
        drs_facets = self._split_drs_dir(mass_dir)
        # identify sub_experiment_id from variant label
        if ('variant_label' in drs_facets) and ('-' in drs_facets['variant_label']):
            drs_facets['sub_experiment_id'] = drs_facets['variant_label'].split('-')[0]
        self.fill_facets_from_dict(drs_facets, update=update)
        if self.mass_dir_contains_var_dir(mass_dir):
            full_facets = self._split_full_dir(mass_dir)
            self._state = state.make_state(full_facets["state"])
        return

    def fill_facets_from_local_path(self, local_path, update=False):
        """Fill facets using values contained in a local path.

        Parameters
        ----------
        local_path: str
            local path
        update: bool, optional
            update rather than overwrite
        """
        base_name = os.path.basename(local_path)
        # We may have a filename in DRS format in base_name, or we may
        # have a parent directory.
        if self.is_drs_name(base_name):
            self.fill_facets_from_drs_name(base_name, update=update)
            return
        facets = self._split_local_dir(local_path)
        self.fill_facets_from_dict(facets, update=update)

    def fill_facets_from_message(self, message, update=False):
        """Fill facets from a msg.MooseMessage object.

        Given a message read from one of the MOOSE RabbitMQ queues, fill
        facets from the message contents.

        Parameters:
        message: msg.MooseMessage
            a message read from a MOOSE queue
        update: bool, optional
            update rather than overwrite
        """
        self.fill_facets_from_dict(message.facets, update=update)
        return

    def fill_facets_from_serialisable(self, serialisable, update=False):
        """Fill facets from a serialised representation of a DRS object.

        Sometimes it is useful to flatten a DataRefSyntax object and
        save it to a file (for example, if an AtomicDatasetCollection
        is serialised). This method takes a "flattened" object and
        fills facets from it.

        arameters
        ---------
        serialisable: dict
            serialised representation of a DataRefSyntax object.
        update: bool, optional
            update rather than overwrite
        """
        if not isinstance(serialisable, dict):
            raise TypeError("fill_facets_from_serialisable expects a dict")
        if "drs" not in serialisable:
            raise DrsException(
                "Invalid dict supplied to fill_facets_from_serialisable")
        serial = serialisable["drs"]
        self.fill_facets_from_dict(serial["facets"], update=update)
        if "state" in serial:
            self._state = state.make_state(serial["state"])
        if "files" in serial:
            self._files = list(serial["files"])
        return

    def matches(self, facet_builder_to_match):
        """Return True if my facets match the supplied facets.

        This method compares the supplied facets (which may be a
        subset of the facets defined in the current object) with our
        facets. If all the supplied facets are the same as our
        internal equivalents, we return True. If not, we return False.

        Note: MASS facets with a defined state also have their states
        compared as part of the "matches" check.

        Parameters
        ----------
        facet_builder_to_match: drs.DataRefSyntax
            facets to compare with our values
        """
        matches = True
        if facet_builder_to_match.state != self.state:
            return False
        facets_to_match_dict = facet_builder_to_match.facets
        for attr in facets_to_match_dict:
            if self._facets[attr] != facets_to_match_dict[attr]:
                matches = False
                break
        return matches

    def is_drs_name(self, name):
        """Return True if name appears to be a DRS-format file name.

        Using the supplied project configuration, this method checks
        that the supplied file name contains enough facets to set all
        the mandatory project facets. At the moment this is done with
        a simple count - as controlled vocabularies are defined, a
        more thorough check will become possible.

        Parameters:
        name: str
            a file basename
        """
        facets_in_name = name.split("_")
        template, optional = self._drs_file_template()
        mandatory = set(template) - optional
        if len(facets_in_name) < len(mandatory):
            return False
        return True

    def contains_sub_atomic_facet(self):
        """Return True if one of our defined facets is only available
        at the filename level in a DRS structure. (For example, the
        "date" facet in CMIP5 only occurred in filenames and wasn't
        used to build directory paths to atomic datasets, or to build
        dataset ids.)
        """
        atomic_facets = self._split_template("atomic")
        for facet in self.facets:
            if facet not in atomic_facets:
                return True
        return False

    def serialisable_form(self):
        """Return a representation of the current object that can
        safely be stored to a file for later restoration. Returns a
        representation of the current object and the objects it
        contains as a dict.
        """
        serialisable = {"drs": {"facets": self.facets}}
        if self.state:
            serialisable["drs"]["state"] = self.state.name()
        if self.files:
            serialisable["drs"]["files"] = self.files
        return serialisable

    def basename(self, full_path):
        """Return the base name of the supplied full path.

        Parameters
        ----------
        full_path: str
            Full MASS or local disk path.
        """
        if re.match("moo(se)?:", full_path):
            return full_path.split("/")[-1]
        else:
            return os.path.basename(full_path)

    def local_dir(self, local_top):
        """Return the expected local path for this facet.

        Parameters
        ----------
        local_top: str
            Top-level directory path.
        """
        path = self._template_to_path("local")
        local_base = self._cfg.optional_attr("local", "base_dir")
        if local_base:
            path.append(local_base)
        return os.path.join(local_top, *path)

    def mass_dir(self):
        """Return the expected MASS directory for this facet."""
        path = self._template_to_path("mass")
        return "/".join(path)

    def dataset_id(self):
        """Return the dataset id for this facet."""
        path = self._template_to_path("dataset_id")
        return ".".join(path)

    def mass_max_path(self):
        """Return the maximum permissible MASS path with our defined
        facets. MASS does not permit wildcards in list commands
        anywhere except the end of the supplied URL. This method will
        use the defined facets in the object to build the longest
        possible MASS path it can as a string.
        """
        template = self._mandatory_attribute("mass")
        possible_mass_facets = template.split("|")
        path = []
        for facet in possible_mass_facets:
            try:
                path.append(self._facets[facet])
            except KeyError:
                break
        return "/".join(path)

    def not_in_max_path(self):
        """Return defined facets that could not be included in the
        maximum MASS path.

        MASS does not permit wildcard characters in list commands
        anywhere except at the end of the URL. As a result, filtering
        code needs to 1) build up the maximum possible path it can
        using our defined facets and later on it 2) needs to filter on
        our defined facets that couldn't be included in the maximum
        MASS path. This methods returns the "not in MASS max path"
        facets as a dict.
        """
        possible_mass_facets = self._split_template("mass")
        # Take a copy of the facet dictionary
        not_in_mass_max = dict(self._facets)
        for facet in self._facets:
            if facet not in possible_mass_facets:
                del not_in_mass_max[facet]
        # MASS max path is built up by stepping through the possible
        # MASS facets in order until there's one we don't have a value
        # for. We can use the same loop knowing that we can return all
        # our remaining "possible MASS facets" as soon as we hit the
        # first "unknown facet" situation.
        for facet in possible_mass_facets:
            try:
                del not_in_mass_max[facet]
            except KeyError:
                return not_in_mass_max
        return not_in_mass_max

    def pattern_for_var(self):
        """Return a wildcard pattern match that will match files
        belong to my DRS variable (as a str). The pattern will match
        file basenames only.
        """
        path = self._template_to_path("pattern")
        pattern = "_".join(path)
        return pattern + "_*"

    def mass_dir_contains_var_dir(self, mass_dir):
        """Return True if MASS path includes a "var_timestamp"
        directory.

        Parameters
        ----------
        mass_dir: str
            MASS path.
        """
        full_facets = self._split_full_dir(mass_dir)
        # TODO: obliterate this as "var_timestamp" is no more
        return "var_timestamp" in full_facets

    def mass_dir_includes_file(self, mass_dir):
        """Return True if MASS path includes a file name.

        Parameters
        ----------
        mass_dir: str
            MASS path.
        """
        full_facets = self._split_full_dir(mass_dir)
        if "drs_file" in full_facets:
            return full_facets["drs_file"] != ""
        else:
            return False

    def add_file(self, full_path):
        """Add a file to the list of files contained in our atomic
        dataset.

        Parameters
        ----------
        full_path: str
            Full path to the file to be added (MASS or local)
        """
        base = self.basename(full_path)
        self._files.append(base)
        return

    def remove_file(self, filename):
        """Remove a file from the list of files in our atomic dataset.
        Note, this removes the file from the internal list, but does
        not physically remove the file from local disk or MASS.

        Parameters
        ----------
        filename: str
            path to file to be removed
        """
        basename = self.basename(filename)
        try:
            self._files.remove(basename)
        except ValueError:
            pass

    @property
    def facet_var(self):
        """Return the DRS variable name."""
        return self._facets["variable"]

    @property
    def facets(self):
        """Return all the defined DRS facets (as a dict)."""
        return self._facets

    @property
    def state(self):
        """Return the state of the facet in MASS (state.State)."""
        return self._state

    @property
    def files(self):
        """Return the list of files in the atomic dataset (list of
        strings).
        """
        return self._files

    def _init_facets(self):
        # Cleans out any defined facets and then fills in any facets
        # that are defined in the project configuration (e.g. institute).
        self._facets = {}
        self._fill_predefined_facets()
        return

    def _check_config_consistency(self):
        # Splits apart the defined attributes in the project configuration and
        # checks that all the resulting facets are included in the "valid"
        # facet set.
        if "valid" not in self._project_config:
            raise DrsException("No definition of valid facets found")
        valid_facets_set = self._valid_facets()
        facets_mentioned_set = set([])
        for attr in self._project_config:
            if attr == "valid" or attr in valid_facets_set:
                continue
            facets = re.split("[|]", self._project_config[attr])
            for facet in facets:
                # Strip off "optional" markers around facet name.
                tidy_facet = re.sub(r"[[\]]", "", facet)
                facets_mentioned_set.add(tidy_facet)
        # We can have valid facets that aren't used in our config, but
        # we mustn't refer to facets unless they're in valid_facets.
        if not facets_mentioned_set.issubset(valid_facets_set):
            raise DrsException(
                "Configuration contains invalid facets \"{}\"".format(
                    list(facets_mentioned_set - valid_facets_set)))
        return

    def _fill_predefined_facets(self):
        valid_facets_set = self._valid_facets()
        for attr in self._project_config:
            if attr in valid_facets_set:
                self._facets[attr] = self._project_config[attr]
        return

    def _define_handlers(self):
        # Pulls in locally-defined handlers for deriving custom facets.
        handlers = {}
        handler_cfg = self._optional_section("handlers")
        if len(handler_cfg) == 0:
            return handlers
        try:
            handler_lib = handler_cfg["handler_lib"]
            del handler_cfg["handler_lib"]
        except KeyError:
            raise DrsException(
                "Must define hander_lib if you supply handlers")
        pkg = importlib.import_module('cdds.deprecated.transfer.{}'.format(handler_lib))
        try:
            local_config = pkg.LocalConfig(self._cfg)
        except config.ConfigError as exc:
            raise DrsException("Error in handler configuration: %s" % exc)
        for handler in handler_cfg:
            handlers[handler] = getattr(local_config, handler_cfg[handler])
        return handlers

    def _drs_file_template(self):
        template = self._mandatory_attribute("name")
        expected = template.split("|")
        allowed = []
        optional = set([])
        for attr in expected:
            is_optional = re.match(r"\[(.*)\]$", attr)
            if is_optional:
                optional.add(is_optional.group(1))
                allowed.append(is_optional.group(1))
            else:
                allowed.append(attr)
        return allowed, optional

    def _passes_cv_check(self):
        # Stub - waiting on controlled vocabs to be finalised.
        return True

    def _split_template(self, template_attr):
        template = self._mandatory_attribute(template_attr)
        return template.split("|")

    def _template_to_path(self, template_attr):
        template_facets = self._split_template(template_attr)
        path = []
        for facet in template_facets:
            try:
                path.append(self._facets[facet])
            except KeyError:
                raise DrsException(
                    "Missing facet %s needed to build path" % facet)
        return path

    def _lstrip_mass_top_dir(self, mass_dir):
        mass_top = self._cfg.attr("mass", "top_dir")
        return re.sub("^%s/" % mass_top, "", mass_dir)

    def _mandatory_section(self, section):
        try:
            return self._cfg.section(section)
        except config.ConfigError:
            raise DrsException(
                "No configuration found for mandatory section %s" % section)

    def _optional_section(self, section):
        try:
            return self._cfg.section(section)
        except config.ConfigError:
            return {}

    def _mandatory_attribute(self, attr):
        try:
            return self._project_config[attr]
        except KeyError:
            raise DrsException(
                "Missing required attribute %s from config" % attr)

    def _valid_facets(self):
        valid = self._project_config["valid"].split("|")
        return set(valid)

    def _split_drs_dir(self, mass_dir):
        mass_dir = self._lstrip_mass_top_dir(mass_dir)
        mass_facets = mass_dir.split("/")
        template_facets = self._split_template("mass")
        return dict(list(zip(template_facets, mass_facets)))

    def _split_full_dir(self, mass_dir):
        mass_dir = self._lstrip_mass_top_dir(mass_dir)
        template_facets = self._complete_mass_template()
        mass_facets = mass_dir.split("/")
        return dict(list(zip(template_facets, mass_facets)))

    def _split_local_dir(self, local_dir):
        """Return a dictionary of facets derived from the local directory
        based upon the config information and the local and sublocal
        facet templates

        Parameters
        ----------
        local_dir : str
            local directory

        Returns
        -------
        dict
            Facets derived from local_dir
        """
        local_top = self._cfg.attr("local", "top_dir")
        relative_local = os.path.relpath(local_dir, local_top)

        template_facets = self._split_template("local")
        local_base = self._cfg.optional_attr("local", "base_dir")
        if local_base:
            template_facets.append(local_base)
        template_facets += self._split_template("sublocal")

        local_facets = relative_local.split("/")
        result = dict(list(zip(template_facets, local_facets)))
        del result[local_base]
        return result

    def _complete_mass_template(self):
        # Adds non-DRS parts to the project template (such as state
        # and variable_timestamp).
        template_facets = self._split_template("mass")
        # TODO: remove var_timestamp
        template_facets += ["state", "var_timestamp", "drs_file"]
        return template_facets

    def _check_vocab(self):
        return ("check_vocab" in self._option and
                self._option["check_vocab"] == "True")

    def __deepcopy__(self, memo):
        result = DataRefSyntax(self._cfg, self._project)
        result.fill_facets_from_dict(self._facets)
        if self._state:
            result._state = state.make_state(self._state.name())
        result._files = list(self._files)
        return result

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (
                self._project_config == other._project_config and
                self.facets == other.facets and
                self.state == other.state and
                self.files == other.files)
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return "facets: %s, state: %s, files: %s" % (
            self._facets, self._state, self._files)


class AtomicDatasetCollection(object):

    """Represents a collection of facets.

    Maintains a dictionary of atomic datasets, keyed by dataset id and DRS
    variable names.

    Public methods:
    add -- add a facet to collection
    discard -- remove a facet from collection
    dataset_ids -- return list of dataset ids in collection
    drs_variables -- return DRS variables for specified dataset id
    get_drs_facet_builder -- return facet builder for dataset id and
    DRS variable
    facets -- return a list of all facets
    filenames -- return filenames contained in specified facet
    serialise_facets -- return our facets in a serialised form
    total_files_in_id -- returns the number of files contained in id
    total_files_in_atomic_dataset -- returns the total number of files
    """

    def __init__(self):
        # _atoms dictionary will have structure
        # {dataset_id: {facet_var name : drs_facet_builder}}
        self._atoms = {}

    def add(self, drs_facet_builder, filename=None):
        """Add a facet builder to collection.

        If filename is specified, it will be added to the list of files
        contained in the atomic dataset.

        Parameters
        ----------
        drs_facet_builder: drs.DataRefSyntax
            facet to add
        filename: str
            DRS filename
        """
        dataset_id = drs_facet_builder.dataset_id()
        if dataset_id in self._atoms:
            if drs_facet_builder.facet_var not in self._atoms[dataset_id]:
                self._atoms[dataset_id][
                    drs_facet_builder.facet_var] = drs_facet_builder
        else:
            self._atoms[dataset_id] = {
                drs_facet_builder.facet_var: drs_facet_builder}
        if filename:
            self._atoms[dataset_id][drs_facet_builder.facet_var].add_file(
                filename)
        return

    def discard(self, drs_facet_builder, filename=None):
        """Remove a facet builder from collection.

        If the collection contains a facet that matches the supplied facet,
        it will be removed from the collection. If a filename is supplied it
        will be removed from the list of filenames.

        parameters
        ----------
        drs_facet_builder: drs.DataRefSyntax
            facet to remove
        filename: str
            DRS filename.
        """
        dataset_id = drs_facet_builder.dataset_id()
        if dataset_id in self._atoms:
            if drs_facet_builder.facet_var in self._atoms[dataset_id]:
                if filename:
                    self._atoms[dataset_id][
                        drs_facet_builder.facet_var].remove_file(filename)
                else:
                    del self._atoms[dataset_id][drs_facet_builder.facet_var]
                if len(self._atoms[dataset_id]) == 0:
                    del self._atoms[dataset_id]
        return

    def dataset_ids(self):
        """Return a sorted list of dataset ids in collection."""
        return sorted(self._atoms.keys())

    def drs_variables(self, dataset_id):
        """Return a sorted list of DRS variable names in specified id.

        Parameters
        ----------
        dataset_id: str
            DRS dataset id
        """
        return sorted(self._atoms[dataset_id].keys())

    def get_drs_facet_builder(self, dataset_id, drs_variable):
        """Return drs_facet_builder for specified dataset id and DRS
        variable name.

        Parameters
        ----------
        dataset_id: str
            dataset id
        drs_variable: str
            DRS variable name
        """
        return self._atoms[dataset_id][drs_variable]

    def get_drs_facet_builder_list(self):
        """Return the drs_facet_builders we contain as a list."""
        facets = []
        for dataset_id in self.dataset_ids():
            for drs_var in self.drs_variables(dataset_id):
                facets.append(self.get_drs_facet_builder(dataset_id, drs_var))
        return facets

    def filenames(self, dataset_id, drs_variable):
        """Return a sorted list of filenames in the selected atomic dataset.

        Parameters
        ----------
        dataset_id: str
            dataset id
        drs_variable: str
            DRS variable name
        """
        return sorted(self._atoms[dataset_id][drs_variable].files)

    def total_files_in_id(self, dataset_id):
        """Return the total number of files in the dataset id.

        Parameters
        ----------
        dataset_id: str
            dataset id
        """
        total_files = 0
        if dataset_id in self._atoms:
            for drs_variable in self.drs_variables(dataset_id):
                total_files += self.total_files_in_atomic_dataset(
                    dataset_id, drs_variable)
        return total_files

    def total_files_in_atomic_dataset(self, dataset_id, drs_variable):
        """Return the total number of files in the atomic dataset.

        Parameters
        ----------
        dataset_id: str
            dataset id
        drs_variable: str
            DRS variable name
        """
        try:
            total_files = len(self.filenames(dataset_id, drs_variable))
        except KeyError:
            total_files = 0
        return total_files

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (self.get_drs_facet_builder_list() ==
                    other.get_drs_facet_builder_list())
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __iter__(self):
        self._ds_idx = 0
        self._var_idx = 0
        self._ds = self.dataset_ids()
        if len(self._ds) > 0:
            self._drs_vars = self.drs_variables(self._ds[self._ds_idx])
        return self

    def __next__(self):
        if len(self._atoms) == 0:
            raise StopIteration
        if self._ds_idx < len(self._ds):
            facet = self.get_drs_facet_builder(
                self._ds[self._ds_idx], self._drs_vars[self._var_idx])
            self._var_idx += 1
            if self._var_idx >= len(self._drs_vars):
                self._ds_idx += 1
                if self._ds_idx < len(self._ds):
                    self._var_idx = 0
                    self._drs_vars = self.drs_variables(self._ds[self._ds_idx])
            return facet
        else:
            raise StopIteration


def filter_filesets(atomic_dataset_collection, variables_to_operate_on):
    """Remove variables in the specifed atomic dataset collection that are
    not specified in the `variables_to_operate_on` list.

    Parameters
    ----------
    atomic_dataset_collection: \
        :class:`cdds.deprecated.transfer.drs.AtomicDatasetCollection`
        Dataset collection to filter
    variables_to_operate_on : list of tuples
        Variables that should be allowed to remain in the
        `atomic_dataset_collection`. All others will be removed.
    """
    logger = logging.getLogger(__name__)
    for drs_facet_builder in atomic_dataset_collection:
        key = (drs_facet_builder.facets['table_id'],
               drs_facet_builder.facets['variable'])
        if key not in variables_to_operate_on:
            logger.info('Dataset "{}/{}" not included in variables list. '
                        'Skipping.'.format(*key))
            atomic_dataset_collection.discard(drs_facet_builder)
