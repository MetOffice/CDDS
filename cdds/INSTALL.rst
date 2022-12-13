.. (C) British Crown Copyright 2022, Met Office.
.. Please see LICENSE.rst for license details.

Installing CDDS
===============

Development mode 
----------------

CDDS can be installed for development in a conda environment using

conda env create -f environment_dev.yml -p <installation location>

Note that at the Met Office the default installation location is $HOME/.conda

Activating the code is then performed using the "setup_env_for_devel"

Tests can be run using the `run_all_tests` script which uses pytest.

Production mode
---------------

See the CDDS Confluence pages for the latest installation and testing procedure.

Building the documentation
==========================

.. code:: python

   python setup.py build_sphinx -Ea
