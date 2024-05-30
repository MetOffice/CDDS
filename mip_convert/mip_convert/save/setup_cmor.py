# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
import logging
import os

from mip_convert.configuration.cv_config import CVConfig
from mip_convert.save.cmor import cmor_lite
from mip_convert.save.cmor.cmor_dataset import Dataset


def setup_cmor(user_config, relaxed_cmor=False):
    """
    Setup |CMOR| in preparation for writing the |output netCDF files|.

    :param user_config: the |user configuration file|
    :type user_config: :class:`configuration.UserConfig` object
    :param relaxed_cmor: If true then CMOR will not perform CMIP6 validation
    :type relaxed_cmor: bool
    """
    logger = logging.getLogger(__name__)
    logger.debug('Setup CMOR:')
    logger.debug('*' * 20)
    cmor_lite.setup(user_config)
    cmor_lite.dataset(get_cmor_dataset(user_config, relaxed_cmor))
    logger.debug('*' * 20)


def get_cmor_dataset(user_config, relaxed_cmor=False):
    """
    Return the items required for ``cmor_dataset_json``.

    :param user_config: the |user configuration file|
    :type user_config: :class:`configuration.UserConfig` object
    :param relaxed_cmor: If true no cmip6 validation will be run
    :type relaxed_cmor: bool
    :return: the items required for ``cmor_dataset_json``
    :rtype: :class:`save.cmor.cmor_dataset.Dataset` object
    """
    # Read and validate the associated Controlled Vocabularies (CV) file, if defined.
    cv_config = get_cv_config(user_config)
    cmor_dataset = Dataset(user_config, cv_config, relaxed_cmor)
    # Ensure the required global attributes exist, then ensure the values conform to the CVs for those attributes
    # that are not currently checked by CMOR.
    cmor_dataset.validate_required_global_attributes()
    return cmor_dataset


def get_cv_config(user_config):
    """
    Return the Controlled Vocabularies (CV).

    :param user_config: the |user configuration file|
    :type user_config: :class:`configuration.UserConfig` object
    :return: the Controlled Vocabularies (CV)
    :rtype: :class:`configuration.CVConfig` object
    """
    logger = logging.getLogger(__name__)
    cv_file_name = '{}_CV.json'.format(user_config.mip_era)
    cv_path = os.path.join(user_config.inpath, cv_file_name)
    cv_config = CVConfig(cv_path)
    logger.debug('CV file "{}" exists'.format(cv_path))
    return cv_config
