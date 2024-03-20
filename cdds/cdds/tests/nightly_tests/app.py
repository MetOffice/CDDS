# (C) British Crown Copyright 2022-2024, Met Office.
# Please see LICENSE.rst for license details.
from abc import ABCMeta, abstractmethod
import argparse
import logging
import os
import shutil

from cdds.tests.nightly_tests.app_config import AppConfig
from cdds.tests.nightly_tests.arguments import CmdArgs
from cdds.tests.nightly_tests.common import NameListFilter, makedirs


class NightlyApp(object, metaclass=ABCMeta):
    """
    Defines the abstract class which all Nightly apps should inherited.
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
        """
        Defines the command-line interface specification for the application.
        This should be a list of dictionaries, each of which specifies a series
        of parameters.

        If no CLI arguments are required then an empty list should be returned.
        """
        raise NotImplementedError

    @abstractmethod
    def run(self):
        """
        Interface to run the application.
        """
        raise NotImplementedError

    def _parse_cli_args(self, app_name):
        """
        Parse command-line arguments according to the app's 'cli_spec'
        property. Parsed options and/or arguments can subsequently be accessed
        via the application object's 'cli_args' attribute.

        Attributes values should normally be accessed using standard dot notation,
        e.g, ``self.cli_args.config`` to obtain the value of a ``--config``
        command-line option, assuming that option is supported by the application.

        Parameters
        ----------
        app_name: :str
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
        """
        Parse configuration options from a file in Rose's extended INI format
        and wrap it in an :class:`cdds.tests.nightly_tests.app_config` object.

        Parameters
        ----------
        config_file: :str
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


class CreateRequestApp(NightlyApp):
    """
    App used by nightly tests to create the request json for each suite defined
    in the rose-app.conf by calling the corresponding method in CDDS.
    """
    APP_ERROR = 'Failed to create request.cfg for suite {}. For more information check log file: {}'
    COUNT = 0

    def __init__(self, *args, **kwargs):
        super(CreateRequestApp, self).__init__(*args, **kwargs)
        app_name = self.__class__.__name__
        self._parse_cli_args(app_name)
        self._parse_app_config()

        self.task_package = getattr(self.cli_args, 'package', None)
        self.request_file = getattr(self.cli_args, 'output_file', None)
        self.request_file_name = os.path.basename(self.request_file)
        self.request_dir = os.path.dirname(self.request_file)
        self.log_file = os.path.join(self.request_dir, 'create_request_json.log')

    @property
    def cli_spec(self):
        """
        Defines the command-line parameters for the app:
            -c/--config-file: Path to the app configuration file
            -o/--output-file: Path to the request output JSON file
        """
        return [
            {"names": ["-c", "--config-file"], "help": "Pathname of app configuration file"},
            {"names": ["-o", "--output-file"], "help": "Path to the request output JSON file"},
            {"names": ["-p", "--package"], "help": "Name of the current cylc task package"}
        ]

    def run(self):
        """
        Run application: Create the request JSON file of the rose suite info specified
        by the values of the app configuration and command line parameters.
        """
        # makedirs(self.request_dir)
        suites = self.app_config.iterate_namelist('suites', NameListFilter.task_suite, self.task_package)
        for suite in suites:
            present_request = suite['use_present_request']
            if present_request:
                self.logger.info('Copy existing request.cfg from {} to {}'.format(present_request, self.request_file))
                shutil.copyfile(present_request, self.request_file)
            else:
                file_name = 'cdds_request_{}.cfg'.format(self.task_package)
                file_path = os.path.join(os.getenv('CYLC_WORKFLOW_RUN_DIR'), 'requests', file_name)
                self.logger.info("Generate new request cfg from source in {}".format(file_path))
                # shutil.copyfile(file_path, self.request_file)

    def build_write_request_json_args(self, suite):
        """
        Build the arguments that is needed to run the call the
        `main_write_rose_suite_request_json` method.

        Parameters
        ----------
        suite: :dict
            Row of a name list entry containing all information of a suite that
            is needed to find the corresponding rose suite info.

        Returns
        -------
        :list
            list of command line arguments and their options
        """
        args = (CmdArgs()
                .with_option('-o', self.request_dir)
                .with_option('-f', self.request_file_name)
                .with_option('-l', self.log_file))
        return args.get()


class AppError(Exception):
    """
    Exception raised if running the app failed.
    """

    def __init__(self, app_name, log_file_path):
        """
        Initialise the exception with an error message containing the name
        of the app and the path to the log file that contains more information
        why the app failed.

        Parameters
        ----------
        app_name: :str
            Name of the app that raise the error.

        log_file_path: :str
            Path to the log file that contains more information about the failure
        """
        super(AppError, self).__init__()
        self.msg = 'Failed to run App "{}". For more information check log file: "{}"'.format(app_name, log_file_path)

    def __str__(self):
        return repr(self.msg)
