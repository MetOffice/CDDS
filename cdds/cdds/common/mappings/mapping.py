# (C) British Crown Copyright 2016-2022, Met Office.
# Please see LICENSE.rst for license details.
"""Convert the input request file into filters in the specified format,
using model to MIP mapping configuration files to find the mappings.

The input request file should be in JSON format and contain the
following:

  ``{"science": {"mip_era": "PROGRAMME_NAME", "model_id": "MODEL_NAME",
  "model_ver": "UM_VERSION"}, "variables": [{"name":
  "MIP_VARIABLE_NAME", "table": "MIP_TABLE_NAME"}]}``

For example:

  ``{"science": {"mip_era": "cmip6", "model_id": "UKESM1", "model_ver":
  "1.0"}, "variables": [{"name": "clt", "table": "Amon"},
  {"name": "rlus", "table": "Amon"}, {"name": "rsuscs", "table": "day"
  }]}``

``model_ver`` can be one of ``"1.0"`` for UKESM1.0, ``"2"`` for
HadGEM2 and ``"3.1"`` for HadGEM3.1.

The filters will be converted to JSON and written to the specified
output file. The general format of the output is:

  ``{"stream": [{"status": "ok", "table": "MIP_TABLE_NAME", "name":
  "MIP_VARIABLE_NAME", "constraint": [{CONSTRAINT1}, ...]}]}``

If a mapping for the MIP variable and table is found in the common
mapping file or in one of the model/MIP table mapping file, the
constraint(s) will be parsed and included in the list for the stream.
For example:

  ``{"apm": [{"status": "ok", "table": "Amon", "name": "clt",
  "constraint": [{"lbtim": "122", "stash": "m01s02i204"}]}]}``

If a mapping cannot be found, the dictionary for the variable will be
as follows:

  ``{"status": "unknown", "table": "MIP_TABLE_NAME", "name":
  "MIP_VARIABLE_NAME"}``

If a MIP table cannot be mapped to a stream, the variable(s) for that
table will be returned with a stream of "unknown". If the stream is
unknown but the variable has a mapping in the common mappings file, the
constraints from that mapping will be included.
"""
import argparse
import configparser
import json
import os.path

from cdds.common.mappings.ancils import remove_ancils_from_mapping
from cdds.common.plugins.plugins import PluginStore
import hadsdk
from hadsdk.common import check_file, compare_versions
from hadsdk.constants import NC_CONSTRAINT_NOT_FOR_MOOSE
from hadsdk.pp import PP_HEADER_CORRECTIONS, stash_to_int
import mip_convert.request as mip_request


def _as_constraints(mapping):
    """
    Return the terms needed for the mass filter from the
    |model to MIP mapping|.

    Parameters
    ----------
    mapping: :class:`new_variable.VariableModelToMIPMapping`
        The |model to MIP mapping| for the |MIP requested variable|.

    Returns
    -------
    list:
       The information needed to create a mass filter to extract
       the |input variable| from the |model output files| for the
       |MIP requested variable|.
    """

    result = [dict(_filter_constraints(loadable.constraints))
              for loadable in mapping.loadables]
    if (any("alev" in dim for dim in mapping.dimension) and
            "site" not in mapping.dimension):
        result.append({"stash": "m01s00i033"})
    return result


def _filter_constraints(constraints):
    """
    Return constraints that could be netCDF filters.

    Only constraints at the netCDF variable level should be filtered in
    MOOSE, not those that filter hyperslabs or sub sections of cubes.
    """
    return [constraint for constraint in constraints
            if constraint[0] not in NC_CONSTRAINT_NOT_FOR_MOOSE]


class ModelToMip(object):

    """Provide services to map a filter request into various formats.

    Parameters
    ----------
    to_map : dict
        Request in the following format:

          ``{"science": {"mip_era": "MIP_ERA", "model_ver":
          "UM_VERSION", "model_id": "MODEL_NAME"}, "variables": [{"name":
          "MIP_VARIABLE_NAME", "table": "MIP_TABLE"}]}``

        If you have a request file in JSON format, you can convert it
        to an appropriate dictionary by calling the
        :func:`read_request` function.
    """
    def __init__(self, to_map):
        self._to_map = to_map
        self._mip_era = self._to_map["science"]["mip_era"].upper()
        self._model_id = self._to_map["science"]["model_id"]
        plugin = PluginStore.instance().get_plugin()
        model_params = plugin.models_parameters(self._model_id)
        self._um_version = model_params.um_version
        # Work the PP_HEADER_CORRECTIONS into an easy to work with format;
        # a dictionary keyed by stash code, and all numbers have to be
        # converted to strings for comparison with the filters dictionary.
        corrections = PP_HEADER_CORRECTIONS
        self._fix_rules_by_stash = {
            stash: rule for stashcodes, rule in corrections.items()
            for stash in stashcodes}

    def mass_filters(self):
        """Return filters in MASS format.

        The example below shows typical return values for a request
        with a known mapping, an unknown mapping and a case where the
        stream can't be deduced.

        ``{"apa": [{"status": "ok", "table": "day", "name": "rsuscs",
        "constraint": [{"lbtim": "122", "stash": "m01s01i211"}]}],
        "apm": [{"status": "unknown", "table": "Amon", "name": "clt"}],
        "unknown": [{"status": "unknown", "table": "3hr",
        "name": "clt"}]}``

        Note that if a variable has a mapping in the "common mapping"
        configuration file, but the stream cannot be deduced from the
        MIP table, the entry for the variable in the ``unknown`` list
        will have the constraints derived from the common mapping.

        Returns
        -------
        dict
            Mapping request in MASS filter format.

        """
        vars_by_table = self._split_by_mip_table()
        filters = {}
        for mip_table in vars_by_table:
            model_mapping = self._mapping_for_model(mip_table)
            for variable_request in vars_by_table[mip_table]:
                variable_name = variable_request["name"]
                if "/" in variable_request["stream"]:
                    stream_name, substream = variable_request["stream"].split("/")
                else:
                    stream_name = variable_request["stream"]
                    substream = None

                if stream_name not in filters:
                    filters[stream_name] = []

                try:
                    variable_mapping = (
                        mip_request.get_variable_model_to_mip_mapping(
                            model_mapping, variable_name, mip_table))
                    # Remove ancillaries from mapping to avoid attempting
                    # to retrieve them from MASS.
                    variable_mapping = remove_ancils_from_mapping(
                        variable_mapping)
                except configparser.Error:
                    variable_mapping = None
                mapping = self._build_mapping(variable_name,
                                              mip_table,
                                              variable_mapping)
                if mapping["status"] != "unknown":
                    if substream is not None:
                        for constraint in mapping["constraint"]:
                            constraint["substream"] = substream
                    for constraint in mapping["constraint"]:
                        # hardcoded fixes to incorrect pressure level syntax
                        if "lbplev" in constraint:
                            constraint["lbuser_5"] = constraint["lbplev"]
                            del constraint["lbplev"]
                        # Apply the reverse of fixes that MIP Convert uses
                        if "stash" in constraint:
                            self._fix_pp_constraint(constraint)
                filters[stream_name].append(mapping)

        return filters

    @staticmethod
    def _build_mapping(variable_name, mip_table, variable_mapping):
        mapping = {"name": variable_name, "table": mip_table}
        if variable_mapping:
            mapping["constraint"] = _as_constraints(variable_mapping)
            mapping["status"] = variable_mapping.status
        else:
            mapping["status"] = "unknown"
        return mapping

    def _fix_pp_constraint(self, constraint):
        """
        Apply fixes to PP constraint using information from
        PP_HEADER_CORRECTIONS.

        Parameters
        ----------
        constraint : dict
            constraint to be fixed
        """
        stash = stash_to_int(constraint["stash"])
        if stash in self._fix_rules_by_stash:
            umver, fixes = self._fix_rules_by_stash[stash]
            # Check that this fix should be applied to this UM
            # version
            if compare_versions(self._um_version, umver):
                # For each change check that the filter already
                # contains the information in correct_values before
                # updating with raw_values (remember that this is the
                # reverse of the process that MIP Convert is applying).
                for raw_values, correct_values in fixes:
                    fix_required = True
                    for name, value in correct_values.items():
                        # Constraint and fix are the same type, but
                        # different values.
                        if (type(constraint[name]) == type(value) and
                                constraint[name] != value):
                            fix_required = False
                        # Constraint is list, but value is scalar
                        # (needed for clisccp).
                        if (isinstance(constraint[name], list) and
                                value not in constraint[name]):
                            fix_required = False
                    # Apply fix if needed
                    if fix_required:
                        for name in correct_values:
                            if isinstance(constraint[name], list):
                                index_to_change = constraint[name].index(
                                    correct_values[name])
                                constraint[name][index_to_change] = (
                                    raw_values[name])
                            else:
                                constraint.update(raw_values)

    @property
    def project(self):
        """
        The project id.

        Returns
        -------
        str
            The project id.

        """
        if "-TEST" in self._mip_era:
            return self._mip_era.replace("-TEST", "")
        return self._mip_era

    def _mapping_for_model(self, mip_table_id):
        mip_table_name = self.project + "_" + mip_table_id
        model_mapping = mip_request.get_model_to_mip_mappings(
            self._to_map["science"]["model_id"], mip_table_name)
        return model_mapping

    def _split_by_mip_table(self):
        variable_request_by_table = {}
        for variable_request in self._to_map["variables"]:
            mip_table = variable_request["table"]
            variable_name = variable_request["name"]
            stream = variable_request["stream"]
            try:
                variable_request_by_table[mip_table].append(
                    {"name": variable_name, "stream": stream})
            except KeyError:
                variable_request_by_table[mip_table] = [
                    {"name": variable_name, "stream": stream}]
        return variable_request_by_table

    @staticmethod
    def _path_to_streams_config():
        path = os.path.join(
            os.path.dirname(hadsdk.__file__), "streams.cfg")
        return path
