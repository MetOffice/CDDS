# (C) British Crown Copyright 2018-2025, Met Office.
# Please see LICENSE.md for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods

import pytest
import os
import pytest
import unittest

from mip_convert.configuration.python_config import ModelToMIPMappingConfig

import mip_convert
from mip_convert.plugins.plugin_loader import load_plugin
from mip_convert.plugins.plugins import MappginPluginStore
from mip_convert.process import REQUIRED_OPTIONS


CFG_SUFFIX = '_mappings.cfg'
PLUGIN_IDS = ['HadGEM3', 'UKESM1']  # TOCO: Kerstin add 'HadGEM2' after add plugin


def get_test_info():
    info = []
    unused_model_configuration = 'model'
    unused_mip_table_id = 'mip'
    for plugin_id in PLUGIN_IDS:
        mip_convert_dir = os.path.dirname(os.path.realpath(mip_convert.__file__))
        path_to_process = os.path.join(mip_convert_dir, 'plugins', plugin_id.lower(), 'data')
        cfg_files = sorted([filename for filename in os.listdir(path_to_process) if filename.endswith(CFG_SUFFIX)])
        for cfg_file in cfg_files:
            prefix = cfg_file[:-len(CFG_SUFFIX)] if cfg_file.endswith(CFG_SUFFIX) else cfg_file
            if prefix == 'common':
                model_configuration = unused_model_configuration
                mip_table_id = unused_mip_table_id
            elif len(prefix.split('_')) == 2:
                model_configuration, mip_table_id = prefix.split('_')
            elif prefix in PLUGIN_IDS:
                model_configuration = prefix
                mip_table_id = unused_mip_table_id
            else:
                model_configuration = unused_model_configuration
                mip_table_id = prefix
            cfg_file_path = os.path.join(path_to_process, cfg_file)
            info.append((plugin_id, cfg_file_path, model_configuration, mip_table_id))
    return info


#@pytest.mark.mappings
@pytest.mark.parametrize("plugin_id, cfg_file, model_id, mip_table_id", get_test_info())
def test_required_options_in_configuration_files(plugin_id, cfg_file, model_id, mip_table_id):
    sections_to_test = ModelToMIPMappingConfig(cfg_file, model_id).sections
    load_plugin(plugin_id)
    # It doesn't matter what is before the _. We choose MIPERA.
    plugin = MappginPluginStore.instance().get_plugin()
    model_to_mip_mappings = plugin.load_model_to_mip_mapping('MIPERA_{}'.format(mip_table_id))
    # TODO: Kerstin is option units/positive required?
    for section in sections_to_test:
        if section not in ['COMMON']:
            mappings = Mappings(section, mip_table_id, os.path.basename(cfg_file), model_to_mip_mappings)
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
