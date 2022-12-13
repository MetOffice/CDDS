# (C) British Crown Copyright 2019-2021, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
"""
Common functions for tests.
"""
import subprocess
import jinja2

from mip_convert.common import parse_to_loadables
from mip_convert.process.config import mappings_config


class DummyMapping(object):
    def __init__(self, expression=None, dimension=None, mip_requested_variable_name=None, mip_table_id=None,
                 positive=None, status=None, units=None):
        if expression is not None:
            self.loadables = parse_to_loadables(expression, {}, mappings_config)
        self.dimension = dimension
        self.mip_requested_variable_name = mip_requested_variable_name
        self.mip_table_id = mip_table_id
        self.positive = positive
        self.status = status
        self.units = units


def handle_process(proc, command):
    """
    Check the output of the subprocess.Popen object proc and raise an
    appropriate error if there was a problem
    """
    out, err = proc.communicate()
    if proc.returncode != 0:
        msg = 'Command "{}" failed with code {}\n'.format(' '.join(command), proc.returncode)
        msg += '  stdout: "{}"\n'.format(out)
        msg += '  stderr: "{}"'.format(err)
        raise RuntimeError(msg)


def create_netcdf_file_with_data(source_cdl, output_filepath, x_size=360, y_size=330):
    """Generates a mock dataset from a cdl file

    Parameters
    ----------
    source_cdl : str
        CDL template
    ouput_filepath : str
        Path to the output file
    x_size : int
        length of the x coordinate
    y_size : int
        length of the y coordinate
    """

    jinjatemplate = jinja2.Template(source_cdl)
    data = ', '.join(['1'] * (x_size * y_size))
    ncgen_input = jinjatemplate.render(data=data, X=x_size, Y=y_size)

    command = ['ncgen', '-k', '4', '-o', output_filepath]

    ncgen_proc = subprocess.Popen(command, stdin=subprocess.PIPE, universal_newlines=True)
    ncgen_proc.stdin.write(ncgen_input)
    ncgen_proc.stdin.close()
    handle_process(ncgen_proc, command)


def create_simple_netcdf_file(source_cdl, output_filepath):
    """
    Write a small netCDF4 file to the specified output file path

    Parameters
    ----------
    source_cdl : str
        CDL template
    ouput_filepath : str
        Path to the output file
    """
    command = ['ncgen', '-k' '4', '-o', output_filepath]
    ncgen_proc = subprocess.Popen(command, stdin=subprocess.PIPE, universal_newlines=True)
    ncgen_proc.stdin.write(source_cdl)
    ncgen_proc.stdin.close()
    handle_process(ncgen_proc, command)
