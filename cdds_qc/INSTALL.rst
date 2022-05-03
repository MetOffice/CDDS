.. (C) British Crown Copyright 2018, Met Office.
.. Please see LICENSE.rst for license details.

Installing CDDS QC
==================

CDDS QC relies on a trimmed-down version of the IOOS Compliance Checker,
published as a fork of the original version on maintainer's github repository.

To install it, you need to clone this fork::

    git clone https://github.com/piotrflorek/compliance-checker

And then run `setup.py` to install the main application.

Then, proceed to install both compliance checker plugins::

    cd cc-plugin-cf17
    python setup.py install
    cd cc-plugin-cmip6
    python setup.py install

Testing the installation
========================

Run only the unit tests::

    python setup.py nosetests

Run only the unit tests and doctests::

    python setup.py nosetests --with-doctest

Run only the doctests::

    python setup.py nosetests -e ^test --with-doctest

Also, you can test the complete compliance checker installation with the
following Python code::

    from compliance_checker.runner import CheckSuite
    chs = CheckSuite()
    chs.load_all_available_checkers()
    chs.checkers
    chs.checkers["cf17"]().supported_ds

and then plugins via their unit tests.

Building the documentation
==========================

.. code:: python

    python setup.py build_sphinx -Ea
