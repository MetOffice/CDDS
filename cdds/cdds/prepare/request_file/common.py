# (C) British Crown Copyright 2020-2022, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = no-member
import os
import tempfile

from cdds.common import rose_config
from cdds.common import run_command
from mip_convert.configuration.cv_config import CVConfig


def load_controlled_vocabulary(experiment_id, cv_path):
    """
    Load controlled vocabulary from internet using curl command
    of given revision and return only the given section of the
    controlled vocabulary

    Parameters
    ----------
    experiment_id: :class:`string`
        the ID of the experiment that controlled vocabulary is
        needed

    cv_path: :class:`string`
        full path to the controlled vocabulary file

    Returns
    -------
    : :class:`dict`
        the controlled vocabulary for the given experiment as dict
    """
    controlled_vocabularies = CVConfig(cv_path)
    return controlled_vocabularies.experiment_cv(experiment_id)


def load_rose_suite_info(svn_url):
    """
    Load rose suite info by given Subversion URL and convert it
    into a dictionary containing the key and the actual value

    Parameters
    ----------
    svn_url: :class:`string`
        The Subversion URL where the rose suite info is found

    Returns
    -------
    :dict
        the rose suite info as a dictionary of key :string and
        value :string
    """
    command = ['svn', 'cat', svn_url]
    data = run_command(command)

    temp_file = _write_into_temp_file(data)
    suite_info = load_suite_info_from_file(temp_file)

    _delete_file(temp_file)
    return suite_info


def load_suite_info_from_file(file_path):
    """
    Loads the rose suite info from a file

    :param file_path: Path to the rose suite info file
    :type file_path: str
    :return: The rose suite info as a dictionary of key :string and value :string
    :rtype: dict
    """
    full_suite = rose_config.load(file_path)
    suite_info = {k: v.value for k, v in full_suite.value.items() if v.state == ''}
    return suite_info


def _delete_file(temp_file):
    if os.path.exists(temp_file):
        os.remove(temp_file)


def _write_into_temp_file(data):
    id, path = tempfile.mkstemp()

    try:
        with open(path, 'w') as temp_file:
            temp_file.write(str(data))
    except IOError:
        raise IOError('Could not write into temp file: {}'.format(path))

    return path
