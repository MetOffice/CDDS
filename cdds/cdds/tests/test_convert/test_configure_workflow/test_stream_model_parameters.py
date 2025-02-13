# (C) British Crown Copyright 2024, Met Office.
# Please see LICENSE.md for license details.
from unittest.mock import Mock

from metomi.isodatetime.data import Duration


from cdds.common.plugins.plugin_loader import load_plugin
from cdds.convert.configure_workflow.stream_model_parameters import (
    StreamModelParameters,
)
from cdds.tests.factories.request_factory import simple_request


class TestConcatenationPeriod:
    def setup_method(self):
        self.request = simple_request()
        self.stream = "ap4"
        self.components = Mock()
        load_plugin()

    def test_max_size_101_years(self):
        stream_model_parameters = StreamModelParameters(self.request,
                                                        self.stream,
                                                        self.components)
        model_params = Mock()
        model_params.full_sizing_info.return_value = {
            "mon": {"75-330-360": 50,
                    "default": 101},
            "monPt": {"86-144-192": 50,
                      "default": 100}
        }
        stream_model_parameters._model_params = model_params

        expected = Duration(years=101)
        result = stream_model_parameters.concatenation_period()

        assert expected == result

    def test_max_size_92_years(self):
        stream_model_parameters = StreamModelParameters(self.request,
                                                        self.stream,
                                                        self.components)
        model_params = Mock()
        model_params.full_sizing_info.return_value = {
            "mon": {"75-330-360": 20,
                    "default": 92},
            "monPt": {"86-144-192": 50,
                      "default": 50}
        }
        stream_model_parameters._model_params = model_params

        expected = Duration(years=92)
        result = stream_model_parameters.concatenation_period()

        assert expected == result

    def test_no_sizing_info(self):
        stream_model_parameters = StreamModelParameters(self.request,
                                                        self.stream,
                                                        self.components)

        model_params = Mock()
        model_params.full_sizing_info.return_value = None
        stream_model_parameters._model_params = model_params

        expected = Duration(years=10)
        result = stream_model_parameters.concatenation_period()

        assert expected == result


class TestCyclingFrequency:
    def setup_method(self):
        self.request = simple_request()
        self.stream = "ap4"
        self.components = Mock()
        load_plugin()

    def test_default_cycling_frequency(self):
        stream_model_parameters = StreamModelParameters(self.request,
                                                        self.stream,
                                                        self.components)
        model_params = Mock()
        model_params.cycle_length.return_value = "P2Y"
        stream_model_parameters._model_params = model_params

        expected = Duration(years=2)
        result = stream_model_parameters.cycling_frequency()
        assert expected == result

    def test_override_cycling_frequency(self):
        self.request.conversion.override_cycling_frequency = ["ap4=P5Y", "ap5=P10Y"]
        stream_model_parameters = StreamModelParameters(self.request,
                                                        self.stream,
                                                        self.components)
        model_params = Mock()
        model_params.cycle_length.return_value = "P2Y"
        stream_model_parameters._model_params = model_params

        expected = Duration(years=5)
        result = stream_model_parameters.cycling_frequency()
        assert expected == result


class TestMemory:
    def setup_method(self):
        self.request = simple_request()
        self.stream = "ap4"
        self.components = Mock()
        load_plugin()

    def test_default_memory(self):
        stream_model_parameters = StreamModelParameters(self.request,
                                                        self.stream,
                                                        self.components)
        stream_model_parameters.stream_components = {"ap4": ["foo", "bar"]}
        model_params = Mock()
        model_params.memory.return_value = "8G"
        stream_model_parameters._model_params = model_params

        expected = {"bar": "8G", "foo": "8G"}
        result = stream_model_parameters.memory

        assert expected == result

    def test_scale_memory(self):
        self.request.conversion.scale_memory_limits = 0.5
        stream_model_parameters = StreamModelParameters(self.request,
                                                        self.stream,
                                                        self.components)
        stream_model_parameters.stream_components = {"ap4": ["foo", "bar"]}
        model_params = Mock()
        model_params.memory.return_value = "8G"
        stream_model_parameters._model_params = model_params

        expected = {"bar": "4096M", "foo": "4096M"}
        result = stream_model_parameters.memory

        assert expected == result


class TestAsJinja2:
    def setup_method(self):
        self.request = simple_request()
        self.stream = "ap4"
        self.components = Mock()

        load_plugin()

    def test_jinja2(self):
        stream_model_parameters = StreamModelParameters(self.request,
                                                        self.stream,
                                                        self.components)
        stream_model_parameters.stream_components = {"ap4": ["atmos-native"]}
        stream_model_parameters.stream_substreams = {"ap4": {"atmos-native": ""}}

        model_params = Mock()
        model_params.temp_space.return_value = "2000"
        model_params.memory.return_value = "8G"
        stream_model_parameters._model_params = model_params

        expected = {
            'STREAMS': "ap4",
            'MEMORY_CONVERT': {"atmos-native": "8G"},
            'MIP_CONVERT_TMP_SPACE': "2000",
            'STREAM_COMPONENTS': ["atmos-native"],
            'STREAM_SUBSTREAMS': {"atmos-native": ""},
        }
        result = stream_model_parameters.as_jinja2()

        assert expected == result
