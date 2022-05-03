.. (C) British Crown Copyright 2018, Met Office.
.. Please see LICENSE.rst for license details.

Installing Compliance Checker CMIP6 plugin
==========================================

Assuming a working installation of ``ioos/compliance_checker``, the plugin can
be installed simply by running::

    cd cc-plugin-cmip6
    pip install .

or::

    python setup.py install

Testing the installation
========================

Run only the unit tests::

    python setup.py nosetests

Run only the unit tests and doctests::

    python setup.py nosetests --with-doctest

Run only the doctests::

    python setup.py nosetests -e ^test --with-doctest


Building the documentation
==========================

.. code:: python

    python setup.py build_sphinx -Ea
