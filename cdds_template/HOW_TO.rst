.. (C) British Crown Copyright 2018, Met Office.
.. Please see LICENSE.rst for license details.

How to use CDDS Template
========================

#. Rename ``cdds_template``, ``cdds_template/cdds_template`` and
   ``cdds_template/doc/source/cdds_template`` to the name of the new package.

#. Replace all instances of ``cdds_template``, ``CDDS Template`` and
   ``CDDSTemplate`` with the name of the new package.

#. Replace all instances of ``A. N. Other`` and ``a.n.other`` with the name of
   the author of the new package.

#. Replace ``[...]`` in ``cdds_template/README.rst``,
   ``cdds_template/cdds_template/__init__.py`` and ``cdds_template/setup.py``
   with the same short description of the new package.

#. Automatically check out ``versions.py``::

     svn propedit svn:externals cdds_template/cdds_template

   and add to the editor that pops up::

     ^/main/trunk/hadsdk/hadsdk/versions.py versions.py

#. Automatically check out ``doc/source/common.txt`` and
   ``doc/source/glossary.rst``::

     svn propedit svn:externals cdds_template/doc/source

   and add to the editor that pops up::

     ^/main/trunk/hadsdk/doc/source/common.txt common.txt
     ^/main/trunk/hadsdk/doc/source/glossary.rst glossary.rst

#. Ignore ``cdds_template/build`` and
   ``cdds_template/cdds_template.egg-info``::

     svn propedit svn:ignore cdds_template

   and add to the editor that pops up::

     build
     cdds_template.egg-info

#. Add the new package to ``run_all_tests`` and ``setup_env_for_devel``.
