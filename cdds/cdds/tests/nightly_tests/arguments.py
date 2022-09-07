# (C) British Crown Copyright 2021, Met Office.
# Please see LICENSE.rst for license details.


class CmdArgs:
    """
    Represents the command line arguments for a command.
    The class should help to build the command line arguments
    easier. It uses the builder pattern.
    """

    def __init__(self):
        self.args = []

    def with_arg(self, value):
        """
        Append a value without an option to the arguments

        Parameters
        ----------
        value: :str
            The argument value

        Returns
        -------
        :class:`cdds.tests.nightly_tests.app_config.CmdArgs`
            The updated class instance
        """
        self.args.append(value)
        return self

    def with_args(self, values, separator=','):
        """
        Append several values without an option to the arguments and
        they are separated by a specific separator.

        Parameters
        ----------
        values: :str
            The argument values separated by the given separator

        separator: :str (optional)
            The separator that separated the values. Default: ','

        Returns
        -------
        :class:`cdds.tests.nightly_tests.app_config.CmdArgs`
            The updated class instance
        """
        value_list = values.split(separator)
        for value in value_list:
            self.args.append(value)
        return self

    def with_option(self, option_name, value):
        """
        Append an argument with an option, e.g.:
        `-c foo.cfg` -> option_name is `-c` and value is `foo.cfg`.

        Parameters
        ----------
        option_name: :str
            The option name

        value: :str
            The argument value

        Returns
        -------
        :class:`cdds.tests.nightly_tests.app_config.CmdArgs`
            The updated class instance
        """
        self.args.append(option_name)
        self.args.append(value)
        return self

    def get(self):
        """
        Returns the current list of arguments.

        Returns
        -------
        :list
            The list of options and arguments sorted by the calling
            order of the with functions
        """
        return self.args
