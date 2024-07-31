# (C) British Crown Copyright 2020-2023, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = no-member
"""
The :mod:`configuration` module contains the configuration classes that
store the information read from the configuration files.
"""
import enum

from mip_convert.configuration.json_config import JSONConfig


class CVKey(object):

    ACTIVITY_ID = 'activity_id'
    EXPERIMENT_ID = 'experiment_id'
    EXPERIMENT = 'experiment'
    FREQUENCY = 'frequency'
    GRID_LABEL = 'grid_label'
    INSTITUTION_ID = 'institution_id'
    NOMINAL_RESOLUTION = 'nominal_resolution'
    REALM = 'realm'
    SOURCE = 'source'
    SOURCE_ID = 'source_id'
    SOURCE_TYPE = 'source_type'
    SUB_EXPERIMENT_ID = 'sub_experiment_id'
    TABLE_ID = 'table_id'
    PARENT_ACTIVITY_ID = 'parent_activity_id'
    REQUIRED_MODEL_COMPONENTS = 'required_model_components'
    ADDITIONAL_ALLOWED_MODEL_COMPONENTS = 'additional_allowed_model_components'
    PARENT_EXPERIMENT_ID = 'parent_experiment_id'
    REQUIRED_GLOBAL_ATTRIBUTES = 'required_global_attributes'
    TRACKING_ID = 'tracking_id'


class CVConfig(JSONConfig):
    """
    Store information read from the Controlled Vocabularies (CV) file.

    Methods are defined such that they return a value that is true for
    the entire instance.
    """

    _UNKNOWN = 'unknown'

    def __init__(self, read_path):
        self.config = None
        super(CVConfig, self).__init__(read_path)

    @property
    def version(self):
        """
        Return the version number of the CV file.
        """
        version_metadata = self.config['CV'].get('version_metadata', {})
        if version_metadata and 'CV_collection_version' in version_metadata:
            cv_version = version_metadata['CV_collection_version']
        elif version_metadata and 'latest_tag_point' in version_metadata:
            cv_version = version_metadata['latest_tag_point']
        else:
            cv_version = None
        return cv_version

    @property
    def activity_ids(self):
        """
        Return all the |MIPs| specified by the CV file.
        """
        return self._get_values_from_cv(CVKey.ACTIVITY_ID)

    def activity_id(self, experiment_id):
        """
        Return the allowed |MIPs| specified by the CV file.

        Parameters
        ----------
        experiment_id: str
            The |experiment identifier|.
        """
        value = []
        info = self._get_value_from_cv(CVKey.EXPERIMENT_ID, experiment_id)
        if CVKey.ACTIVITY_ID in info:
            value = info[CVKey.ACTIVITY_ID][0].split()
        return value

    def experiment_cv(self, experiment_id):
        """
        Return the a dictionary from the Controlled Vocabularies
        with all the information on a particular experiment

        Parameters
        ----------
        experiment_id: str
            The |experiment identifier|.
        """
        info = self._get_value_from_cv(CVKey.EXPERIMENT_ID, experiment_id)
        return info

    def experiment(self, experiment_id):
        """
        Return the long description of the |experiment| specified by
        the CV file.

        Parameters
        ----------
        experiment_id: str
            The |experiment identifier|.
        """
        value = self._UNKNOWN
        info = self._get_value_from_cv(CVKey.EXPERIMENT_ID, experiment_id)
        if info and CVKey.EXPERIMENT in info:
            value = info[CVKey.EXPERIMENT]
        return value

    def institution(self, institution_id):
        """
        Return the long description of the institution specified by the
        CV file.

        Parameters
        ----------
        institution_id: str
            The institution identifier.
        """
        return self._get_value_from_cv(CVKey.INSTITUTION_ID, institution_id)

    def parent_activity_id(self, experiment_id, parent_experiment_id, mip_era):
        """
        Return the parent |mip| specified by the CV file.

        Parameters
        ----------
        experiment_id: str
            The |experiment identifier|.
        parent_experiment_id: str
            The |experiment identifier| of the parent simulation.
        mip_era: str
            The |MIP era|. If ``CMIP6`` then allow for choices in
            parent experiment.
        """
        info = self._get_value_from_cv(CVKey.EXPERIMENT_ID, experiment_id)
        # If experiment_id is not found return unknown
        if info == self._UNKNOWN:
            return self._UNKNOWN
        # Otherwise attempt to get parent activity id from parentage
        # dictionary
        parentage_dict = self._get_parentage_dictionary(info)
        if parent_experiment_id not in parentage_dict:
            error_message = 'Parent experiment id "{}" not found in parentage dictionary: "{}"'
            raise RuntimeError(error_message.format(parent_experiment_id, parentage_dict))
        return parentage_dict[parent_experiment_id]

    def source(self, source_id):
        """
        Return the long description of the source (|model|) specified
        by the CV file.

        Parameters
        ----------
        source_id: str
            The |model identifier|.
        """
        value = self._UNKNOWN
        info = self._get_value_from_cv(CVKey.SOURCE_ID, source_id)
        if CVKey.SOURCE in info:
            value = info[CVKey.SOURCE]
        return value

    @property
    def source_types(self):
        """
        Return all the |model types| specified by the CV file.
        """
        return self._get_values_from_cv(CVKey.SOURCE_TYPE)

    def allowed_source_types(self, experiment_id):
        """
        Return the required |model types| and the additional allowed |model types|
        specified by the CV file.

        Parameters
        ----------
        experiment_id: str
            The |experiment identifier|.
        """
        return self.required_source_type(experiment_id) + self.additional_source_type(experiment_id)

    def required_source_type(self, experiment_id):
        """
        Return the required |model types| specified by the CV file.

        Parameters
        ----------
        experiment_id: str
            The |experiment identifier|.
        """
        value = []
        info = self._get_value_from_cv(CVKey.EXPERIMENT_ID, experiment_id)
        if CVKey.REQUIRED_MODEL_COMPONENTS in info:
            value = info[CVKey.REQUIRED_MODEL_COMPONENTS]
        return value

    def additional_source_type(self, experiment_id):
        """
        Return the additional allowed |model types| specified by the CV
        file.

        Parameters
        ----------
        experiment_id: str
            The |experiment identifier|.
        """
        value = []
        info = self._get_value_from_cv(CVKey.EXPERIMENT_ID, experiment_id)
        if CVKey.ADDITIONAL_ALLOWED_MODEL_COMPONENTS in info:
            value = info[CVKey.ADDITIONAL_ALLOWED_MODEL_COMPONENTS]
        return value

    def sub_experiment(self, sub_experiment_id):
        """
        Return the long description of the sub experiment specified by
        the CV file.

        Parameters
        ----------
        sub_experiment_id: str
            The sub-|experiment identifier|.
        """
        return self._get_value_from_cv(CVKey.SUB_EXPERIMENT_ID, sub_experiment_id)

    @property
    def tracking_prefix(self):
        """
        Return the tracking prefix specified by the CV file.
        """
        result = self._UNKNOWN
        if CVKey.TRACKING_ID in self.config['CV']:
            tracking_ids = self.config['CV'][CVKey.TRACKING_ID]
            result = tracking_ids[0].split('/')[0]
        return result

    @property
    def tracking_id(self):
        """
        Return the tracking prefix specified by the CV file.
        """
        result = self._UNKNOWN
        if CVKey.TRACKING_ID in self.config['CV']:
            result = self.config['CV'][CVKey.TRACKING_ID][0]
        return result

    @property
    def conventions(self):
        """
        Return the first element of the Conventions attribute
        """
        return self._get_values_from_cv("Conventions")[0].replace('\\', '')

    @property
    def required_global_attributes(self):
        """
        Return the required global attributes specified by the CV file.

        :return: the required global attributes specified by the CV
            file
        :rtype: list
        """
        written_by_cmor = [
            'Conventions', 'creation_date', 'data_specs_version', 'frequency',
            'mip_era', 'product', 'realm', 'table_id', 'tracking_id',
            'variable_id']
        required = []
        if CVKey.REQUIRED_GLOBAL_ATTRIBUTES in self.config['CV']:
            required = self.config['CV'][CVKey.REQUIRED_GLOBAL_ATTRIBUTES]
        return [attribute for attribute in required if attribute not in written_by_cmor]

    def validate_with_error(self, expected_value, attribute_key):
        """
        Ensure ``expected_value`` exists in the list of values returned
        when checking the attribute with key ``attribute_key``.

        Parameters
        ----------
        expected_value: str
            The expected value of the attribute to validate.
        attribute_key: str
            The name of the attribute that has the list of values to
            validate against.

        Raises
        ------
        RuntimeError: if the value of the attribute does not exist in
            the list of values to validate against.
        """
        actual_values = getattr(self, attribute_key)
        if expected_value not in actual_values:
            raise RuntimeError('"{}" does not exist in "{}"'.format(expected_value, attribute_key))

    def validate(self, attribute_name, attribute_value):
        """
        Ensure ``attribute_value`` exists in the list of values returned
        when calling the method ``method_name``.

        Parameters
        ----------
        attribute_value: str
            The value of the attribute to validate.
        attribute_name: str
            The name of the attribute that returns the list of values to
            validate against.

        Returns
        ------
        :bool :str
            True if validation passed else false and a logging message
        """
        collection = self._get_values_from_cv(attribute_name, [])
        if attribute_value in collection:
            return True, ''
        return False, '"{}" does not belong to CV collection "{}"'.format(attribute_value, attribute_name)

    def parent_experiment_id(self, experiment_id):
        info = self._get_value_from_cv(CVKey.EXPERIMENT_ID, experiment_id)
        if info == self._UNKNOWN:
            return self._UNKNOWN

        return info[CVKey.PARENT_EXPERIMENT_ID]

    def get_collection(self, attribute):
        return self._get_values_from_cv(attribute)

    def _get_values_from_cv(self, attribute, default_attributes=None):
        attributes = default_attributes
        if attribute in self.config['CV']:
            attributes = self.config['CV'][attribute]
        return attributes

    def _get_value_from_cv(self, attribute, key):
        value = 'unknown'
        attributes = self._get_values_from_cv(attribute)
        if attributes and key in attributes:
            value = attributes[key]
        return value

    @staticmethod
    def _get_single_value(key, value):
        if key in value:
            value = value[key]
            if len(value) != 1:
                raise RuntimeError('"{}" is not a single value'.format(key))
            value = value[0]
        return value

    @staticmethod
    def _get_parentage_dictionary(info):
        parent_experiment = info[CVKey.PARENT_EXPERIMENT_ID]
        parent_activity = info[CVKey.PARENT_ACTIVITY_ID]
        return {experiment: mip for experiment, mip in zip(parent_experiment, parent_activity)}
