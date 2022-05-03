# (C) British Crown Copyright 2015-2021, Met Office.
# Please see LICENSE.rst for license details.
"""
Setup script for the Hadley Centre Science Development Kit package.
"""
import imp
import os
from setuptools import setup, find_packages

# Where some things live
#
SOURCE_DIR = '.'
SCRIPT_DIRS = ['bin']
DATA_DIRS = ['doc', 'etc']
BASIC_DATA_FILES = ['LICENSE.rst', 'README.rst', 'setup.py', 'setup.cfg']


def extract_version():
    """
    Return the version number of HadSDK.
    """
    filename = os.path.join(SOURCE_DIR, 'hadsdk', '__init__.py')
    imported_module = imp.load_source('__init__', filename)
    version = imported_module.__version__
    return version


def extract_readme():
    """
    Return the contents of the README.rst file in HadSDK.
    """
    with open('README.rst') as readme_file:
        return readme_file.read()


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


def find_files_by_extension(root_dir, extensions=['json']):
    """
    Find files by extensions, returning a list of filepaths.
    """
    filelist = []
    for root, _, files in os.walk(root_dir):
        for filename in files:
            if any(map(filename.endswith, extensions)):
                filelist.append(os.path.join(root, filename))
    return filelist


def find_data_files(basics, datadirs):
    """
    Find data files, returning a list of (d, [file ...]).

    basics is files (in the current directory) which may not exist but
    should be returned if they do.

    datadirs is a list of directories to search for other files: all
    files, at any level, in these dirs will be returned.  Elements of
    datadirs need not exist: any that don't (or aren't directories)
    will be skipped.

    """
    files = [('', [name for name in basics if os.path.isfile(name)])]
    for datadir in datadirs:
        if os.path.isdir(datadir):
            files.extend([(directory, [os.path.join(directory, entry)
                                       for entry in entries])
                          for (directory, _, entries) in os.walk(datadir)])
    return files


setup(name='hadsdk',
      version=extract_version(),
      description=('The Hadley Centre Science Development Kit package '
                   'contains a collection of generic Python code used by one '
                   'or more of the CDDS components.'),
      long_description=extract_readme(),
      keywords='hadsdk',
      url='https://code.metoffice.gov.uk/trac/cdds',
      author='Jamie Kettleborough, Phil Bentley, Paul Whitfield',
      author_email='jamie.kettleborough@metoffice.gov.uk',
      maintainer='Emma Hogan',
      maintainer_email='emma.hogan@metoffice.gov.uk',
      platforms=['Linux', 'Unix'],
      package_data={
          'hadsdk': ['grids.cfg', 'streams.cfg',]},
      package_dir={'': SOURCE_DIR},
      packages=find_packages(SOURCE_DIR),
      data_files=find_data_files(BASIC_DATA_FILES, DATA_DIRS) +
                 find_files_by_extension(os.path.join(SOURCE_DIR, 'hadsdk')) +
                 find_files_by_extension(os.path.join(SOURCE_DIR, 'hadsdk', 'general_config'), 'cfg'),
      test_suite='nose.collector',
      tests_require=['nose'],
      scripts=find_scripts(SCRIPT_DIRS),
      include_package_data=True,
      zip_safe=False)
