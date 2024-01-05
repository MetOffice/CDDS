# (C) British Crown Copyright 2017-2023, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`cmor_dataset` module contains the code required to assemble
the information required for the call to ``cmor_dataset_json``.
"""
import atexit
import json
import logging
import os
import regex as re
from tempfile import mkstemp

from cdds.common import VARIANT_LABEL_FORMAT

from mip_convert import model_date

FILES_TO_REMOVE = []
_ATTR = {
    # <required by CMOR>: [<provided by 'user configuration file'>].
    'branch_time_in_parent': ['branch_date_in_parent', 'parent_base_date'],
    'branch_time_in_child': ['branch_date_in_child', 'base_date']}


class Dataset(object):
    """
    Store information required for the call to ``cmor_dataset_json``.
    """

    def __init__(self, user_config, cv_config, relaxed_cmor=False):
        """
        Parameters
        ----------
        user_config: :class:`configuration.UserConfig` object
            The |user configuration file|.
        cv_config: :class:`mip_convert.configuration.cv_config.CVConfig` object
            The Controlled Vocabularies (CV).
        relaxed_cmor: bool
            If true then CMIP6 validation will not be run.
        """
        self.logger = logging.getLogger(__name__)
        self._user_config = user_config
        self._cv_config = cv_config
        self._items = {}
        self._relaxed_cmor = relaxed_cmor

    def validate_required_global_attributes(self):
        """
        Ensure the global attributes required by CMOR are available.
        """
        msg = 'Required global attribute "{}" {}'
        for attribute in self._cv_config.required_global_attributes:
            if attribute not in self.items:
                raise RuntimeError(msg.format(attribute, 'missing'))
            self.logger.debug(msg.format(attribute, 'exists'))
        if not self._relaxed_cmor:
            self.validate_activity_id_values()
            self.validate_source_type_values()

    def validate_activity_id_values(self):
        """
        Ensure the |MIPs| provided by the |user configuration file|
        conform to the CVs.

        Note the current version of CMOR (3.4.0) doesn't perform this
        check.

        Raises
        ------
        RuntimeError: if any |MIP| does not exist in the list of valid
            |MIPs| from the CVs.
        RuntimeError: if any |MIP| is inconsistent with the values
            specified for the |experiment| from the CVs.
        """
        logger = logging.getLogger(__name__)
        for activity_id in self._user_config.activity_id:
            # First ensure the value of 'activity_id' provided by the 'user configuration file' is a valid value.
            self._cv_config.validate_with_error(activity_id, 'activity_ids')

            # Then ensure the value is consistent with the value for the experiment from the CVs.
            if 'experiment_id' in self._cv_config._get_values_from_cv('required_global_attributes'):
                experiment_id = self._user_config.experiment_id
                cv_activity_id = self._cv_config.activity_id(experiment_id)
                if activity_id not in cv_activity_id:
                    message = ('"{}" is inconsistent with the values specified for the '
                               'experiment "{}" from the CVs ("{}")')
                    raise RuntimeError(message.format(activity_id, experiment_id, ' '.join(cv_activity_id)))
            else:
                logger.debug('Could not validate activity id (mip), for experiment as experiment_id is not '
                             'a required global attribute')

    def validate_source_type_values(self):
        """
        Ensure the 'source_type' provided by the
        |user configuration file| conforms to the CVs.

        Note the current version of CMOR (3.4.0) doesn't perform this
        check.

        Raises
        ------
        RuntimeError: if any |model type| does not exist in the list of
            valid |model types| from the CVs.
        RuntimeError: if the required |model types| specified for the
            |experiment| from the CVs are not present in the
            |user configuration file|.
        RuntimeError: if any additional |model types| specified in the
            |user configuration file| are inconsistent with the values
            specified for the |experiment| from the CVs.
        """
        logger = logging.getLogger(__name__)
        user_source_types = self._user_config.source_type
        for source_type in user_source_types:
            # First ensure the value of 'source_type' provided by the 'user configuration file' is a valid value.
            self._cv_config.validate_with_error(source_type, 'source_types')

        if 'experiment_id' in self._cv_config._get_values_from_cv('required_global_attributes'):
            experiment_id = self._user_config.experiment_id
            # Then ensure the required values for the experiment from the CVs are provided by the
            # 'user configuration file'.
            required_source_types = self._cv_config.required_source_type(experiment_id)
            for required_source_type in required_source_types:
                if required_source_type not in self._user_config.source_type:
                    message = 'Required model type "{}" for experiment "{}" not present'
                    raise RuntimeError(message.format(required_source_type, experiment_id))

            # Finally ensure any additional values for the experiment from the CVs are consistent with the values
            # provided by the 'user configuration file'.
            additional_source_types = self._cv_config.additional_source_type(experiment_id)
            invalid = set(user_source_types).difference(
                set(required_source_types)).difference(set(additional_source_types))

            if invalid:
                raise RuntimeError(
                    '"{}" is inconsistent with the additional values specified for the experiment "{}" '
                    'from the CVs ("{}")'.format(' '.join(sorted(invalid)), experiment_id,
                                                 ' '.join(additional_source_types))
                )
        else:
            logger.debug('Could not validate source type for experiment as experiment_id is not '
                         'a required global attribute')

    @property
    def items(self):
        """
        Return all items required for the call to
        ``cmor_dataset_json``.
        """
        # Add the items provided via the 'user configuration file'.
        self._items.update(self._user_config.cmor_dataset)
        # Add the history.
        self._items.update({'history': self._user_config.history})
        # Add whether CMIP6 validation should be performed.
        if not self._relaxed_cmor:
            self._items.update({'_cmip6_option': 'CMIP6'})
        # Add the items that can be determined from the 'variant_label'.
        self._items.update(self._items_from_variant_label)
        # Add the items that can be determined from the CV file.
        self._items.update(self._items_from_CV)
        # Add the CMOR filenames.
        self._items.update(self._CMOR_filenames)
        # Add global attributes
        self._items.update(self.global_attributes)

        # Add the items that are calculated using information provided by the 'user configuration file'.
        for branch_time_name, (
                branch_date_name, base_date_name) in list(_ATTR.items()):
            branch_time = self._branch_time(branch_time_name, branch_date_name, base_date_name)
            self._items.update(branch_time)

            # Remove options provided by the 'user configuration file'
            # not required for the call to ``cmor_dataset_json``.
            for option in (branch_date_name, base_date_name):
                if option in self._items:
                    del self._items[option]
        return self._items

    def write_json(self):
        """
        Write the items required for the call to ``cmor_dataset_json``
        to a JSON file.

        Returns
        -------
        : string
            The name of the JSON file.
        """
        os_handle, filename = mkstemp()
        with os.fdopen(os_handle, 'w') as file_handle:
            file_handle.write(json.dumps(self.items))
            file_handle.write('\n')
        FILES_TO_REMOVE.append(filename)
        # log CMOR JSON file content
        logger = logging.getLogger(__name__)
        logger.debug('CMOR json file content: {}'.format(json.dumps(self.items)))
        return filename

    @property
    def global_attributes(self):
        """
        Return the global attributes.
        """
        attributes = {}
        attributes.update(self._user_config.global_attributes)
        # Add the 'run identifier' to the global attributes so that it
        # gets written to the 'output netCDF files'.
        attributes['mo_runid'] = self._user_config.suite_id
        return attributes

    @property
    def _items_from_variant_label(self):
        logger = logging.getLogger(__name__)
        pattern = re.compile(VARIANT_LABEL_FORMAT)
        if 'variant_label' in self._cv_config._get_values_from_cv('required_global_attributes'):
            match = pattern.match(self._user_config.variant_label)
            items_from_variant_label = {
                'realization_index': match.group(1),
                'initialization_index': match.group(2),
                'physics_index': match.group(3),
                'forcing_index': match.group(4)
            }
        else:
            logger.debug('Could not populate CMIP6 style indices as variant_label not present')
            items_from_variant_label = {}

        return items_from_variant_label

    @property
    def _items_from_CV(self):
        logger = logging.getLogger(__name__)
        items_from_CV = {
            'cv_version': self._cv_config.version,
            'tracking_prefix': self._cv_config.tracking_prefix
        }
        required_global_attributes = self._cv_config._get_values_from_cv('required_global_attributes')
        # Could break this out as a constant, but these have to correspond to
        # implemented methods on the CVConfig class.
        items_from_CV_mapping = {
            'experiment': 'experiment_id',
            'institution': 'institution_id',
            'source': 'source_id',
            'sub_experiment': 'sub_experiment_id',
        }
        for val, val_id in items_from_CV_mapping.items():
            if hasattr(self._user_config, val_id):
                items_from_CV[val] = getattr(self._cv_config, val)(getattr(self._user_config, val_id))
            else:
                logger.debug('Field "{}" not added as "{}" not found in required '
                             'global attributes'.format(val, val_id))
        # can only check parent activity id where it is relevant.
        # Assume that if branch_method is defined, as in CMIP6, then parent_activity_id should be obtained in the
        # CMIP6 fashion
        if hasattr(self._user_config, 'branch_method') and self._user_config.branch_method != 'no parent':
            parent_activity_id = self._cv_config.parent_activity_id(self._user_config.experiment_id,
                                                                    self._user_config.parent_experiment_id,
                                                                    self._user_config.mip_era)
            items_from_CV['parent_activity_id'] = parent_activity_id
        else:
            logger.debug('Parent information not included as "branch_method" not included in '
                         'user config')
        return items_from_CV

    @property
    def _CMOR_filenames(self):
        mip_era = self._user_config.mip_era
        project_id = self.global_attributes.get('project_id', None)
        tables_directory = self._user_config.inpath
        CMOR_filenames = {
            '_controlled_vocabulary_file': '{}_CV.json',
            '_AXIS_ENTRY_FILE': '{}_coordinate.json',
            '_FORMULA_VAR_FILE': '{}_formula_terms.json'
        }
        for k, v in CMOR_filenames.items():
            file_found = False
            for file_prefix in [mip_era, project_id]:
                mip_era_path = os.path.join(tables_directory, v.format(file_prefix))
                if os.path.exists(mip_era_path):
                    CMOR_filenames[k] = v.format(file_prefix)
                    file_found = True
                    continue

            if not file_found:
                CMOR_filenames[k] = v.format('MIP')

        return CMOR_filenames

    def _branch_time(self, branch_time_name, branch_date_name, base_date_name):
        branch_time = {}
        if branch_date_name in self._user_config.cmor_dataset:
            if self._user_config.cmor_dataset[branch_date_name] == 'N/A':
                value = 0.
            else:
                value = (self._time_from_option(branch_date_name) - self._time_from_option(base_date_name))
            branch_time[branch_time_name] = value
        return branch_time

    def _time_from_option(self, option):
        value = getattr(self._user_config, option)
        return model_date.strptime(value, self._user_config.TIMEFMT, self._user_config.calendar)


@atexit.register
def _clean():
    if FILES_TO_REMOVE:
        for file_to_remove in FILES_TO_REMOVE:
            if os.path.isfile(file_to_remove):
                os.remove(file_to_remove)
