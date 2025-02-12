# (C) British Crown Copyright 2015-2024, Met Office.
# Please see LICENSE.rst for license details.
"""
Setup script for the MIP Convert package.
"""
import os
from setuptools import setup, find_packages
from typing import AnyStr
from importlib.machinery import SourceFileLoader


def extract_version(module_name: str) -> AnyStr:
    """
    Returns the version number of the module.

    Parameters
    ----------
    module_name: str
        Name of the module

    Returns
    -------
    str
        The CDDS module version
    """
    filename = os.path.join(module_name, '__init__.py')
    imported_module = SourceFileLoader(module_name, filename).load_module()
    version = imported_module.__version__
    return version


def extract_readme():
    """
    Return the contents of the README.rst file in MIP Convert.
    """
    with open('README.rst') as readme_file:
        return readme_file.read()


def data_file_search(directory):
    """
    Return a list in the form [(p1, f1), (p2, f2), ...], where p<#> is
    a string containing the path to a directory (the root of the
    directory is provided by the 'directory' argument) and f<#> is a
    list containing the files in that directory.
    """
    search_dirs = [dirpath for (dirpath, _, _) in os.walk(directory)]
    # The 'search_dir' string will always start with the 'directory' string
    return [(search_dir, [os.path.join(search_dir, filename) for filename in
                          os.listdir(search_dir) if
                          os.path.isfile(os.path.join(search_dir, filename))])
            for search_dir in search_dirs]


def find_data_files():
    """
    Return a list to use as the value of 'data_files' in the call to
    'setup'.
    """
    data_files = [('', ['CHANGES.md', 'INSTALL.rst', 'LICENSE.rst',
                        'README.rst', 'pylintrc', 'setup.py', 'setup.cfg'])]
    data_files.extend(data_file_search(directory='etc'))
    data_files.extend(data_file_search(directory='doc'))
    return data_files


def find_scripts(directories):
    """
    Find and return all the scripts in the directories given.
    The directories are assumed to contain just scripts.
    Directories need not exist: any that don't (or aren't directories)
    will be skipped.

    This returns a list of (dir [script ...]) tuples, for each dir in
    dirs.
    """
    scripts = []
    for directory in directories:
        if os.path.isdir(directory):
            scripts.extend([os.path.join(directory, entry)
                            for entry in os.listdir(directory)
                            if os.path.isfile(os.path.join(directory, entry))])
    return scripts


setup(name='mip_convert',
      version=extract_version('mip_convert'),
      description=('The MIP Convert package enables a user to produce the'
                   'output netCDF files for a MIP using model output files.'),
      long_description=extract_readme(),
      keywords='mip convert netcdf model request variable transform pp',
      url='https://code.metoffice.gov.uk/trac/cdds',
      author='Emma Hogan, Jamie Kettleborough',
      author_email='emma.hogan@metoffice.gov.uk',
      maintainer='Emma Hogan',
      maintainer_email='emma.hogan@metoffice.gov.uk',
      platforms=['Linux', 'Unix'],
      packages=find_packages(),
      data_files=find_data_files(),
      scripts=find_scripts(['bin']),
      include_package_data=True,
      zip_safe=False)
