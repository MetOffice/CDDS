# (C) British Crown Copyright 2024, Met Office.
# Please see LICENSE.rst for license details.
from pathlib import Path
from unittest import mock
from unittest.mock import Mock
import collections

import pytest

from cdds.configure.constants import FILENAME_TEMPLATE
from cdds.convert.configure_workflow.stream_components import StreamComponents
from cdds.tests.factories.request_factory import simple_request


class TestUserConfigs:
    def setup_method(self):
        self.arguments = Mock()
        self.arguments.user_config_template_name = FILENAME_TEMPLATE
        self.request = simple_request()

    @mock.patch("cdds.convert.configure_workflow.stream_components.component_directory")
    def test_user_configs(self, mock_component_directory, tmp_path: Path):
        proc = tmp_path / "configure"
        proc.mkdir()
        test_file = proc / "mip_convert.cfg.atmos-native"
        test_file.write_text("[stream_ap4]\nCMIP6_AERmon = emiso2")
        mock_component_directory.return_value = proc

        stream_components = StreamComponents(self.arguments, self.request)
        configs = stream_components.user_configs()
        assert "atmos-native" in configs.keys()
        assert "stream_ap4" in configs["atmos-native"].sections

    @mock.patch("cdds.convert.configure_workflow.stream_components.component_directory")
    def test_no_user_configs_found(self, mock_component_directory, tmp_path: Path):
        proc = tmp_path / "configure"
        proc.mkdir()
        test_file = proc / "wrong.cfg.name"
        test_file.write_text("[stream_ap4]")
        mock_component_directory.return_value = proc
        stream_components = StreamComponents(self.arguments, self.request)

        with pytest.raises(FileNotFoundError) as excinfo:
            stream_components.user_configs()

        assert "No configuration files were found in" in str(excinfo.value)


class TestBuildStreamComponents:
    def setup_method(self):
        self.arguments = Mock()
        self.arguments.user_config_template_name = FILENAME_TEMPLATE
        self.request = simple_request()

    def test_1(self):
        self.arguments.streams = []
        self.request.data.streams = ["ap4", "ap5", "onm"]
        DummyConfig = collections.namedtuple("DummyConfig", ["sections"])
        base_sections = ["cmor_setup", "cmor_dataset", "request"]

        config_file_1 = ["stream_ap4", "stream_ap5"]
        config_file_2 = ["stream_onm_diad-T"]

        data = {
            "atmos-native": DummyConfig(base_sections + config_file_1),
            "ocean-native-diad-T": DummyConfig(base_sections + config_file_2),
        }

        expected = {
            "ap4": {"atmos-native": ""},
            "ap5": {"atmos-native": ""},
            "onm": {"ocean-native-diad-T": "diad-T"},
        }

        with mock.patch.object(StreamComponents, "user_configs") as user_configs_mocked:
            user_configs_mocked.return_value = data
            stream_components = StreamComponents(self.arguments, self.request)
            stream_components.build_stream_components()

        assert expected == stream_components.stream_substreams


class TestValidateStreams:
    def setup_method(self):
        self.arguments = Mock()
        self.request = simple_request()

    @mock.patch.object(
        StreamComponents, "active_streams", new_callable=mock.PropertyMock
    )
    def test_no_activte_streams(self, mock_active_streams):
        mock_active_streams.return_value = []
        stream_components = StreamComponents(self.arguments, self.request)

        with pytest.raises(RuntimeError) as excinfo:
            stream_components.validate_streams()

        assert "No streams to process" in str(excinfo.value)


class TestStreams:
    def setup_method(self):
        self.arguments = Mock()
        self.arguments.user_config_template_name = FILENAME_TEMPLATE
        self.request = simple_request()

    def test_streams(self):
        self.arguments.streams = []
        self.request.data.streams = ["ap4", "ap5", "onm"]
        stream_components = StreamComponents(self.arguments, self.request)
        assert stream_components.streams == ["ap4", "ap5", "onm"]

    def test_cli_override(self):
        self.arguments.streams = ["ap4"]
        self.request.data.streams = ["ap4", "ap5", "onm"]
        stream_components = StreamComponents(self.arguments, self.request)
        assert stream_components.streams == ["ap4"]

    def test_rejected_streams(self):
        self.arguments.streams = ["onm", "ap6"]
        self.request.data.streams = ["ap4", "ap5", "onm"]
        stream_components = StreamComponents(self.arguments, self.request)
        assert stream_components.streams == ["onm"]


class TestActiveStreams:
    def setup_method(self):
        self.arguments = Mock()
        self.request = simple_request()

    def test_activte_streams(self):
        stream_components = StreamComponents(self.arguments, self.request)
        stream_components.stream_components = {"ap4": None, "ap5": None}
        assert ["ap4", "ap5"] == stream_components.active_streams

    def test_no_activte_streams(self):
        stream_components = StreamComponents(self.arguments, self.request)
        expected = []
        assert expected == stream_components.active_streams
