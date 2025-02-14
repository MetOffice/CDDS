# (C) British Crown Copyright 2020-2025, Met Office.
# Please see LICENSE.md for license details.
# pylint: disable = no-member
"""
The :mod:`constants` module contains the constants required
to create a CSV sheet of requested variables.
"""
import enum


class Field(enum.Enum):
    """
    Stores all field keys (json and csv) for approved variables
    """

    def __new__(cls, *args, **kwds):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, json, csv):
        self.json = json
        self.csv = csv

    NAME = 'label', 'variable_name'
    MIPTABLE = 'miptable', 'miptable'
    ACTIVE = 'active', 'active'
    PRODUCIBLE = 'producible', 'producible'
    METHOD = 'cell_methods', 'cell_methods'
    DIMENSIONS = 'dimensions', 'dimensions'
    FREQUENCY = 'frequency', 'frequency'
    IN_MAPPINGS = 'in_mappings', 'in_mappings'
    IN_MODEL = 'in_model', 'in_model'
    PRIORITY = 'priority', 'priority'
    ENSEMBLE_SIZE = 'ensemble_size', 'ensemble_size'
    COMMENTS = 'comments', 'comments'
    STREAM = 'stream', 'stream'


class JSONType(enum.Enum):
    """
    Define field json value types
    """

    def __new__(cls, *args, **kwds):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, default_value):
        self.default_value = default_value

    VALUE = 'not defined'
    LIST = ['not defined']


# CSV header field names
HEADER_FIELDS = [Field.NAME.csv,
                 Field.MIPTABLE.csv,
                 Field.ACTIVE.csv,
                 Field.PRODUCIBLE.csv,
                 Field.METHOD.csv,
                 Field.DIMENSIONS.csv,
                 Field.FREQUENCY.csv,
                 Field.IN_MAPPINGS.csv,
                 Field.IN_MODEL.csv,
                 Field.PRIORITY.csv,
                 Field.STREAM.csv,
                 Field.ENSEMBLE_SIZE.csv,
                 Field.COMMENTS.csv]

# Mapping field names - json field name: csv field name
MAPPING_FIELDS = {
    Field.NAME.json: Field.NAME.csv,
    Field.MIPTABLE.json: Field.MIPTABLE.csv,
    Field.ACTIVE.json: Field.ACTIVE.csv,
    Field.PRODUCIBLE.json: Field.PRODUCIBLE.csv,
    Field.METHOD.json: Field.METHOD.csv,
    Field.DIMENSIONS.json: Field.DIMENSIONS.csv,
    Field.FREQUENCY.json: Field.FREQUENCY.csv,
    Field.IN_MAPPINGS.json: Field.IN_MAPPINGS.csv,
    Field.IN_MODEL.json: Field.IN_MODEL.csv,
    Field.PRIORITY.json: Field.PRIORITY.csv,
    Field.STREAM.json: Field.STREAM.csv,
    Field.ENSEMBLE_SIZE.json: Field.ENSEMBLE_SIZE.csv,
    Field.COMMENTS.json: Field.COMMENTS.csv
}

# JSON not defined value
NOT_DEFINED = 'not defined'
