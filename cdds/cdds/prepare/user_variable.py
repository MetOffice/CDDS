# (C) British Crown Copyright 2022-2025, Met Office.
# Please see LICENSE.md for license details.
import logging
from collections import defaultdict
from typing import Dict, Tuple, List

from cdds.common.mip_tables import UserMipTables
from cdds.common.plugins.plugins import PluginStore


class UserDefinedVariable:
    """
    Class to hold information on a user requested variable built from mip tables.
    It is designed to have close similarity to the DataRequestVariable Class from
    cdds.prepare.data_request_interface.
    """

    def __init__(
        self,
        mip_table: str,
        var_name: str,
        variable_metadata: dict,
        stream: str | None = None,
        frequency: str | None = None,
    ) -> None:
        """
        Construct an object representing a variable from given mip tables,
        based on its |MIP| table and |MIP requested variable| name.

        :param mip_table: |MIP table| for the variable.
        :type mip_table: str
        :param var_name: |MIP requested variable name.
        :type var_name: str
        :param mip_table_dir: Directory containing Mip tables
        :type mip_table_dir: str
        :param stream: Only consider this stream (optional)
        :type stream: str
        """
        self.mip_table = mip_table
        self.var_name = var_name
        self.stream = stream
        self.var_dict = variable_metadata
        self.frequency = frequency

        self.var_dict["mip_table"] = self.mip_table

        self._set_attributes_from_variable()

    def _set_attributes_from_variable(self) -> None:
        # Set attributes from the given mip table
        self.cell_measures = self.var_dict["cell_measures"]
        self.cell_methods = self.var_dict["cell_methods"]
        self.comment = self.var_dict["comment"]
        self.description = self.var_dict["comment"]
        self.long_name = self.var_dict["long_name"]
        self.modeling_realm = self.var_dict.get("modeling_realm", None)
        self.output_variable_name = self.var_name
        self.positive = self._blank_to_none(self.var_dict["positive"])
        self.standard_name = self.var_dict["standard_name"]
        self.type = self.var_dict.get("type", None)
        self.units = self.var_dict["units"]
        self.variable_name = self.var_name

        # Cmip7
        if isinstance(self.var_dict["dimensions"], list):
            self.dimensions = self.var_dict["dimensions"]
        else:
            self.dimensions = self.var_dict["dimensions"].split()

        if not self.frequency:
            self.frequency = self.var_dict["frequency"]

    def _blank_to_none(self, value: str) -> str | None:
        result = value
        if value == "":
            result = None
        return result


def _blank_to_none(value: str) -> str:
    result = value
    if value == '':
        result = None
    return result


def parse_variable_list(mip_tables: UserMipTables, requested_variables: list[str]) -> list[UserDefinedVariable]:
    logger = logging.getLogger()

    variable_list = []

    for var_str in requested_variables:
        if "@" in var_str:
            if ":" in var_str:
                mip_table, var_str = var_str.split("/", maxsplit=1)
                variable, var_str = var_str.split("@")
                frequency, stream = var_str.split(":")
            else:
                raise NotImplementedError("Stream must be explicitly specified.")
        else:
            if ":" in var_str:
                mip_table, var_str = var_str.split("/", maxsplit=1)
                variable, stream = var_str.split(":")
            else:
                stream_info = PluginStore.instance().get_plugin().stream_info()
                mip_table, variable = var_str.split("/")
                stream_id, substream = stream_info.retrieve_stream_id(variable, mip_table)
                stream = "{}/{}".format(stream_id, substream) if substream is not None else stream_id
            frequency = None

        if mip_table not in mip_tables.tables:
            err = 'Requested Mip Table "{}" not found in given Mip Tables'.format(mip_table)
            logger.error(err)
            raise RuntimeError(err)

        if variable not in mip_tables.get_variables(mip_table):
            err = 'Requested variable "{}" not found in the "{}" Mip Table'.format(variable, mip_table)
            logger.error(err)
            raise RuntimeError(err)

        variable_metadata = mip_tables.get_variable_meta(mip_table, variable)
        user_variable = UserDefinedVariable(mip_table, variable, variable_metadata, stream, frequency)
        variable_list.append(user_variable)

    return variable_list
