# (C) British Crown Copyright 2022-2025, Met Office.
# Please see LICENSE.md for license details.
from abc import ABCMeta, abstractmethod
import argparse
import logging

from cdds.tests.nightly_tests.app_config import AppConfig


class NightlyApp(object, metaclass=ABCMeta):
    """Defines the abstract class which all Nightly apps should inherited.
    Subclasses should define the application's command-line interface by over-
    riding the :attr:`cli_spec` property. The application's functionality should
    be specified by overriding the :meth:`run` method. The latter may of course
    call any number of private methods in order to implement that functionality.
    """

    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # Namespace object holding values parsed from any command-line options
        self.cli_args = argparse.Namespace()
        self.app_config = None

    @property
    @abstractmethod
    def cli_spec(self):
        """Defines the command-line interface specification for the application.
        This should be a list of dictionaries, each of which specifies a series
        of parameters.

        If no CLI arguments are required then an empty list should be returned.
        """
        raise NotImplementedError

    @abstractmethod
    def run(self):
        """Interface to run the application."""
        raise NotImplementedError

    def _parse_cli_args(self, app_name):
        """Parse command-line arguments according to the app's 'cli_spec'
        property. Parsed options and/or arguments can subsequently be accessed
        via the application object's 'cli_args' attribute.

        Attributes values should normally be accessed using standard dot notation,
        e.g, ``self.cli_args.config`` to obtain the value of a ``--config``
        command-line option, assuming that option is supported by the application.

        Parameters
        ----------
        app_name: str
            the name of the app to display in the usage text.
        """
        program_name = self.__class__.__name__
        parser = argparse.ArgumentParser(
            prog=program_name,
            description="{0}: App for nightly tests".format(app_name),
            conflict_handler='resolve')

        for cli_arg in self.cli_spec or []:
            try:
                tmp_dict = cli_arg.copy()
                names = tmp_dict.pop('names')
                parser.add_argument(*names, **tmp_dict)
            except Exception:
                self.logger.error("Error in CLI argument specification:\n{}", cli_arg)
                raise

        parser.parse_args(namespace=self.cli_args)

    def _parse_app_config(self, config_file=None):
        """Parse configuration options from a file in Rose's extended INI format
        and wrap it in an :class:`cdds.tests.nightly_tests.app_config` object.

        Parameters
        ----------
        config_file: str
            Path to the configuration file to parse. If not specified then the
            command-line argument list is checked for a --config-file option.
        """
        if not config_file:
            config_file = getattr(self.cli_args, 'config_file', None)

        if not config_file:
            raise AttributeError("No configuration file specified.")

        try:
            self.app_config = AppConfig.from_file(config_file)
        except Exception:
            self.logger.error("Error parsing configuration file %s", config_file)
            raise
