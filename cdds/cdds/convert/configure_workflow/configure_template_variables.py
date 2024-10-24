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
    
    def update(self):
        self.flags()
        self.stream_options()
        self.external_plugin_options()
        self.general_configuration()
        self.final()

    @property
    def final_cycle_point(self):
        final_cycle_points = self.stream_config["FINAL_CYCLE_POINT"].values()
        final_cycle_points = [TimePointParser().parse(point) for point in final_cycle_points]
        return max(final_cycle_points)

    def final(self):
        changes = {"FINAL_CYCLE_POINT": str(self.final_cycle_point)}
        self.apply_changes(changes)

    @property
    def request_path(self):
        # In order to run subtasks in the convert suite (extract, QC and transfer), the suite needs to know
        # the path to the request cfg file. This path is often specified as a relative path, so we need to
        # get the absolute path if this is the case to pass to the suite config.
        if os.path.isabs(self._arguments.request_path):
            request_cfg_path = self._arguments.request_path
        else:
            request_cfg_path = os.path.abspath(self._arguments.request_path)
        return request_cfg_path

    def flags(self):
        changes = {
            'DEV_MODE': _DEV,
            'EMAIL_NOTIFICATIONS': not self._request.conversion.no_email_notifications,
            'RUN_EXTRACT': not self._request.conversion.skip_extract,
            'RUN_EXTRACT_VALIDATION': not self._request.conversion.skip_extract_validation,
            'RUN_QC': not self._request.conversion.skip_qc,
            'RUN_TRANSFER': not self._request.conversion.skip_archive,
            'RELAXED_CMOR': self._request.common.is_relaxed_cmor(),
            'CONTINUE_IF_MIP_CONVERT_FAILED': self._request.conversion.continue_if_mip_convert_failed,
        }
        self.apply_changes(changes)

    def general_configuration(self) -> None:
        """
        Update the rose-suite.conf file with suite level settings that are the same for all streams.
        Stream specific settings will be set trhough stream-specific optional config files
        (see _update_suite_opt_conf).

        :param location: The platform on which to run the tasks in the suite.
        :type location: str
        """
        changes = {
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
            changes['CDDS_DIR'] = os.environ['CDDS_DIR']
        else:
            self.logger.info('Environment variable CDDS_DIR not found. Skipping interpolation into rose suite')

        # if location:
        #     changes['LOCATION'] = location

        self.apply_changes(changes)

    def external_plugin_options(self):
        plugin_id = self._request.metadata.mip_era
        if self._request.common.force_plugin:
            plugin_id = self._request.common.force_plugin

        use_external_plugin = False
        external_plugin = ''
        external_plugin_location = ''
        if self._request.common.external_plugin:
            use_external_plugin = True
            external_plugin = self._request.common.external_plugin
            external_plugin_location = self._request.common.external_plugin_location

        changes = {'USE_EXTERNAL_PLUGIN': use_external_plugin,}
        changes = {'PLUGIN_ID': plugin_id}

        if use_external_plugin:
            changes['EXTERNAL_PLUGIN'] = external_plugin
            changes['EXTERNAL_PLUGIN_LOCATION'] = external_plugin_location
        
        self.apply_changes(changes)

    def stream_options(self):
        changes = self.stream_config
        self.apply_changes(changes)

    def apply_changes(self, changes):
        try:
            changes_applied = update_suite_conf_file(self.config_file,
                                                     self.section,
                                                     changes,
                                                     raw_value=False)
        except Exception as err:
            self.logger.exception(err)
        else:
            self.logger.info(f'Update to {self.config_file} successful. Changes made: "{changes_applied}"')
