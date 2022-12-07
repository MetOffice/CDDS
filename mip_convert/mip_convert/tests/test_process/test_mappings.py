# (C) British Crown Copyright 2018-2021, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods

import pytest
import os
import pytest
import unittest

from mip_convert.configuration.python_config import ModelToMIPMappingConfig

import mip_convert
from mip_convert.process import REQUIRED_OPTIONS
from mip_convert.request import get_model_to_mip_mappings


PATH_TO_PROCESS = os.path.join(os.path.dirname(os.path.realpath(mip_convert.__file__)), 'process')
CFG_SUFFIX = '_mappings.cfg'
CFG_FILES = sorted([filename for filename in os.listdir(PATH_TO_PROCESS) if filename.endswith(CFG_SUFFIX)])
MODELS_IN_CFG_FILES = ['HadGEM2', 'HadGEM3', 'UKESM']


def get_test_info():
    info = []
    unused_model_configuration = 'model'
    unused_mip_table_id = 'mip'
    for cfg_file in CFG_FILES:
        prefix = cfg_file[:-len(CFG_SUFFIX)] if cfg_file.endswith(CFG_SUFFIX) else cfg_file
        if prefix == 'common':
            model_configuration = unused_model_configuration
            mip_table_id = unused_mip_table_id
        elif len(prefix.split('_')) == 2:
            model_configuration, mip_table_id = prefix.split('_')
        elif prefix in MODELS_IN_CFG_FILES:
            model_configuration = prefix
            mip_table_id = unused_mip_table_id
        else:
            model_configuration = unused_model_configuration
            mip_table_id = prefix
        info.append((cfg_file, model_configuration, mip_table_id))
    return info


@pytest.mark.mappings
@pytest.mark.parametrize("cfg_file, model_id, mip_table_id", get_test_info())
def test_required_options_in_configuration_files(cfg_file, model_id, mip_table_id):
    cfg_path = os.path.join(PATH_TO_PROCESS, cfg_file)
    sections_to_test = ModelToMIPMappingConfig(cfg_path, model_id).sections
    # It doesn't matter what is before the _. We choose MIPERA.
    model_to_mip_mappings = get_model_to_mip_mappings(model_id, 'MIPERA_{}'.format(mip_table_id))
    for section in sections_to_test:
        if section not in ['COMMON']:
            mappings = Mappings(section, mip_table_id, cfg_file, model_to_mip_mappings)
            check_model_to_mip_mappings(mappings)


def check_model_to_mip_mappings(mappings):
    for required_option in REQUIRED_OPTIONS:
        if mappings.mip_table_id.startswith('Prim'):
            if required_option in ['dimension', 'status']:
                continue
        msg = '"{}" does not exist for "{}" in "{}"'.format(
            required_option, mappings.section, mappings.cfg_file)
        assert required_option in mappings.items, msg


class Mappings(object):
    def __init__(self, section, mip_table_id, cfg_file, model_to_mip_mappings):
        self.section = section
        self.mip_table_id = mip_table_id
        self.cfg_file = cfg_file
        self.model_to_mip_mappings = model_to_mip_mappings

    def __repr__(self):
        """
        Return a string that will be used as the name of the test.
        """
        return "'{}', '{}'".format(self.section, self.cfg_file)

    @property
    def items(self):
        try:
            _items = self.model_to_mip_mappings.items(self.section)
        except Exception:
            # nose doesn't like using configparser.NoSectionError.
            _items = {}
        return _items


if __name__ == '__main__':
    unittest.main()
