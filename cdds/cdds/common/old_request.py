# (C) British Crown Copyright 2018-2022, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = no-member
"""
The :mod:`request` module contains the code required to handle the
information about the request.
"""
from copy import deepcopy
import logging

from cdds.common.constants import REQUIRED_KEYS_FOR_GENERAL_CONFIG_ACCESS
from cdds.common.plugins.plugin_loader import load_plugin
from cdds.common.io import read_json, write_json


def read_request(request_path, required_keys=None, default_items=None):
    """
    Return the information from the request.

    If an option in ``default_items`` already exists in the request,
    the value of the option in the request will be used.

    Parameters
    ----------
    request_path: str
        The full path to the JSON file containing the information from
        the request.
    required_keys: list
        The keys that must exist in the JSON file containing the
        information from the request.
    default_items: dict
        The default items to be added to the request.

    Returns
    -------
    : :class:`cdds.common.old_request.Request`
        The information from the request.
    """
    # Retrieve the logger.
    logger = logging.getLogger(__name__)

    # Read the information from the request.
    logger.debug('Reading request information from "{}"'.format(request_path))
    items = read_json(request_path)

    request = construct_request(items, required_keys, default_items)
    load_cdds_plugins(request)
    return request


def load_cdds_plugins(request):
    """
    Loads all internal CDDS plugins and external CDDS plugins specified in
    the request object.

    :param request: The information from the request json file.
    :type request: `cdds.common.old_request.Request`
    """
    external_plugin = None
    if request.external_plugin:
        external_plugin = request.external_plugin
    load_plugin(request.mip_era, external_plugin, request.external_plugin_location)


def construct_request(items, required_keys=None, default_items=None):
    """
    Return the information from the request.

    Parameters
    ----------
    items : dict
        The information from the request.
    required_keys: list
        The keys that must exist in ``items``.
    default_items: dict
        The default items to be added to the request.

    Returns
    -------
    : :class:`cdds.common.old_request.Request`
        The information from the request.
    """
    # Add the default items only if they don't already exist in the
    # request.
    if default_items is not None:
        for option, value in list(default_items.items()):
            if option not in items:
                items[option] = value

    # Always include the keys required to access the general
    # configuration file. Remove this once Arguments class has been
    # utilised across CDDS.
    if required_keys is None:
        required_keys = []
    required_keys.extend(REQUIRED_KEYS_FOR_GENERAL_CONFIG_ACCESS)

    # Validate the information from the request.
    request = Request(items, list(set(required_keys)))

    return request


class Request(object):
    """
    Store the information about the request. The request object
    contains the following attributes:

    * ``ancil_files``: See the `request section`_ in the
      `MIP Convert User Guide`_.
    * ``atmos_timestep``: See the `request section`_ in the
      `MIP Convert User Guide`_.
    * ``branch_date_in_child``: See the `cmor_dataset section`_ in the
      `MIP Convert User Guide`_.
    * ``branch_date_in_parent``: See the `cmor_dataset section`_ in the
      `MIP Convert User Guide`_.
    * ``branch_method``: See the `CMIP6 Global Attributes document`_.
    * ``calendar``: See the `cmor_dataset section`_ in the
      `MIP Convert User Guide`_.
    * ``child_base_date``: See the `cmor_dataset section`_ in the
      `MIP Convert User Guide`_.
    * ``create_subdirectories``: See the documentation for
      `cmor_setup`_.
    * ``cmor_log_file``: See ``logfile`` in the documentation for
      `cmor_setup`_.
    * ``config_version``: The version number of the CDDS configuration
      files.
    * ``deflate_level``: See the `request section`_ in the
      `MIP Convert User Guide`_.
    * ``experiment_id``: The |experiment identifier|.
    * ``hybrid_heights_files``: See the `request section`_ in the
      `MIP Convert User Guide`_.
    * ``institution_id``: See the `CMIP6 Global Attributes document`_.
    * ``license``: See the `CMIP6 Global Attributes document`_.
    * ``mip_table_dir``: See ``inpath`` in the documentation for
      `cmor_setup`_.
    * ``model_id``: The |model identifier|.
    * ``model_output_dir``: The directory containing the
      |model output files|.
    * ``model_type``: The |model type|.
    * ``mip``: The name of the |MIP|.
    * ``mip_era``: The |MIP era|.
    * ``netcdf_file_action``: See the documentation for `cmor_setup`_.
    * ``output_dir``: The directory containing the
      |output netCDF files|.
    * ``package``: The name of the |package|.
    * ``parent_base_date``: See the `cmor_dataset section`_ in the
      `MIP Convert User Guide`_.
    * ``parent_experiment_id``: See the
      `CMIP6 Global Attributes document`_.
    * ``parent_mip``: See ``parent_activity_id`` in the
      `CMIP6 Global Attributes document`_.
    * ``parent_mip_era``: See the `CMIP6 Global Attributes document`_.
    * ``parent_model_id``: See ``parent_source_id`` in the
      `CMIP6 Global Attributes document`_.
    * ``parent_time_units``: See the
      `CMIP6 Global Attributes document`_.
    * ``parent_variant_label``: See the
      `CMIP6 Global Attributes document`_.
    * ``replacement_coordinates_file``: See the `request section`_ in
      the `MIP Convert User Guide`_.
    * ``request_id``: The |request identifier|.
    * ``run_bounds``: See the `request section`_ in the
      `MIP Convert User Guide`_.
    * ``run_bounds_for_stream_<stream_id>``: The run bounds for a
      particular |stream identifier|.
    * ``shuffle``: See the `request section`_ in the
      `MIP Convert User Guide`_.
    * ``sites_file``: See the `request section`_ in the
      `MIP Convert User Guide`_.
    * ``sub_experiment_id``: See the
      `CMIP6 Global Attributes document`_.
    * ``suite_id``: The |suite identifier|.
    * ``variant_label``: See the `CMIP6 Global Attributes document`_.

    If an attribute has no value, a value of ``None`` is returned.
    """
    ALLOWED_ATTRIBUTES = [
        'ancil_files', 'atmos_timestep', 'branch_date_in_child', 'branch_date_in_parent', 'branch_method', 'calendar',
        'child_base_date', 'create_subdirectories', 'cmor_log_file', 'config_version', 'deflate_level',
        'external_plugin', 'external_plugin_location', 'experiment_id', 'global_attributes', 'hybrid_heights_files',
        'input_dir', 'institution_id', 'license', 'mass_ensemble_member', 'mip_table_dir', 'model_id',
        'model_output_dir', 'model_type', 'mip', 'mip_era', 'netcdf_file_action', 'output_dir', 'package',
        'parent_base_date', 'parent_experiment_id', 'parent_mip', 'parent_mip_era', 'parent_model_id',
        'parent_time_units', 'parent_variant_label', 'replacement_coordinates_file', 'mass_data_class', 'run_bounds',
        'shuffle', 'sites_file', 'sub_experiment_id', 'suite_branch', 'suite_id', 'suite_revision', 'variant_label'
    ]

    def __init__(self, items, required_keys=None):
        """
        Parameters
        ----------
        items: dict
            The information about the request.
        required_keys: list
            The keys that must exist in ``items``.
        """
        # Retrieve the logger.
        self.logger = logging.getLogger(__name__)
        self._items = items
        self._required_keys = required_keys
        self._add_attributes()
        self._validate_keys()

    def _add_attributes(self):
        for attribute in Request.ALLOWED_ATTRIBUTES:
            value = None
            if attribute in self._items:
                value = self._items[attribute]
            setattr(self, attribute, value)
        for attribute in self._items:
            if attribute.startswith('run_bounds_for_stream_'):
                value = self._items[attribute]
                setattr(self, attribute, value)

    def _validate_keys(self):
        if self._required_keys is not None:
            for key in self._required_keys:
                self._validate(key)

    def _validate(self, attribute):
        if getattr(self, attribute) is None:
            if attribute != 'config_version':  # while replacing config
                msg = 'Request requires a value for "{}"'.format(attribute)
                raise AttributeError(msg)

    def validate(self, attributes):
        """
        Ensure the object has the attributes provided by ``attributes``.
        """
        for attribute in attributes:
            self._validate(attribute)

    @property
    def request_id(self):
        """
        str: The |request identifier|.
        """
        _request_id = None
        if self.model_id is not None and self.experiment_id is not None and (
                self.variant_label is not None):
            _request_id = '{}_{}_{}'.format(self.model_id, self.experiment_id,
                                            self.variant_label)
        return _request_id

    @property
    def items(self):
        """
        dict: The information about the request.
        """
        items = deepcopy(self._items)
        if self.request_id is not None:
            items['request_id'] = self.request_id
        if not self.external_plugin:
            items['external_plugin'] = ''
        if not self.external_plugin_location:
            items['external_plugin_location'] = ''
        if not self.global_attributes:
            items['global_attributes'] = {}
        return items

    @property
    def flattened_items(self):
        """
        Returns all items in a flatted dictionary structure
        :return: The information about the request in a flattened version
        :rtype: dict
        """
        stack = [self.items]
        flat_dict = {}
        while stack:
            current_dict = stack.pop()
            for key, value in current_dict.items():
                if isinstance(value, dict):
                    stack.append(value)
                else:
                    flat_dict[key] = value
        return flat_dict

    @property
    def items_global_attributes(self):
        """
        Returns all items of the global attributes section as a dictionary

        :return: Global attributes items
        :rtype: dict
        """
        items = getattr(self, 'global_attributes')
        return items if items else {}

    @property
    def items_for_facet_string(self):
        """
        dict: The items for the facet string.
        """
        facet_string_to_attribute_mapping = {
            'experiment': 'experiment_id', 'project': 'mip',
            'programme': 'mip_era', 'model': 'model_id',
            'realisation': 'variant_label', 'request': 'request_id'}
        return self._get_items(facet_string_to_attribute_mapping)

    @property
    def items_for_cmor(self):
        """
        dict: The items for |CMOR|.
        """
        cmor_to_attribute_mapping = {
            'activity_id': 'mip', 'source_id': 'model_id',
            'source_type': 'model_type'}
        return self._get_items(cmor_to_attribute_mapping)

    def _get_items(self, name_to_attribute_mapping):
        items = self.items
        for name, attribute in list(name_to_attribute_mapping.items()):
            if attribute in items:
                del items[attribute]
                items[name] = getattr(self, attribute)
        return items

    @property
    def streaminfo(self):
        """
        dict: Stream information.
        """
        req_vars_streams = [
            (k1, v1) for k1, v1 in list(self.items.items())
        ]
        streams_dict = {}
        for stream_bounds_var, stream_bounds_data in req_vars_streams:
            if stream_bounds_var.startswith('run_bounds_for_stream'):
                stream_name = stream_bounds_var.split('_')[-1]
                streams_dict[stream_name] = {
                    'var': stream_bounds_var,
                    'start_date': stream_bounds_data.split(' ')[0],
                    'end_date': stream_bounds_data.split(' ')[1],
                    'type': 'pp' if stream_name.startswith(
                        'ap') else 'nc'
                }
        return streams_dict

    def write(self, jsonfile):
        """
        Write the request information to a JSON file with the name
        ``jsonfile``.

        Parameters
        ----------
        jsonfile: str
            The name of file to write to.
        """
        write_json(jsonfile, self.items)
