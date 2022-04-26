# (C) British Crown Copyright 2017-2021, Met Office.
# Please see LICENSE.rst for license details.
"""
Setup script for the CDDS Convert package.
"""
import imp
import os
from setuptools import setup, find_packages


def extract_version():
    """
    Return the version number of CDDS Convert.
    """
    filename = os.path.join('cdds_convert', '__init__.py')
    imported_module = imp.load_source('__init__', filename)
    version = imported_module.__version__
    return version


def extract_readme():
    """
    Return the contents of the README.rst file in CDDS Convert.
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
    data_files = [('', ['CHANGES.rst', 'INSTALL.rst', 'LICENSE.rst',
                        'README.rst', 'pylintrc', 'setup.py', 'setup.cfg'])]
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


setup(name='cdds_convert',
      version=extract_version(),
      description=('The CDDS Convert package manages the running of MIP '
                   'Convert processes for the Climate Data Dissemination '
                   'System.'),
      long_description=extract_readme(),
      keywords='cdds convert',
      url='https://code.metoffice.gov.uk/trac/cdds',
      author='Matthew Mizielinski',
      author_email='matthew.mizielinski@metoffice.gov.uk',
      maintainer='Matthew Mizielinski',
      maintainer_email='matthew.mizielinski@metoffice.gov.uk',
      platforms=['Linux', 'Unix'],
      package_data={'cdds_convert': ['arguments.json', 'sizing/*json']},
      packages=find_packages(),
      data_files=find_data_files(),
      test_suite='nose.collector',
      tests_require=['nose'],
      scripts=find_scripts(['bin']),
      include_package_data=True,
      zip_safe=False)
