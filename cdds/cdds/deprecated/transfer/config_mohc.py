# (C) British Crown Copyright 2016-2025, Met Office.
# Please see LICENSE.md for license details.
from mip_convert import mip_parser
from cdds.deprecated.transfer.drs import DrsException


class LocalConfig(object):

    """Define methods to build custom facets.

    Note: local handlers can be called on partial facets (for example,
    facets that are being defined for filtering, where only certainly facets
    are defined). As a result all the handlers fail safe and return empty
    dicts if they can't deduce a facet's value.

    Public methods:
    driving_model -- deduce driving model from GCM model name
    experiment_domain -- join experiment and domain
    gcm_model_name -- deduce GCM model name
    mip_frequency -- parse MIP table to deduce frequency
    mip_realm -- parse MIP table to deduce realm
    split_rcm_model_name -- deduce model name from RCM model name
    """

    def __init__(self, config):
        """Create local handlers.

        Argument:
        config -- config.Config object
        """
        self._cfg = config

    def mip_frequency(self, facets, mip_path_builder):
        """Parse MIP table and return frequency.

        Arguments:
        facets -- (dict) DRS facets
        mip_path_builder -- (method) build path to MIP table
        """
        mip = self._mip_attrs(facets, mip_path_builder)
        try:
            result = {"frequency": mip["atts"]["frequency"]}
        except KeyError:
            result = {}
        return result

    def mip_realm(self, facets, mip_path_builder):
        """Parse MIP table and return realm.

        Arguments:
        facets -- (dict) DRS facets
        mip_path_builder -- (method) build path to MIP table
        """
        mip = self._mip_attrs(facets, mip_path_builder)
        try:
            result = {"realm": mip["atts"]["modeling_realm"]}
        except KeyError:
            result = {}
        return result

    def split_rcm_model_name(self, facets, mip_path_builder):
        """Deduce model name from RCM model name.

        Arguments:
        facets -- (dict) DRS facets
        mip_path_builder -- (method) build path to MIP table
        """
        try:
            model = facets["rcmModelName"].split("-")[1:]
            result = {"model": "-".join(model)}
        except (KeyError, IndexError):
            result = {}
        return result

    def experiment_domain(self, facets, mip_path_builder):
        """Make experiment_domain from facets.

        Arguments:
        facets -- (dict) DRS facets
        mip_path_builder -- (method) build path to MIP table
        """
        try:
            result = {
                "experimentDomain": "_".join(
                    [facets["experiment"], facets["domain"]])}
        except KeyError:
            result = {}
        return result

    def gcm_model_name(self, facets, mip_path_builder):
        """Deduce GCM model name from driving model.

        Arguments:
        facets -- (dict) DRS facets
        mip_path_builder -- (method) build path to MIP table
        """
        try:
            if facets["drivingModel"] != "ERAINT":
                raise DrsException(
                    "Can't deduce institute for driving model %s" %
                    facets["drivingModel"])
            result = {
                "gcmModelName": "ECMWF-{driving_model}".format(
                    driving_model=facets["drivingModel"])}
        except KeyError:
            result = {}
        return result

    def driving_model(self, facets, mip_path_builder):
        """Deduce driving model from GCM model name.

        Arguments:
        facets -- (dict) DRS facets
        mip_path_builder -- (method) build path to MIP table
        """
        if "drivingModel" in facets:
            result = {}
        else:
            try:
                result = {
                    "drivingModel": facets["gcmModelName"].split("-")[1]}
            except (KeyError, IndexError):
                result = {}
        return result

    def _mip_attrs(self, facets, mip_path_builder):
        try:
            mip_path = mip_path_builder(facets["mip"])
            result = mip_parser.parseMipTable(mip_path)
        except KeyError:
            result = {}
        return result
