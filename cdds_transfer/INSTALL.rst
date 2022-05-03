.. (C) British Crown Copyright 2018, Met Office.
.. Please see LICENSE.rst for license details.

Installing CDDS Transfer
========================

CDDS Transfer can be installed using the following command::

  python setup.py install 

Testing the installation
========================

Run only the unit tests::
   
  python setup.py nosetests

Run only the unit tests and doctests::

  python setup.py nosetests --with-doctest

Run only the end-to-end tests::

  python setup.py nosetests -a slow

Run only the doctests::
 
  python setup.py nosetests -e ^test --with-doctest

Building the documentation
==========================

.. code:: python

   python setup.py build_sphinx -Ea
