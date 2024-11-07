# (C) British Crown Copyright 2024, Met Office.
# Please see LICENSE.rst for license details.
import os
import logging

from metomi.isodatetime.parsers import TimePointParser

from cdds import _DEV, _NUMERICAL_VERSION
from cdds.common.cdds_files.cdds_directories import component_directory, input_data_directory, output_data_directory
from cdds.convert.constants import NTHREADS_CONCATENATE, PARALLEL_TASKS
from cdds.convert.process.workflow_interface import update_suite_conf_file


class ConfigureTemplateVariables:
    def __init__(self, arguments, request, stream_config, config_file, section="template variables"):
        self._arguments = arguments
        self._request = request
        self.stream_config = stream_config
        self.config_file = config_file
        self.section = section

        self.logger = logging.getLogger()

    @property
    def template_variables(self) -> dict:
        """Combine the separate groupings of jinja2 variables into a single dictionary.

        :return: A dictionary of all jinja2 variables needed to run u-ak283
        :rtype: dict
        """
        template_variables = {}
        template_variables.update(self.flag_variables())
        template_variables.update(self.stream_variables())
        template_variables.update(self.plugin_variables())
        template_variables.update(self.general_variables())
        template_variables.update(self.final_cycle_point_variable())

        return template_variables

    @property
    def request_path(self) -> str:
        """
        In order to run subtasks in the convert suite (extract, QC and transfer), the suite needs to know
        the path to the request cfg file. This path is often specified as a relative path, so we need to
        get the absolute path if this is the case to pass to the suite config.

        :return: Absolute path to the request.cfg
        :rtype: str
        """
        if os.path.isabs(self._arguments.request_path):
            request_cfg_path = self._arguments.request_path
        else:
            request_cfg_path = os.path.abspath(self._arguments.request_path)
        return request_cfg_path

    def flag_variables(self) -> dict:
        """ A grouping of flag-like jinja2 variables.

        :return: A dictionary of jinja2 flags.
        :rtype: dict
        """
        flag_variables = {
            'DEV_MODE': _DEV,
            'EMAIL_NOTIFICATIONS': not self._request.conversion.no_email_notifications,
            'RUN_EXTRACT': not self._request.conversion.skip_extract,
            'RUN_EXTRACT_VALIDATION': not self._request.conversion.skip_extract_validation,
            'RUN_QC': not self._request.conversion.skip_qc,
            'RUN_TRANSFER': not self._request.conversion.skip_archive,
            'RELAXED_CMOR': self._request.common.is_relaxed_cmor(),
            'CONTINUE_IF_MIP_CONVERT_FAILED': self._request.conversion.continue_if_mip_convert_failed,
        }

        return flag_variables

    def general_variables(self) -> dict:
        """ A grouping of general jinja2 variables.

        :return: A dictionary of jinja2 general variables
        :rtype: dict
        """

        general_variables = {
            'ARCHIVE_DATA_VERSION': self._request.data.data_version,
            'MIP_ERA': self._request.metadata.mip_era,
            'CDDS_CONVERT_PROC_DIR': component_directory(self._request, 'convert'),
            'CDDS_VERSION': _NUMERICAL_VERSION,
            'CALENDAR': self._request.metadata.calendar,
            'END_DATE': str(self._request.data.end_date),
            'INPUT_DIR': input_data_directory(self._request),
            'OUTPUT_MASS_ROOT': self._request.data.output_mass_root,
            'OUTPUT_MASS_SUFFIX': self._request.data.output_mass_suffix,
            'MIP_CONVERT_CONFIG_DIR': component_directory(self._request, 'configure'),
            'MODEL_ID': self._request.metadata.model_id,
            'NTHREADS_CONCATENATE': (NTHREADS_CONCATENATE),
            'OUTPUT_DIR': output_data_directory(self._request),
            'PARALLEL_TASKS': PARALLEL_TASKS,
            'REF_DATE': str(self._request.metadata.base_date),
            'REQUEST_CONFIG_PATH': self.request_path,
            'ROOT_DATA_DIR': self._request.common.root_data_dir,
            'ROOT_PROC_DIR': self._request.common.root_proc_dir,
            'START_DATE': str(self._request.data.start_date),
            'TARGET_SUITE_NAME': self._request.data.model_workflow_id,
        }

        if 'CDDS_DIR' in os.environ:
            general_variables['CDDS_DIR'] = os.environ['CDDS_DIR']
        else:
            self.logger.info('Environment variable CDDS_DIR not found. Skipping interpolation into rose suite')

        # if location:
        #     general_variables['LOCATION'] = location

        return general_variables

    def plugin_variables(self) -> dict:
        """Set various jinja2 variables relating to plugins.

        :return: A dictionary of jinja2 plugin variables.
        :rtype: dict
        """
        plugin_variables = {'EXTERNAL_PLUGIN': "",
                            'EXTERNAL_PLUGIN_LOCATION': "",
                            'USE_EXTERNAL_PLUGIN': False,
                            'PLUGIN_ID': self._request.metadata.mip_era}

        if self._request.common.external_plugin:
            plugin_variables['EXTERNAL_PLUGIN'] = self._request.common.external_plugin
            plugin_variables['EXTERNAL_PLUGIN_LOCATION'] = self._request.common.external_plugin_location
            plugin_variables['USE_EXTERNAL_PLUGIN'] = True

        if self._request.common.force_plugin:
            plugin_variables['PLUGIN_ID'] = self._request.common.force_plugin

        return plugin_variables

    def stream_variables(self) -> dict:
        """ Return a copy of self.stream_config without FINAL_CYCLE_POINT.

        :return: A dictionary of jinja2 stream variables.
        :rtype: dict
        """
        stream_variables = {k: v for k, v in self.stream_config.items() if k != "FINAL_CYCLE_POINT"}

        return stream_variables

    def final_cycle_point_variable(self) -> dict:
        """ A Cylc workflow can only have one final cycle point, so the latest point out of all streams
        is used.

        :return: The latest FINAL_CYCLE_POINT out of all of the streams.
        :rtype: dict
        """
        final_cycle_points = self.stream_config["FINAL_CYCLE_POINT"].values()
        final_cycle_points = [TimePointParser().parse(point) for point in final_cycle_points]
        final_cycle_point_variable = {"FINAL_CYCLE_POINT": str(max(final_cycle_points))}

        return final_cycle_point_variable

    def update(self) -> None:
        """ Write the self.template_variables to the rose-suite.conf file."""
        try:
            changes_applied = update_suite_conf_file(self.config_file,
                                                     self.section,
                                                     self.template_variables,
                                                     raw_value=False)
        except Exception as err:
            self.logger.exception(err)
        else:
            self.logger.info(f'Update to {self.config_file} successful. Changes made: "{changes_applied}"')
