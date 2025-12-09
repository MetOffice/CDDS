# (C) British Crown Copyright 2021-2025, Met Office.
# Please see LICENSE.md for license details.
import re
from functools import cmp_to_key

from cdds.common import rose_config
from cdds.common.rose_config import ConfigNode


class AppConfig(ConfigNode):
    """Read Rose configuration files. This extends ``rose_config.ConfigNode`` to
    provide additional functionality.
    """

    def __init__(self, value=None, state=ConfigNode.STATE_NORMAL, comments=None):
        """Initialise the app config class

        Parameters
        ----------
        value: :dict or :str
            The value of the AppConfig object, typically a dict or str.

        state: :str
            The ignore state of the object. Either '', '!' or '!!'.

        comments: :str
            Any comments about the object.
        """
        allowed_states = [ConfigNode.STATE_NORMAL, ConfigNode.STATE_USER_IGNORED, ConfigNode.STATE_SYST_IGNORED]
        if state not in allowed_states:
            msg = 'State "{}" is not an allowed value.'.format(state)
            raise ValueError(msg)
        ConfigNode.__init__(self, value, state, comments)

    @staticmethod
    def from_file(filename):
        """Create an instance from a Rose configuration file.

        Parameters
        ----------
        filename: str
            The path to the Rose configuration file to load.

        Returns
        -------
        :class:`cdds.tests.nightly_tests.app_config.AppConfig`
            AppConfig objet containing the loaded Rose configuration
        """
        rose_cfg = rose_config.load(filename)
        return AppConfig(rose_cfg.value, rose_cfg.state, rose_cfg.comments)

    def get_property(self, section, property_name, default=None):
        """Get a string from the specified ``section`` and ``prop_name`` of the
        loaded Rose configuration.

        Parameters
        ----------
        section: str
            The name of the section.

        property_name: str
            Name of the property

        default: str (optional)
            Default value if the property is not set. Default: None

        Returns
        -------
        str
            The string property value
        """
        return self.get_value([section, property_name], default)

    def iterate_namelist(self, namelist, callback=None, callback_args=None):
        """A iterator function (lazy loading of the namelist) to iterate
        through the items in the specified namelist. A item is represent
        by a dictionaries containing its data.

        The index of each item is included in the returned dictionary with the
        key '_index'.

        Parameters
        ----------
        namelist: str
            The name of the namelist.

        callback: :function (optional)
            A function to filter the returned items. It should accept a dictionary
            containing the properties of a namelist item and return a boolean indicating
            if this namelist item should be output.

        callback_args: str (optional)
            Argument of the callback function.

        Returns
        -------
        dict
            Dictionary containing the data of the next namelist item.
        """
        section_keys = list(self.value.keys())
        sorter = rose_config.sort_settings
        section_keys.sort(key=cmp_to_key(sorter))
        section_name = r'namelist:{}\((.+)\)'.format(namelist)

        for section_key in section_keys:
            node = self.get([section_key])
            if node.is_ignored():
                continue
            index_match = re.findall(section_name, section_key)
            if isinstance(node.value, dict) and index_match:
                sub_keys = list(node.value.keys())
                index_str = index_match[0]
                output = {'_index': index_str}
                for key in sub_keys:
                    output[key] = node.get_value([key])
                if callback and callback_args:
                    if callback(output, callback_args):
                        yield output
                elif callback and not callback_args:
                    if callback(output):
                        yield output
                else:
                    yield output

    def section_to_dict(self, section):
        """Convert a top-level configuration section to a plain dict object.

        Parameters
        ----------
        section: str
            The name of the section to convert to a dictionary.

        Returns
        -------
        dict
            Dictionary containing the key-value pairs of the properties
            defined in the requested section.
        """
        if section not in self.get_value().keys():
            raise ValueError('Section "{}" does not occur in AppConfig object.'.format(section))

        section_dict = {}
        section_node = self.get([section])

        for keys, node in section_node.walk():
            if node.is_ignored():
                section_dict[keys[-1]] = None
            else:
                section_dict[keys[-1]] = node.get_value()

        return section_dict
