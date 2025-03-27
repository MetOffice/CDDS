# (C) British Crown Copyright 2024-2025, Met Office.
# Please see LICENSE.md for license details.
from pathlib import Path
from unittest.mock import MagicMock

from cdds import _DEV
from cdds.convert.configure_workflow.configure_template_variables import ConfigureTemplateVariables


class TestConfigureTemplateVariables:
    def setup_method(self):
        self.arguments = MagicMock()
        self.request = MagicMock()
        self.stream_config = {
            "CONCATENATION_FIRST_CYCLE_OFFSET": {"ap4": "P27000D"},
            "CONCATENATION_WINDOW": {"ap4": "P100Y"},
            "CONVERT_ALIGNMENT_OFFSET": {"ap4": "P0Y"},
            "CYCLING_FREQUENCY": {"ap4": "P5Y"},
            "DO_CONVERT_ALIGNMENT_CYCLE": {"ap4": False},
            "DO_FINAL_CONCATENATE": {"ap4": True},
            "FINAL_CONCATENATION_CYCLE": {"ap4": "2165-01-01T00:00:00Z"},
            "FINAL_CONCATENATION_WINDOW_START": {"ap4": "2150-01-01T00:00:00Z"},
            "SINGLE_CONCATENATION_CYCLE": {"ap4": False},
        }
        self.conf = "foo.conf"

    def test_stream_variables(self):
        template_variables = ConfigureTemplateVariables(self.arguments,
                                                        self.request,
                                                        self.stream_config)

        assert "FINAL_CYCLE_POINT" not in template_variables.stream_variables()

    def test_final_cycle_point_variable(self):
        stream_config = {"FINAL_CONCATENATION_CYCLE": {"ap4": "2000-01-01T00:00:00Z",
                                                       "ap5": "2032-01-01T00:00:00Z",
                                                       "ap6": "2030-01-01T00:00:00Z",
                                                       "onm": "2034-10-01T00:00:00Z"}}

        template_variables = ConfigureTemplateVariables(self.arguments,
                                                        self.request,
                                                        stream_config)
        result = template_variables.final_cycle_point_variable()
        expected = {"FINAL_CYCLE_POINT": "2034-10-01T00:00:00Z"}
        assert expected == result

    def test_flag_variables(self):
        self.request.conversion.no_email_notifications = True
        self.request.conversion.skip_extract = True
        self.request.conversion.skip_extract_validation = True
        self.request.conversion.skip_qc = False
        self.request.conversion.skip_archive = False
        self.request.common.is_relaxed_cmor.return_value = False
        self.request.conversion.continue_if_mip_convert_failed = False

        template_variables = ConfigureTemplateVariables(self.arguments,
                                                        self.request,
                                                        self.stream_config)
        expected = {
            "DEV_MODE": _DEV,
            "EMAIL_NOTIFICATIONS": False,
            "RUN_EXTRACT": False,
            "RUN_EXTRACT_VALIDATION": False,
            "RUN_QC": True,
            "RUN_TRANSFER": True,
            "RELAXED_CMOR": False,
            "CONTINUE_IF_MIP_CONVERT_FAILED": False,
        }

        assert expected == template_variables.flag_variables()

    def test_plugin_variables(self):
        self.request.metadata.mip_era = "CMIP6"
        self.request.common.external_plugin = ""
        self.request.common.force_plugin = ""
        self.request.conversion.model_params_dir = ""
        template_variables = ConfigureTemplateVariables(self.arguments,
                                                        self.request,
                                                        self.stream_config)
        expected = {'EXTERNAL_PLUGIN': "",
                    'EXTERNAL_PLUGIN_LOCATION': "",
                    'USE_EXTERNAL_PLUGIN': False,
                    'PLUGIN_ID': "CMIP6",
                    'MODEL_PARAM_DIR': ""}

        assert expected == template_variables.plugin_variables()

    def test_plugin_variables_external_plugin(self):
        self.request.metadata.mip_era = "CMIP6"
        self.request.common.external_plugin = "myplugin"
        self.request.common.external_plugin_location = "/my/custom/plugin"
        self.request.common.force_plugin = ""
        self.request.conversion.model_params_dir = ""
        template_variables = ConfigureTemplateVariables(self.arguments,
                                                        self.request,
                                                        self.stream_config)
        expected = {'EXTERNAL_PLUGIN': "myplugin",
                    'EXTERNAL_PLUGIN_LOCATION': "/my/custom/plugin",
                    'USE_EXTERNAL_PLUGIN': True,
                    'PLUGIN_ID': "CMIP6",
                    'MODEL_PARAM_DIR': ""}

        assert expected == template_variables.plugin_variables()

    def test_plugin_variables_model_params_dir_to_overload(self):
        self.request.metadata.mip_era = "CMIP6"
        self.request.common.external_plugin = "myplugin"
        self.request.common.external_plugin_location = "/my/custom/plugin"
        self.request.common.force_plugin = ""
        self.request.conversion.model_params_dir = "/path/to/model/params_dir"
        template_variables = ConfigureTemplateVariables(self.arguments,
                                                        self.request,
                                                        self.stream_config)
        expected = {'EXTERNAL_PLUGIN': "myplugin",
                    'EXTERNAL_PLUGIN_LOCATION': "/my/custom/plugin",
                    'USE_EXTERNAL_PLUGIN': True,
                    'PLUGIN_ID': "CMIP6",
                    'MODEL_PARAM_DIR': '/path/to/model/params_dir'}

        assert expected == template_variables.plugin_variables()

    def test_plugin_variables_force_plugin(self):
        self.request.metadata.mip_era = "CMIP6"
        self.request.common.external_plugin = ""
        self.request.common.force_plugin = "CORDEX"
        self.request.conversion.model_params_dir = ""
        template_variables = ConfigureTemplateVariables(self.arguments,
                                                        self.request,
                                                        self.stream_config)
        expected = {'EXTERNAL_PLUGIN': "",
                    'EXTERNAL_PLUGIN_LOCATION': "",
                    'USE_EXTERNAL_PLUGIN': False,
                    'PLUGIN_ID': "CORDEX",
                    'MODEL_PARAM_DIR': ""}

        assert expected == template_variables.plugin_variables()

    def test_plugin_variables_request_path_absolute(self, tmp_path: Path):
        request = tmp_path / "request.cfg"
        request.touch()
        self.arguments.request_path = request

        template_variables = ConfigureTemplateVariables(self.arguments,
                                                        self.request,
                                                        self.stream_config)

        assert request == template_variables.request_path
