# (C) British Crown Copyright 2020-2021, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = no-member
"""
The :mod:`configuration` module contains the configuration classes that
store the information read from the configuration files.
"""
from collections import OrderedDict

import configparser

from hadsdk.common import remove_newlines
from hadsdk.configuration.common import AbstractConfig, ValidateConfigError
from hadsdk.constants import COMMENT_FORMAT, DATE_TIME_FORMAT
from hadsdk.configuration.user_config import cmor_setup_config, cmor_dataset_config, request_config


class PythonConfig(AbstractConfig):
    """
    Read Python configuration files.
    """

    def __init__(self, read_path):
        self.config = self._config()
        super(PythonConfig, self).__init__(read_path)

    @staticmethod
    def _config():
        interpolation = configparser.ExtendedInterpolation()
        config = configparser.ConfigParser(interpolation=interpolation, inline_comment_prefixes=('#',))
        config.optionxform = str  # Preserve case.
        return config

    def read(self, read_path):
        """
        Read the configuration file; see
        `configparser.ConfigParser.read_file`_.

        The ``config`` attribute is set equal to an instance of
        `backports.configparser.ConfigParser`_.
        `configparser.ExtendedInterpolation`_ is used, which enables
        the use of values from other sections using the syntax
        ``${section:option}``.

        :raises backports.configparser.DuplicateSectionError: if more
            than one section with the same name exists in the
            configuration file
        :raises backports.configparser.DuplicateOptionError: if more
            than one option with the same name exists in a single
            section in the configuration file
        """
        config_to_read = self._config()
        if isinstance(read_path, dict):
            config_to_read.read_dict(read_path)
        else:
            config_to_read.read_file(open(read_path), read_path)
        # Each section must be read as follows before updating
        # self.config to ensure options defined in the default section
        # are correctly included.
        for section in config_to_read.sections():
            items = OrderedDict(sorted(config_to_read[section].items()))
            if section not in self.config.sections():
                self.config[section] = items
            else:
                self.config[section].update(items)

    def write(self, filename, header=None):
        self.logger.debug('Writing "{}"'.format(filename))
        with open(filename, 'w') as file_handle:
            if header:
                file_handle.write(COMMENT_FORMAT.format(header))
            self.config.write(file_handle)

    @property
    def sections(self):
        """
        Return a list of sections available in the configuration file;
        see `configparser.ConfigParser.sections`_.

        :return: the sections in the configuration file
        :rtype: list of strings
        """
        # 'configparser' returns the section with a type 'unicode' by
        # default.
        return [str(section) for section in self.config.sections()]

    def items(self, section, msg=None):
        """
        Return the items (i.e., options and values) within a section in
        the configuration file; see `configparser.ConfigParser.items`_.

        :param section: the name of the section in the configuration
                        file
        :type section: string
        :return: the items within a section in the form
                 ``{option: value}``
        :rtype: dictionary
        """
        # 'configparser' returns the option and value with a type
        # 'unicode' by default.
        try:
            all_items = dict(
                [(str(option), str(remove_newlines(value))) for (option, value) in self.config.items(section)]
            )
        except configparser.Error as err:
            if msg is not None:
                err = '{err} {msg}'.format(err=err, msg=msg)
            raise configparser.Error(err)
        return all_items

    def options(self, section):
        """
        Return a list of options available within a section in the
        configuration file; see `configparser.ConfigParser.options`_.

        :param section: the name of the section in the configuration
                        file
        :type section: string
        :return: the options within a section in the configuration file
        :rtype: list of strings
        """
        # 'configparser' returns the option with a type 'unicode' by
        # default.
        options = None
        if self.config.has_section(section):
            options = [str(option) for option in self.config.options(section)]
        return options

    def value(self, section, option, ptype):
        """
        Return the single value from an option within a section in the
        configuration file; see `configparser.ConfigParser.get`_.

        :param section: the name of the section in the configuration
                        file
        :type section: string
        :param option: the name of the option within the section
        :type option: string
        :param ptype: the Python type of the value
        :type ptype: Python built-in function e.g., str, int
        :return: the single value of the option
        :rtype: defined by the ``ptype`` parameter
        """
        # 'configparser' returns the value with a type 'unicode' by
        # default.
        return ptype(remove_newlines(self.config.get(section, option)).strip())

    def _multiple_values(self, section, option, ptype):
        """
        Return the multiple values from an option within a section in
        the configuration file.

        :param section: the name of the section in the configuration
                        file
        :type section: string
        :param option: the name of the option within the section
        :type option: string
        :param ptype: the Python type of the values in the list
        :type ptype: Python built-in function e.g., str, int
        :return: the multiple values of the option
        :rtype: list of values with a type defined by the ``ptype``
                parameter
        """
        return [ptype(remove_newlines(value)) for value in self.config.get(section, option).split()]

    def _add_attributes(self, options):
        """
        Add the options from the configuration file as attributes to
        the object.

        The options provided to the ``options`` parameter must be a
        dictionary in the form ``{option: dictionary}``, where
        ``option`` is a string specifying the name of the option to be
        added as an attribute and ``dictionary`` is a dictionary that
        must contain at least ``{'section': section,
        'python_type': ptype, 'value_type': vtype, 'name': name,
        'check_function': function}``, where ``section`` is a string
        specifying the name of the section in the configuration file
        containing the ``option``, ``ptype`` is the Python type of the
        value of the ``option``, ``vtype`` is a string specifying
        whether the option has a single value or multiple values,
        respectively (choices are ``single`` or ``multiple``; multiple
        values are stored in a list), ``name`` is a string specifying
        the attribute name and ``function`` is a function that
        can be used to perform any checks or validation before the
        attribute is added. If the ``function`` returns a value, this
        value will be used as the value of the attribute.

        :param options: the options to be added as attributes
        :type options: dictionary

        :raises ValueError: if the ``value_type`` is not 'single' or
            'multiple'
        """
        msg = 'Adding attribute "{name}" to "{instance}" with value "{value}"'
        for option, option_info in options.items():
            section = option_info['section']
            ptype = option_info['python_type']
            vtype = option_info['value_type']
            default_value = option_info['default_value']
            name = option_info['name']
            check_function = option_info['check_function']
            if self.config.has_option(section, option):
                value = None
                if check_function is not None:
                    # Get the 'raw' value (i.e., as a string) from the
                    # configuration file.
                    raw_value = str(self.config.get(section, option).strip())
                    print(
                        'Checking "{raw_value}" (specified by "{option}")'.format(raw_value=raw_value, option=option)
                    )
                    return_value = check_function(raw_value)
                    self.logger.info('Validated "{raw_value}"'.format(raw_value=raw_value))
                    if return_value is not None:
                        value = return_value
                if value is None:
                    if vtype == 'multiple':
                        value = self._multiple_values(section, option, ptype)
                    elif vtype == 'single':
                        if ptype == bool:
                            value = self.config.getboolean(section, option)
                        else:
                            value = self.value(section, option, ptype)
                    else:
                        raise ValueError('Unsupported value type "{vtype}"'.format(vtype=vtype))
                self.logger.debug(msg.format(name=name, instance=self, value=value))
                setattr(self, name, value)
            # If the option doesn't exist in the section, check whether
            # the default value of None should be returned.
            elif default_value:
                value = None
                self.logger.debug(msg.format(name=name, instance=self, value=value))
                setattr(self, name, value)

    def _validate_required_options(self, section, options):
        """
        Ensure that the section provided to the ``section`` parameter
        in the configuration file contains the required options
        provided to the ``options`` parameter.

        :param section: the name of the section in the configuration
                        file
        :type section: string
        :param option: the names of the required options
        :type option: list of strings
        :raises ValidateConfigError: if the section does not exist in
                                     the configuration file
        :raises ValidateConfigError: if the section is missing a
                                     required option
        """
        if not self.config.has_section(section):
            raise ValidateConfigError(
                'Section "{section}" does not exist in configuration file '
                '"{read_path}"'.format(section=section, read_path=self.read_path))
        for required_option in options:
            if not self.config.has_option(section, required_option):
                raise ValidateConfigError(
                    'Section "{section}" in configuration file "{read_path}" does not contain "{required_option}"'
                    ''.format(section=section, read_path=self.read_path, required_option=required_option))
            self.logger.debug(
                'Required option "{required_option}" exists in section "{section}"'
                ''.format(required_option=required_option, section=section))


class UserConfig(PythonConfig):
    """
    Store information read from the |user configuration file|.

    The :class:`configuration.UserConfig` object has attributes with
    names equal to each option in the |user configuration file|.
    """

    _configs = [cmor_setup_config(), cmor_dataset_config(), request_config()]

    def __init__(self, read_path, history):
        super(UserConfig, self).__init__(read_path)
        self._all_options = {}
        self._required_options = {}
        self._global_attributes = {}
        self.streams_to_process = {}

        # Validate the sections.
        self._validate_sections()
        # Validate the options and populate self._all_options.
        self._validate_options()
        self.logger.debug('Options to be added as attributes: {attributes}'.format(
            attributes=list(self._all_options.keys())))
        self._add_attributes(self._all_options)
        self._add_streams()
        # The 'history' option from the 'user configuration file' is
        # never used; define a value for it here.
        self.history = history
        # Add the date time format.
        self.TIMEFMT = DATE_TIME_FORMAT

    @property
    def global_attributes(self):
        """
        Return the items (i.e., options and values) within the
        ``global_attributes`` section in the |user configuration file|.

        Anything in the ``global_attributes`` section in the
        |user configuration file| will be written to the header of the
        |output netCDF file|.

        :return: the items within the ``global_attributes`` section in
                 the form ``{option: value}``
        :rtype: dictionary
        """
        section = 'global_attributes'
        if self.config.has_section(section):
            self._global_attributes = self.items(section)
        return self._global_attributes

    @property
    def cmor_dataset(self):
        """
        Return the items (i.e. options and values) from the
        ``cmor_dataset`` section in the |user configuration file|,
        where the options are the names used in CMOR.
        """
        values = {config['name']: getattr(self, config['name'])
                  for config in list(cmor_dataset_config().values())
                  if hasattr(self, config['name'])}
        # Set 'activity_id' and 'source_type' to strings.
        for attribute in ['activity_id', 'source_type']:
            if attribute in values:
                values[attribute] = ' '.join(values[attribute])
        return values

    def _validate_sections(self):
        for section in ['cmor_setup', 'cmor_dataset', 'request']:
            if section not in self.sections:
                message = 'User configuration file does not contain the required section "{}"'
                raise ValidateConfigError(message.format(section))

    def _validate_options(self):
        for config in self._configs:
            self._all_options.update(config)
            for option, option_info in config.items():
                section = option_info['section']
                required = (option_info['required_by_cmor'] or option_info['required_by_mip_convert'])
                if required:
                    if section not in self._required_options:
                        self._required_options[section] = []
                    self._required_options[section].append(option)
        self.logger.debug('Required options: {}'.format(self._required_options))
        for section, options in self._required_options.items():
            self._validate_required_options(section, options)

    def _add_streams(self):
        """
        Add the |stream identifiers| from the configuration file as
        entries in the ``streams_to_process`` dictionary. This
        dictionary is keyed by the tuple (|stream identifier|,
        |MIP table| name) and has the corresponding list of
        |MIP requested variable names| as values.

        :raises ValidateConfigError: if there are duplicate
            |MIP requested variable names| specified for a given
            |MIP table| in the ``stream_<stream_id>`` sections in the
            |user configuration file|
        """
        # Add all items in any stream sections.
        for section in self.sections:
            if section.startswith('stream'):
                # Assuming the stream section names in the user configuration
                # file of form stream_stream_id_substream
                # e.g. stream_onm_grid-T
                section_elements = section.split('_')
                if len(section_elements) == 2:
                    (_, stream_id) = section_elements
                    substream = None
                elif len(section_elements) == 3:
                    (_, stream_id, substream) = section_elements
                else:
                    raise ValidateConfigError('The "stream" section in the user configuration file is invalid')

                for mip_table_name in self.options(section):
                    values = self._multiple_values(section, mip_table_name,
                                                   str)
                    if len(set(values)) != len(values):
                        raise ValidateConfigError(
                            'There are duplicate variable names specified for the "{mip_table_name}" option in the '
                            '"{stream_id}" section in the user configuration file'.format(
                                mip_table_name=mip_table_name, stream_id=stream_id)
                        )
                    self.logger.debug(
                        'Adding values ["{values}"] to streams_to_process dictionary under key ("{stream_id}", '
                        '"{mip_table_name}")'.format(
                            stream_id=stream_id,
                            mip_table_name=mip_table_name,
                            values='", "'.join(values)))
                    self.streams_to_process[(stream_id, substream, mip_table_name)] = values


class RequestConfig(PythonConfig):
    """
    Store information read from the request configuration files.

    There may be many instances of this class, one for each
    request configuration file. Methods are defined such that they
    return a value that is true for the entire instance.
    """

    def __init__(self, read_path, stream_id):
        """
        :param stream_id: the |stream identifier|
        :type stream_id: string
        """
        super(RequestConfig, self).__init__(read_path)
        self.stream_id = stream_id
        required_by_mip_convert = ['miptable']
        for section in self.sections:
            self._validate_required_options(section, required_by_mip_convert)

    @property
    def variable_names(self):
        """
        Return the |MIP requested variable names| from the
        request configuration file.

        :return: the |MIP requested variable names| from the
                 request configuration file
        :rtype: list of strings
        """
        return self.sections


class ModelToMIPMappingConfig(PythonConfig):
    """
    Store information read from the |model to MIP mapping|
    configuration files.
    """

    def __init__(self, read_path, model_id):
        super(ModelToMIPMappingConfig, self).__init__(read_path)
        self.model_id = model_id

    def select_mapping(self, variable_name, mip_table_id):
        """
        Return the |model to MIP mapping| for a specific
        |MIP requested variable|.

        :param variable_name: the |MIP requested variable name|
        :type variable_name: string
        :param mip_table_id: the |MIP table identifier|
        :type mip_table_id: string
        :return: the |model to MIP mapping| for a specific
            |MIP requested variable| in the form ``{option: value}``
        :rtype: dictionary
        :raises RuntimeError: if there is no |model to MIP mapping| for
            the specified |MIP table identifier|
        """
        msg = 'in model to MIP mapping configuration file'
        items = self.items(variable_name, msg)
        if 'mip_table_id' in items:
            if mip_table_id not in items['mip_table_id'].split():
                msg = 'No model to MIP mapping available for "{}" for "{}"'
                raise RuntimeError(msg.format(variable_name, mip_table_id))
        return items
