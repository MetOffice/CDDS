# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
from mip_convert.save.cmor.cmor_outputter import MoNameSpace
from mip_convert.load.model_output_config import AbstractDataSourceUser


class CmorSetupConf(object):
    """
    Instances of this class read the cmor.setup arguments from the
    cmor_project file.

    The arguments are options in the [general] section of the
    cmor_project file.
    """
    SECTION = 'general'

    def __init__(self, config_parser):
        """
        :param config_parser: a ConfigParser opened on cmor_project
                              and already read.
        """
        self.config_parser = config_parser

    def __getattr__(self, attname):
        msg_fmt = "type object '%s' has no attribute '%s'"
        if not self._has(attname):
            raise AttributeError(msg_fmt % (self.__class__.__name__, attname))
        return self._get(attname)

    def _get(self, option):
        """
        return the string value of the option
        """
        return self.config_parser.get(self.SECTION, option)

    def _has(self, option):
        """
        returns True if have the option
        """
        return self.config_parser.has_option(self.SECTION, option)


class CmorDatasetConf(AbstractDataSourceUser):
    """
    Instances of this class read the cmor.dataset arguments from the
    cmor_project file.

    The arguments are options in the [data_source] section of the
    cmor_project file.
    """

    RUNID_GLOBAL = MoNameSpace.RUNID

    def __init__(self, project_config, application_history, date_generator, outpath):
        """
        :param project_config: the opened ConfigParser to get configuration
                               info from.
        :param application_history: the relevant application_history to be put
                                    into the CMOR global history attribute.
        :param date_generator: (no longer used - needs refactoring to remove)
        :param outpath: the path for any NetCDF files written as part of this data set.
        """
        self._project_config = project_config
        self._date_generator = date_generator
        self.history = application_history
        self.outpath = outpath
        self._globals = _CmorConfigGlobalSection(project_config)

    def __getattr__(self, attname):
        msg_fmt = "type object '%s' has no attribute '%s'"
        if not self._has(attname):
            raise AttributeError(msg_fmt % (self.__class__.__name__, attname))
        return self._get(attname)

    def _get(self, option):
        """
        return the string value of the option
        """
        return self._project_config.get(self.SECTION, option)

    def _has(self, option):
        return self._project_config.has_option(self.SECTION, option)

    def _standard_globals(self):
        glob_atts = dict()
        glob_atts[self.RUNID_GLOBAL] = ' '.join(self.runnames)
        return glob_atts

    def global_attributes(self):
        """
        Return iterator of global attributes and their values.

        The runids will always be a global attribute in the iterator.
        Other global attributes are read from the [global_attributes]
        section of the cmor_project file.
        """
        glob_atts = self._standard_globals()
        glob_atts.update(self._globals.read())
        return iter(list(glob_atts.items()))


class _CmorConfigGlobalSection(object):
    """
    Instances of this class can be used to interpret the
    [global_attributes] section in the cmor_project file.

    Each option in the [global_attributes] section is used as the
    name of a global attribute.  The value of the option becomes
    the value of the corresponding global attribute.

    As ConfigParser converts all option names to lower case the
    preserve_case option of the [globa_attributes] section supports
    the keeping of case into the NetCDF global attribute.
    """
    _SECTION = 'global_attributes'
    _PRESERVE = 'preserve_case'

    def __init__(self, project_config):
        """
        :param project_config: the ConfigParser opened on cmor_project
        """
        self._project_config = project_config

    def read(self):
        """
        Interpret the options of the [global_attributes] section
        and return a dictionary of attribute names and  values.
        """
        glob_atts = dict()
        if self._exists():
            for option in self._attribute_options():
                glob_atts[self._as_netcdf_attr(option)] = self._get(option)
        return glob_atts

    def _preserved_case(self):
        result = []
        if self._has_preserved():
            result = self._get(self._PRESERVE).split()
        return result

    def _as_netcdf_attr(self, option):
        attr = option
        for preserved in self._preserved_case():
            if option == preserved.lower():
                attr = preserved
        return attr

    def _exists(self):
        return self._project_config.has_section(self._SECTION)

    def _attribute_options(self):
        options = self._project_config.options(self._SECTION)
        self._remove_specials(options)
        return options

    def _get(self, option):
        return self._project_config.get(self._SECTION, option)

    def _has_preserved(self):
        return self._project_config.has_option(self._SECTION, self._PRESERVE)

    def _remove_specials(self, options):
        for special in self._special_options():
            if special in options:
                options.remove(special)

    def _special_options(self):
        return [self._PRESERVE] + list(self._project_config.defaults().keys())
