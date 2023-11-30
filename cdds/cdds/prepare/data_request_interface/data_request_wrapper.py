# (C) British Crown Copyright 2018-2023, Met Office.
# Please see LICENSE.rst for license details.
"""
Tools to load the CMIP6 data request via dreqPy
"""
import logging
import os

from dreqPy import dreq as data_request_lib
from dreqPy.dreq import loadDreq
from typing import Dict, Any, List

from cdds.common.plugins.plugins import PluginStore

DATA_REQUEST_BASE_DIR = os.path.join(os.environ['CDDS_ETC'], 'data_requests/CMIP6')

# The following items were found by searching through the attributes of the
# dreq module and picking out strings that contain the current version number.
# This may break if dreqPy changes structure.
FIELDS_TO_ALTER_PRIOR_TO_LOAD = {
    'DOC_DIR': 'dreqPy/docs',
    'blockSchemaFile': 'dreqPy/docs/BlockSchema.csv',
    'defaultDreqPath': 'dreqPy/docs/dreq.xml',
    'defaultConfigPath': 'dreqPy/docs/dreq2Defn.xml',
    'defaultManifestPath': 'dreqPy/docs/dreqManifest.txt',
    'PACKAGE_DIR': 'dreqPy'}


class ExperimentNotFoundError(Exception):
    """
    Error raised when the Experiment identifier is not found in the Data
    request at the version specified.
    """
    pass


class DataRequestWrapper(object):
    """
    A class to provide a consolidated point of access to the CMIP6 data
    request.
    """

    def __init__(self) -> None:
        """
        Loads the data request and add top level properties. The data request is loaded
        from the mip table directory provided by the plugins
        """
        self.data_request_dir: str = PluginStore.instance().get_plugin().mip_table_dir()

        self.code_version: str = data_request_lib.version
        self._data_request: loadDreq = None
        self.files_loaded: Dict[str, str] = {}
        self._load_data_request_at_version()
        self.version = self._data_request.version

    def _load_data_request_at_version(self) -> None:
        """
        Load the data request object at the specified version or from
        the specified package directory.

        *Note:*
        This method alters a set of module level constants within the dreqPy.dreq module, loads the data request and
        then puts all the constants back to their original values. It is possible that when the version of the python
        library being used and the version being loaded are a long way apart that something will go wrong.

        The following attributes are set by this method;z
         * `files_loaded` : List of data request data files that were read.
         * `code_version` : Version of the data request python code used to load the data request.
         * `version` : Version of the data request that is being represented, i.e. the version listed
            in the data files that were read.

        The "raw" top level data request object is stored in the `_data_request` attribute.
        """
        logger = logging.getLogger(__name__)
        logger.debug('Loading data request files from "{}"'.format(self.data_request_dir))

        original_values = {}

        # Load the data request objects
        logger.info('Loading data request')
        self._data_request: loadDreq = data_request_lib.loadDreq()
        logger.info('Loaded data request version "{}"'
                    ''.format(self._data_request.version))

        # Record the files loaded
        self.files_loaded = {field: getattr(data_request_lib, field) for field in FIELDS_TO_ALTER_PRIOR_TO_LOAD}
        # Add new attribute to make it clear that the data request xml and code come from different versions
        self._data_request.code_version = self.code_version
        # Restore dreq module constants to their original values
        for item, value in original_values.items():
            setattr(data_request_lib, item, value)

    def get_experiment_uid(self, experiment_name: str) -> str:
        """
        Return the unique id corresponding to the experiment name supplied in the data request.

        :param experiment_name: |Experiment| name
        :type experiment_name: str
        :return: Unique ID
        :rtype: str
        """
        logger = logging.getLogger(__name__)

        # Check for upper and lower case versions of experiment name it it
        # cannot be found in the data request.
        name = None
        for current_name in [experiment_name, experiment_name.upper(), experiment_name.lower()]:
            if current_name in self._data_request.inx.experiment.label:
                name = current_name
                break

        # If experiment name is not found at all raise an error, otherwise log the experiment name found and proceed.
        if name is None:
            error_msg = 'Experiment name "{}" not found in this version of the data request'
            raise ExperimentNotFoundError(error_msg.format(experiment_name))
        elif name != experiment_name:
            log_msg = 'Experiment name "{}" not found in this version of the data request, but found "{}"'
            logger.info(log_msg.format(experiment_name, name))

        experiment_uids = self._data_request.inx.experiment.label[name]
        if len(experiment_uids) > 1:
            error_msg = 'Found multiple experiment uids for experiment name "{}": "{}"'
            raise RuntimeError(error_msg.format(experiment_name, '", "'.join(experiment_uids)))
        return experiment_uids[0]

    def get_object_dictionary(self, object_type: str) -> Dict[str, Any]:
        """
        Return a dictionary of uid to data request objects for the specified data request object_type.

        :param object_type: Data request object type, e.g. "CMORvar" or "requestItem".
        :type object_type: str
        :return: The data request objects, of the specified type, organised by data request unique id (uid).
        :rtype: Dict[str, Any]
        """
        return getattr(self._data_request.inx, object_type).uid

    def get_object_by_uid(self, uid: str) -> Any:
        """
        Return the data request object with the specified uid.
        :param uid: Unique id.
        :type uid: str
        :return: The corresponding data request object.
        :rtype: Any
        """
        return self._data_request.inx.uid[uid]

    def get_object_by_label(self, object_type: str, label: str) -> List[Any]:
        """
        Return data request objects of the specified type with the specified label (e.g. CMORvar with label `tas`).

        :param object_type: Data request object type, e.g. "CMORvar" or "requestItem".
        :type object_type: str
        :param label: Object label to filter on.
        :type label: str
        :return: The data request objects of specified type and label.
        :rtype: List[Any]
        """
        uids = getattr(self._data_request.inx, object_type).label[label]
        return [self.get_object_by_uid(uid) for uid in uids]
