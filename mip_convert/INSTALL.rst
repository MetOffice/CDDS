.. Copyright (C) British Crown (Met Office) & Contributors.
.. Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
.. See the LICENSE file in the top level of this repository for full details.

Installing MIP Convert
======================

Installing MIP Convert currently requires the `cdds` package to be installed. 
Please follow the CDDS installation instructions replicated below.

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
