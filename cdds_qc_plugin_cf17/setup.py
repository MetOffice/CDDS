# (C) British Crown Copyright 2018-2021, Met Office.
# Please see LICENSE.rst for license details.
"""
Setup script for the CDDS QC CMIP6 plugin package.
"""
import imp
import os
from setuptools import setup, find_packages


def extract_version():
    """
    Return the version number of CDDS QC CF1.7 plugin.
    """
    filename = os.path.join('cdds_qc_plugin_cf17', '__init__.py')
    imported_module = imp.load_source('__init__', filename)
    version = imported_module.__version__
    return version


def extract_readme():
    """
    Return the contents of the README.rst file in CDDS QC CF1.7 plugin.
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


setup(name='cdds_qc_plugin_cf17',
      version=extract_version(),
      description=('The CF1.7 plugin is an extension of the original CF1.6 '
                   'checker, providing some additional features and '
                   'configurability.'),
      long_description=extract_readme(),
      keywords='cdds qc',
      url='https://code.metoffice.gov.uk/trac/cdds',
      author='Piotr Florek',
      author_email='piotr.florek@metoffice.gov.uk',
      maintainer='Piotr Florek',
      maintainer_email='piotr.florek@metoffice.gov.uk',
      platforms=['Linux', 'Unix'],
      packages=find_packages(),
      data_files=find_data_files(),
      test_suite='nose.collector',
      tests_require=['nose'],
      include_package_data=True,
      zip_safe=False,
      entry_points={'compliance_checker.suites': [
          'cf17 = cdds_qc_plugin_cf17.cf17:CF17Check']
      })
