# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
import configparser


class ConfigError(Exception):
    """ Exception raised in the event of configuration problems. """
    pass


class Config(object):

    """Wrap configuration files with a simple interface.

    Public methods:
    attr -- return a mandatory attribute from a configuration section
    optional_attr -- return an optional attribute from a configuration section
    section -- return a configuration section
    """

    def __init__(self, config_file):
        """Create a wrapper object around configuration files.

        Arguments:
        config_file -- (str or list of strs) Path(s) to config files

        If config_file is None then an empty Config object is returned.
        """
        self._config_file = config_file
        self._cp = configparser.ConfigParser(interpolation=None)
        self._cp.optionxform = str
        if config_file is not None:
            files_read = self._cp.read(config_file)
            if len(files_read) < 1:
                raise ConfigError(
                    "Error reading config from \"{}\"" .format(config_file))

    def section(self, section_name):
        """Return a configuration section as a dict. Raise a ConfigError if
        the specified section does not exist.

        Arguments:
        section_name -- (str) name of the section to return
        """
        self._check_section(section_name)
        return dict(self._cp.items(section_name))

    def attr(self, section_name, name):
        """Return the value of the configuration section and attribute. Raise
        a ConfigError if either the section or attribute aren't defined in
        the configuration file(s).

        Arguments:
        section_name -- (str) name of section containing attribute
        name -- (str) name of the attribute to return
        """
        self._check_section(section_name)
        if not self._cp.has_option(section_name, name):
            raise ConfigError(
                "missing attribute %s from section %s, file %s" % (
                    name, section_name, self._config_file))
        return self._cp.get(section_name, name)

    def optional_attr(self, section_name, name):
        """Return the value of the configuration section and attribute, or
        None if the attribute isn't defined.

        Arguments:
        section_name -- (str) name of section containing attribute
        name -- (str) name of the attribute to return
        """
        attr = None
        if self._cp.has_section(section_name):
            try:
                attr = self._cp.get(section_name, name)
            except configparser.NoOptionError:
                pass
        return attr

    def _check_section(self, section_name):
        if not self._cp.has_section(section_name):
            raise ConfigError(
                "missing section %s from config file %s" % (
                    section_name, self._config_file))
