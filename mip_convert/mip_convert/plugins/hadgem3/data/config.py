# (C) British Crown Copyright 2015-2021, Met Office.
# Please see LICENSE.md for license details.
"""
The :mod:`config` module defines the information to be read from the
|model to MIP mapping| configuration file.
"""


def mappings_config_info():
    """
    Define the information to be read from the |model to MIP mapping|
    configuration file.
    """
    return {
        'blev': {
            'python_type': float,
            'value_type': 'multiple'},
        'cell_methods': {
            'python_type': str,
            'value_type': 'single'},
        'comment': {
            'python_type': str,
            'value_type': 'single'},
        'component': {
            'python_type': str,
            'value_type': 'multiple'},
        'constraint': {
            'python_type': str,
            'value_type': 'multiple'},
        'depth': {
            'python_type': float,
            'value_type': 'multiple'},
        'dimension': {
            'python_type': str,
            'value_type': 'multiple'},
        'expression': {
            'python_type': str,
            'value_type': 'single'},
        'lblev': {
            'python_type': int,
            'value_type': 'single'},
        'lbplev': {
            'python_type': int,
            'value_type': 'single'},
        'lbproc': {
            'python_type': int,
            'value_type': 'single'},
        'lbtim': {
            'python_type': int,
            'value_type': 'single'},
        'mip_table_id': {
            'python_type': str,
            'value_type': 'multiple'},
        'notes': {
            'python_type': str,
            'value_type': 'single'},
        'positive': {
            'python_type': str,
            'value_type': 'single'},
        'reviewer': {
            'python_type': str,
            'value_type': 'single'},
        'stash': {
            'python_type': str,
            'value_type': 'single'},
        'status': {
            'python_type': str,
            'value_type': 'single'},
        'units': {
            'python_type': str,
            'value_type': 'single'},
        'valid_min': {
            'python_type': float,
            'value_type': 'single'},
        'variable_name': {
            'python_type': str,
            'value_type': 'single'},
    }
