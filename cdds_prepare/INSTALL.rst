.. (C) British Crown Copyright 2017-2019, Met Office.
.. Please see LICENSE.rst for license details.

.. include:: common.txt

Requirements
============

Software:

* Python 2.7
* Rose 2018.02.0
* `Data request`_ `01.00.28`

  * Additional versions of the |data request| (as specified in the CDDS
    Configuration files) should also be downloaded.

* hadsdk 2.0.3
* mip_convert 2.0.3
* Setuptools 26.1.1

Documentation:

* Sphinx 1.4.8
* docutils 0.12

Testing:

* nose 1.3.0
* mock 1.0.1

Installing CDDS Prepare
=======================

CDDS Prepare can be installed using the following command::

  python setup.py install 

Testing the installation
========================

Run only the unit tests::
   
  python setup.py nosetests

Run only the unit tests and doctests::

  python setup.py nosetests --with-doctest

Run only the functional tests::

  python setup.py nosetests -a slow

Run only the doctests::
 
  python setup.py nosetests -e ^test --with-doctest

Building the documentation
==========================

.. code:: python

   python setup.py build_sphinx -Ea
