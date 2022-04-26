.. (C) British Crown Copyright 2017-2018, Met Office.
.. Please see LICENSE.rst for license details.

Requirements
============

CDDS convert is designed around the use of a Rose suite to control processes
on a batch cluster. As such it has been developed to work with the following
tools;

* cylc version 7.4.0
* Rose version 2017.05.0

This code has also been built to use the Scientific Software Stack provided
by the AVD team within the Met Office. To date no testing as been performed
elsewhere.

Installing CDDS Convert
========================

CDDS Convert can be installed using the following command::

  python setup.py install 

Testing the installation
========================

Run only the unit tests::
   
  python setup.py nosetests

Run only the unit tests and doctests::

  python setup.py nosetests --with-doctest

Run only the integration tests::

  python setup.py nosetests -a integration

Run only the doctests::
 
  python setup.py nosetests -e ^test --with-doctest

Building the documentation
==========================

.. code:: python

   python setup.py build_sphinx -Ea
