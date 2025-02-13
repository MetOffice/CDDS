# (C) British Crown Copyright 2018-2021, Met Office.
# Please see LICENSE.md for license details.
"""
Tools to load the CMIP6 data request via dreqPy
"""
import logging
import os

from dreqPy import dreq as data_request_lib

DATA_REQUEST_BASE_DIR = os.path.join(os.environ['CDDS_ETC'], 'data_requests', 'CMIP6')

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

    def __init__(self, required_version, basedir=None):
        """
        Load the data request and add top level properties.

        Parameters
        ----------
        required_version : str
            String describing the version of the data request.
        basedir : str, optional
            Location of the tags directory where data request files for
            various versions are checked out.
        """
        self.required_version = required_version
        if basedir is None:
            self.basedir = DATA_REQUEST_BASE_DIR
        else:
            self.basedir = basedir

        self.code_version = data_request_lib.version
        self._data_request = None
        self.files_loaded = {}
        self._load_data_request_at_version()
        self.version = self._data_request.version

    def _load_data_request_at_version(self):
        """
        Load the data request object at the specified version or from
        the specified package directory.

        Notes
        -----
        This method alters a set of module level constants within the
        dreqPy.dreq module, loads the data request and then puts all
        the constants back to their original values. It is possible that
        when the version of the python library being used and the version
        being loaded are a long way apart that something will go wrong.
        Note that the required version of the data request must have been
        checked out to a similar location to the code version.

        The following attributes are set by this method;
         * `files_loaded` : List of data request data files that were
           read.
         * `code_version` : Version of the data request python code used
           to load the data request.
         * `version` : Version of the data request that is being
           represented, i.e. the version listed in the data files that
           were read.

        The "raw" top level data request object is stored in the
        `_data_request` attribute.
        """
        logger = logging.getLogger(__name__)
        logger.info('Data request version "{}" requested'
                    ''.format(self.required_version))
        logger.info(
            'Using data request code version "{}"'.format(self.code_version))
        logger.debug('Loading data request files from "{}"'
                     ''.format(self.basedir))

        original_values = {}
        # Overwrite the properties of the data request module that need
        # changing to effect a change of version when loading. Hold on to the
        # original values in a dictionary so that they can be reset later.
        if self.code_version != self.required_version:
            for item, suffix in FIELDS_TO_ALTER_PRIOR_TO_LOAD.items():
                value = getattr(data_request_lib, item)
                original_values[item] = value
                new_value = os.path.join(
                    self.basedir, self.required_version, suffix)
                if not os.path.exists(new_value):
                    raise IOError('File or directory does not exist: "{}"'
                                  ''.format(new_value))
                setattr(data_request_lib, item, new_value)

        # Load the data request objects
        logger.info('Loading data request')
        self._data_request = data_request_lib.loadDreq()
        logger.info('Loaded data request version "{}"'
                    ''.format(self._data_request.version))
        if self._data_request.version != self.required_version:
            if self._data_request.version.startswith(self.required_version):
                logger.warning(
                    'Data request version has suffix: required version = "{}",'
                    ' loaded version = "{}"'
                    ''.format(self.required_version,
                              self._data_request.version))
            else:
                raise RuntimeError(
                    'Data request version mismatch: "{}" != "{}"'
                    ''.format(self._data_request.version,
                              self.required_version))
        # Record the files loaded
        self.files_loaded = {field: getattr(data_request_lib, field)
                             for field in FIELDS_TO_ALTER_PRIOR_TO_LOAD}
        # Add new attribute to make it clear that the data request xml and
        # code come from different versions
        self._data_request.code_version = self.code_version
        # Restore dreq module constants to their original values
        for item, value in original_values.items():
            setattr(data_request_lib, item, value)

    def get_experiment_uid(self, experiment_name):
        """
        Return the unique id corresponding to the experiment_name
        supplied in the data request.

        Parameters
        ----------
        experiment_name : str
            |Experiment| name.

        Returns
        -------
        : str
            unique id.

        Raises
        ------
        RuntimeError
            If experiment_name cannot be found in the data request
            (upper and lower case versions checked for) or there are
            multiple unique id's found.
        """
        logger = logging.getLogger(__name__)

        # Check for upper and lower case versions of experiment name it it
        # cannot be found in the data request.
        name = None
        for i in [experiment_name, experiment_name.upper(),
                  experiment_name.lower()]:
            if i in self._data_request.inx.experiment.label:
                name = i
                break

        # If experiment name is not found at all raise an error, otherwise
        # log the experiment name found and proceed.
        if name is None:
            raise ExperimentNotFoundError(
                'Experiment name "{}" not found in this version of the data '
                'request ("{}")'.format(experiment_name, self.version))
        elif name != experiment_name:
            logger.info('Experiment name "{}" not found in this version of '
                        'the data request ("{}"), but found "{}"'
                        ''.format(experiment_name, self.version, name))

        experiment_uids = self._data_request.inx.experiment.label[name]
        if len(experiment_uids) > 1:
            raise RuntimeError(
                'Found multiple experiment uids for experiment name "{}": "{}"'
                ''.format(experiment_name, '", "'.join(experiment_uids)))
        return experiment_uids[0]

    def get_object_dictionary(self, object_type):
        """
        Return a dictionary of uid to data request objects for the
        specified data request object_type.

        Parameters
        ----------
        object_type : str
            Data request object type, e.g. "CMORvar" or "requestItem".

        Returns
        -------
        : dict
            The data request objects, of the specified type, organised
            by data request unique id (uid).
        """
        return getattr(self._data_request.inx, object_type).uid

    def get_object_by_uid(self, uid):
        """
        Return the data request object with the specified uid.

        Parameters
        ----------
        uid : str
            Unique id.

        Returns
        -------
        : object
            The corresponding data request object.
        """
        return self._data_request.inx.uid[uid]

    def get_object_by_label(self, object_type, label):
        """
        Return data request objects of the specified type with the
        specified label (e.g. CMORvar with label `tas`).

        Parameters
        ----------
        object_type : str
            Data request object type, e.g. "CMORvar" or "requestItem".
        label : str
            Object label to filter on.

        Returns
        -------
        : list
            The data request objects of specified type and label.
        """
        uids = getattr(self._data_request.inx, object_type).label[label]
        return [self.get_object_by_uid(uid) for uid in uids]
