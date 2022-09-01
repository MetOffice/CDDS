# (C) British Crown Copyright 2019-2022, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
# pylint: disable = no-member
"""
Tests for :mod:`arguments.py`.
"""
import os
import unittest

from cdds.common.constants import PACKAGE_KEY_FOR_ARGUMENTS
from cdds.arguments import retrieve_script_arguments, Arguments


class TestRetrieveScriptArguments(unittest.TestCase):
    """
    Tests for :func:`retrieve_script_arguments` in :mod:`arguments.py`.
    """
    def setUp(self):
        self.package = PACKAGE_KEY_FOR_ARGUMENTS
        self.script_name = 'script1'
        self.default_package_and_script_args = {
            self.package: {
                'param2': 'arg6', 'param4': 'arg4', 'param5': 'arg5'},
            self.script_name: {
                'param1': 'arg8', 'param5': 'arg9', 'param6': 'arg6'},
            'script2': {'param7': 'arg7'}}

    def test_construct_default_arguments(self):
        default_package_args, default_script_args = retrieve_script_arguments(
            self.script_name, self.default_package_and_script_args)
        self.assertEqual(default_package_args,
                         self.default_package_and_script_args[self.package])
        self.assertEqual(default_script_args,
                         self.default_package_and_script_args[
                             self.script_name])

    def test_construct_default_arguments_with_no_package_option(self):
        del self.default_package_and_script_args[self.package]
        default_package_args, default_script_args = retrieve_script_arguments(
            self.script_name, self.default_package_and_script_args)
        self.assertEqual(default_package_args, {})
        self.assertEqual(default_script_args,
                         self.default_package_and_script_args[
                             self.script_name])

    def test_construct_default_arguments_with_no_script_option(self):
        del self.default_package_and_script_args[self.script_name]
        default_package_args, default_script_args = retrieve_script_arguments(
            self.script_name, self.default_package_and_script_args)
        self.assertEqual(default_package_args,
                         self.default_package_and_script_args[self.package])
        self.assertEqual(default_script_args, {})


class TestArguments(unittest.TestCase):
    """
    Tests for :class:`Arguments` in :mod:`arguments.py`.
    """
    def setUp(self):
        self.default_global_args = {
            'param1': 'arg1', 'param2': 'arg2', 'param3': 'arg3'}
        self.default_package_args = {
            'param2': 'arg6', 'param4': 'arg4', 'param5': 'arg5'}
        self.default_script_args = {
            'param1': 'arg7', 'param5': 'arg8', 'param6': 'arg6'}
        self.arguments = Arguments(
            self.default_global_args, self.default_package_args,
            self.default_script_args)

    def test_arguments(self):
        reference = {'param1': 'arg7', 'param2': 'arg6', 'param3': 'arg3',
                     'param4': 'arg4', 'param5': 'arg8', 'param6': 'arg6'}
        self.assertEqual(self.arguments.args, reference)

    def test_attributes(self):
        self.assertEqual(self.arguments.param1, 'arg7')
        self.assertEqual(self.arguments.param2, 'arg6')
        self.assertEqual(self.arguments.param3, 'arg3')
        self.assertEqual(self.arguments.param4, 'arg4')
        self.assertEqual(self.arguments.param5, 'arg8')
        self.assertEqual(self.arguments.param6, 'arg6')

    def test_add_user_args_arguments(self):
        info = {'paramA': 'argA', 'paramB': 'argB', 'paramC': 'argC',
                'param4': 'argD'}
        user_args = DummyNamespace(info)
        self.arguments.add_user_args(user_args)
        reference = {'param1': 'arg7', 'param2': 'arg6', 'param3': 'arg3',
                     'param4': 'argD', 'param5': 'arg8', 'param6': 'arg6',
                     'paramA': 'argA', 'paramB': 'argB', 'paramC': 'argC'}
        self.assertEqual(self.arguments.args, reference)

    def test_add_user_args_attributes(self):
        info = {'paramA': 'argA', 'paramB': 'argB', 'paramC': 'argC',
                'param4': 'argD'}
        user_args = DummyNamespace(info)
        self.arguments.add_user_args(user_args)
        self.assertEqual(self.arguments.param1, 'arg7')
        self.assertEqual(self.arguments.param2, 'arg6')
        self.assertEqual(self.arguments.param3, 'arg3')
        self.assertEqual(self.arguments.param4, 'argD')
        self.assertEqual(self.arguments.param5, 'arg8')
        self.assertEqual(self.arguments.param6, 'arg6')
        self.assertEqual(self.arguments.paramA, 'argA')
        self.assertEqual(self.arguments.paramB, 'argB')
        self.assertEqual(self.arguments.paramC, 'argC')

    def test_mip_table_dir(self):
        default_data_request_version = '01.00.50'
        root_mip_table_dir = '/root/mip/table/dir/'
        default_global_args = {
            'data_request_version': default_data_request_version,
            'root_mip_table_dir': root_mip_table_dir}
        arguments = Arguments(default_global_args, {}, {})
        default_mip_table_dir = os.path.join(
            root_mip_table_dir, default_data_request_version)
        self.assertEqual(arguments.mip_table_dir, default_mip_table_dir)
        data_request_version = '01.00.60'
        info = {'data_request_version': data_request_version}
        user_args = DummyNamespace(info)
        arguments.add_user_args(user_args)
        reference = os.path.join(root_mip_table_dir, data_request_version)
        self.assertEqual(arguments.mip_table_dir, reference)


class DummyNamespace(object):
    def __init__(self, info):
        for key, value in list(info.items()):
            setattr(self, key, value)


if __name__ == '__main__':
    unittest.main()
