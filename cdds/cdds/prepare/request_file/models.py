# (C) British Crown Copyright 2020-2022, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = no-member
import logging
import os

from cdds.common.io import read_json
from cdds.common.plugins.plugin_loader import load_plugin
from cdds.common.plugins.plugins import PluginStore
from cdds.common.plugins.grid import GridType
from cdds.prepare.request_file.constants import (BASE_DATE,
                                                 LICENSES,
                                                 ROSE_SUITE_FILENAME,
                                                 CONFIG_VERSION)

from hadsdk.arguments import Arguments
from hadsdk.common import check_svn_location, determine_rose_suite_url
from hadsdk.constants import NO_PARENT, STANDARD
from hadsdk.request import Request


class RoseSuiteRequest(Request):
    """
    Stores the request items of a rose suite and the unmodified rose suite info
    """

    def __init__(self, items={}, suite_info={}):
        super(RoseSuiteRequest, self).__init__(items, None)
        self._suite_info = suite_info

    @property
    def suite_info(self):
        return self._suite_info

    def read_from_json(self, json_file):
        """
        Read JSON in given file and convert them into request
        items. Afterwards, all items where validated.

        Parameters
        ----------
        json_file: :class:`string`
            Path to JSON file
        """
        self._items = read_json(json_file)
        self._add_attributes()
        self._validate_keys()

    def load(self, suite_info, suite_arguments):
        """
        Load the request by using the given rose suite info. The rose
        suite info values and rose suite arguments will be used to
        fulfill all necessary request properties.

        Parameters
        ----------
        suite_info: :dict
            rose suite dictionary that should be used to load
            the request properties

        suite_arguments: :class:`cdds.prepare.request_file.models.RoseSuiteArguments`
            arguments that is needed to load the rose suite info correctly
            into the request
        """
        self._items = {}

        self._suite_info = suite_info
        self._override_run_bounds(suite_arguments)
        self._load_required_items(suite_arguments)
        self._load_streams_items(suite_arguments.streams)
        self._load_parent_items()

    def _override_run_bounds(self, suite_arguments):
        """
        Handle the overriding of the start and end dates in the rose-suite.info
        in the run bounds.

        Parameters
        ----------
        suite_arguments: :class:`cdds.prepare.request_file.models.RoseSuiteArguments`
            arguments that is needed to load the rose suite info correctly
            into the request
        """
        logger = logging.getLogger(__name__)
        # default to rose-suite.info values
        self._run_bounds_start_date = self._suite_info['start-date']
        self._run_bounds_end_date = self._suite_info['end-date']
        if suite_arguments.start_date is not None:
            logger.info('Replacing start date "{}" with "{}"'.format(
                self._suite_info['start-date'],
                suite_arguments.start_date
            ))
            self._run_bounds_start_date = suite_arguments.start_date
        if suite_arguments.end_date is not None:
            logger.info('Replacing end date "{}" with "{}"'.format(
                self._suite_info['end-date'],
                suite_arguments.end_date
            ))
            self._run_bounds_end_date = suite_arguments.end_date

    @staticmethod
    def _load_institution_info_from_cv(cv_dir, mip_era, institution_id):
        cvv = read_json(os.path.join(cv_dir, '{}_CV.json'.format(mip_era)))
        institutions = cvv['CV']['institution_id']
        institution_info = institutions[institution_id]
        return institution_info.split(',')[0]

    def _load_license(self, mip_era, institution_info):
        if 'license' in self._suite_info.keys():
            return self._suite_info['license']
        else:
            return LICENSES[mip_era].format(institution_info)

    def _load_required_items(self, arguments):
        model_id = self._suite_info['model-id']
        mip_era = self._suite_info.get('mip-era', 'CMIP6')
        institution_info = self._load_institution_info_from_cv(
            arguments.cv_dir, mip_era, self._suite_info['institution'])
        license = self._load_license(mip_era, institution_info)

        plugin = self._get_plugin(mip_era, arguments)
        grid_info = plugin.grid_info(model_id, GridType.ATMOS)

        base_items = {
            'atmos_timestep': str(grid_info.atmos_timestep),
            'branch_method': self._get_branch_method(),
            'calendar': self._suite_info['calendar'],
            'child_base_date': BASE_DATE,
            'config_version': CONFIG_VERSION,
            'experiment_id': self._suite_info['experiment-id'],
            'institution_id': self._suite_info['institution'],
            'license': license,
            'mip': self._suite_info['MIP'],
            'mip_era': mip_era,
            'mip_table_dir': arguments.cv_dir,
            'model_id': self._suite_info['model-id'],
            'model_type': self._suite_info['source-type'].replace(',', ' '),
            'package': arguments.package,
            'request_id': '{model-id}_{experiment-id}_{variant-id}'.format(**self._suite_info),
            'run_bounds': '{}-00-00-00 {}-00-00-00'.format(self._run_bounds_start_date, self._run_bounds_end_date),
            'sub_experiment_id': self._suite_info['sub-experiment-id'],
            'suite_branch': arguments.branch,
            'suite_id': arguments.suite,
            'suite_revision': str(arguments.revision),
            'variant_label': self._suite_info['variant-id'],
            'mass_data_class': arguments.mass_data_class,
        }
        if arguments.mass_ensemble_member:
            base_items['mass_ensemble_member'] = arguments.mass_ensemble_member
        self._items.update(base_items)

    def _load_streams_items(self, streams):
        for stream in streams:
            key = 'run_bounds_for_stream_' + stream
            self._items[key] = '{}-00-00-00 {}-00-00-00'.format(self._run_bounds_start_date, self._run_bounds_end_date)

    def _load_parent_items(self):
        if self._has_parent():
            parent_items = {
                'branch_date_in_child': '{start-date}-00-00-00'.format(**self._suite_info),
                'branch_date_in_parent': '{branch-date}-00-00-00'.format(**self._suite_info),
                'parent_base_date': BASE_DATE,
                'parent_experiment_id': self._suite_info['parent-experiment-id'],
                'parent_mip': self._suite_info['parent-experiment-mip'],
                'parent_mip_era': 'CMIP6',
                'parent_model_id': self._suite_info['model-id'],
                'parent_time_units': 'days since 1850-01-01',
                'parent_variant_label': self._suite_info['parent-variant-id']
            }
            self._items.update(parent_items)

    @staticmethod
    def _get_plugin(mip_era, arguments):
        plugin_loaded = PluginStore.any_plugin_loaded()
        if not plugin_loaded:
            load_plugin(mip_era, arguments.external_plugin)
        return PluginStore.instance().get_plugin()

    def _get_branch_method(self):
        return STANDARD if self._has_parent() else NO_PARENT

    def _has_parent(self):
        key = 'parent-experiment-id'
        # Allowed values of parent-experiment-id other than valid experiment id's
        return key in self._suite_info and self._suite_info[key] not in [NO_PARENT, '', 'None', None]


class RoseSuiteArguments(Arguments):
    """
    Stores all arguments that are used to write a request from a rose suite

    branch - the branch that should be used, for example: cdds
    revision - revision of the rose suite that should be used
    suite - the suite ID
    package - the package of the experiment
    streams - the additional round bound streams that should be considered
    cv_dir - the directory of the controlled vocabularies
    request_file - the path to the output file of the request
    """

    SVN_URL_TEMPLATE = '{}/{}/{}@{}'

    def __init__(self, default_global_args={}, default_package_args={}, default_script_args={}):
        super(RoseSuiteArguments, self).__init__(default_global_args, default_package_args, default_script_args)

    def set_suite_arguments(self, suite_value, branch_value, revision_value, package_value, streams_value):
        self.__setattr__('suite', suite_value)
        self.__setattr__('branch', branch_value)
        self.__setattr__('revision', revision_value)
        self.__setattr__('package', package_value)
        self.__setattr__('streams', streams_value)

    @property
    def svn_location(self):
        """
        Uses the class variables to construct the valid Subversion
        location where the rose suite info is stored

        Returns
        -------
        :string
            URL of Subversion location
        """
        base_url = determine_rose_suite_url(self.suite)
        if not check_svn_location(base_url):
            base_url = determine_rose_suite_url(self.suite, False)
        return self.SVN_URL_TEMPLATE.format(base_url, self.branch, ROSE_SUITE_FILENAME, self.revision)

    @property
    def request_file(self):
        return os.path.join(self.output_dir, self.output_file_name)

    @property
    def cv_dir(self):
        return super(RoseSuiteArguments, self).mip_table_dir
