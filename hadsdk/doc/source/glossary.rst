.. (C) British Crown Copyright 2015-2018, Met Office.
.. Please see LICENSE.rst for license details.

********
Glossary
********

.. include:: common.txt
.. glossary::

   CDDS
     Climate Data Dissemination System.
     
   CF convention
     `netCDF Climate and Forecast (CF) Metadata Convention`_.

   CMOR
     `Climate Model Output Rewriter`_.

   Concatenation Task
     A task to join together the output from individual processing tasks. To
     manage compute resources, processing is divided into small date ranges,
     producing one output file per date range. Concatenation Tasks are then
     run to join the files into a single file for a larger date range of
     length |Concatenation Period|. Concatenation tasks are executed once
     per |Concatenation Cycle|.

   Concatenation Cycle
     A concatenation cycle is a date range for which all data for that
     period is processed by one |Concatenation Task|.

   Concatenation Period
     The length of the date range to be processed by 1 |Concatenation Task|.

   Controlled Vocabulary
     A pre-defined set of terms describing acceptable values for various
     quantities. For CMIP6, see the `CMIP6 Controlled Vocabulary`_.

   CREM
     `Climate Research Experiment Management`_.

   Data request
     Information describing which |MIP requested variables| need to be produced
     for a given |MIP|-|experiment| combination. For CMIP6, see the
     `CMIP6 Data Request`_.

   Dataset
     A group of data containing some or all of the |model output files| from a
     single model simulation (i.e., |model output files| from a single
     realization of a single experiment from a single model).

   Experiment
     A defined set of forcing inputs, and duration, for a model run.

   Experiment identifier
     A short name identifying an experiment, e.g. ``piControl``. For CMIP6, see
     the `CMIP6 Global Attributes document`_ and the
     `CMIP6 Controlled Vocabulary`_.

   Input variable
     A |multi-dimensional data object| that contains data selected from the
     |model output files| as determined from the information provided by the
     |model to MIP mapping|.   

   Iris
     `A Python library for Meteorology and Climatology`_.

   Mapping identifier
     A text code that is used, along with the |UM version|, to obtain the
     |model to MIP mapping| from the old mapping table. A |mapping identifier|
     has the form ``A (B, C)``, where ``A`` is the name of the |MIP| for which
     the |model to MIP mapping| was first used, ``B`` is the
     |MIP table identifier| and ``C`` is the
     |MIP requested variable name|. The |mapping identifier| was specified in
     the old request configuration files, but if it was not present, it was
     inferred from the |MIP table identifier| and the
     |MIP requested variable name|.

   MIP
     Model Intercomparison Project, e.g. ``ScenarioMIP``. For CMIP6, see
     ``activity_id`` in the `CMIP6 Global Attributes document`_ and the
     `CMIP6 Controlled Vocabulary`_.

   MIP era
     The associated CMIP cycle, e.g. `CMIP5`_, CMIP6. For CMIP6, see the
     `CMIP6 Global Attributes document`_ and the
     `CMIP6 Controlled Vocabulary`_.

   MIP output variable
     The final |multi-dimensional data object| that is written to an
     |output netCDF file| and corresponds to the |MIP requested variable|. 

   MIP requested diagnostic
     The physical, generally observable concept that a user ultimately wants
     data for. However, it may not be possible to provide the data for the
     |MIP requested diagnostic|, since the data in the |model output files| may
     not be able to represent the physical concept.

   MIP requested variable
     The physical, generally observable concept for a given time sampling and
     level sampling (where applicable) that is fully identified by both the
     |MIP requested variable name| and the |MIP table identifier|.

   MIP requested variable name
     The short name of a physical, generally observable concept, e.g. ``tas``.

   MIP table
   MIP-specific table of information
     A text file that contains |MIP|-specific metadata (in practice, the
     metadata is often shared between |MIPs|) constrained by the
     |CF convention| that describe the |MIP requested variable| for that |MIP|;
     much of the metadata written to the |output netCDF files| by |CMOR| is
     defined in the |MIP tables| and ensures compliance with the |MIP|
     specifications. The files have a name in the form
     ``<MIP>_<MIP_table_identifier>``, e.g. ``CMIP5_Amon``. For more
     information about |MIP tables|, please see the `CMOR MIP tables`_ web
     page.

   MIP table identifier
     A text code (e.g. ``Amon``) identifying a |MIP table|. The
     |MIP table identifier| roughly corresponds to a |stream|.

   Model
   Model configuration
     A recognised configuration of a climate model that is used for a wide
     variety of |experiments| / |simulations|.

   Model configuration information
     Information describing which |MIP requested variables| a |model| has the
     capability to produce.

   Model identifier
     A short name identifying a model, e.g. ``HadGEM3-GC31-LL``. For CMIP6, see
     ``source_id`` in the `CMIP6 Global Attributes document`_ and the
     `CMIP6 Controlled Vocabulary`_.
   
   Model output files
     Output files produced from a modelling system, e.g. NEMO, CICE, etc. that
     conform to a naming convention.

   Model to MIP mapping
     Information providing details specifying which data are to be read from
     the |model output files| to create the |input variables| (e.g. for PP
     files, the name of the PP field header element) and how to process the
     |input variables| to produce a |MIP output variable|. Some
     |MIP output variables| are based on an arithmetic combination of two or
     more |input variables|. Various complexities of |model to MIP mapping|
     exist. The |model to MIP mappings| are stored in the
     |model to MIP mapping configuration files|.

   Model to MIP mapping configuration files
     A text file that can be read by the Python `configparser`_ containing one
     or more |MIP requested variable names| organised in sections; each
     section provides information about the |model to MIP mapping|. The files
     have a name that ends in ``_mappings.cfg``. For more information on the
     structure of the |model to MIP mapping configuration files|, please see
     `Model to MIP Mapping Configuration Files`_

     The |model to MIP mapping configuration files| have superseded the old
     mapping table and the old request configuration files. The old mapping
     table was a text file (typically called ``stash_mappings.txt``)
     containing the information in the "STASH-MIP Mappings" database in |CREM|
     that enabled access to the specific details of the processing used in the
     |model to MIP mapping| given the |mapping identifier| and |UM version|.
     The old mapping table originated from wiki markup. The old request
     configuration files had a name in the form ``<stream_id>_variables``
     (i.e., there was one old request configuration file per |stream|).

   Model type
     A text code (e.g.  ``AOGCM``, ``AGCM``) identifying which model components
     are used in a given |experiment| / |simulation|. For CMIP6, see
     ``source_type`` in the `CMIP6 Global Attributes document`_ and the
     `CMIP6 Controlled Vocabulary`_.

   Multi-dimensional data object
     A Python object representing the geophysical field and contains a
     multi-dimensional NumPy array and corresponding metadata (e.g. coordinate
     information, spatio-temporal metadata). A |multi-dimensional data object|
     is the generic term that is used to describe an |Iris| ``cube`` or the
     ``Variable`` object in the ``mip_convert`` code.

   netCDF
     `network Common Data Form`_. The "CDF" part was capitalized in part to pay
     homage to the NASA "CDF" data model which the |netCDF| data model
     extended (see `netCDF best practices`_).

   Output netCDF file
     A |netCDF| file produced by |CMOR| that is compliant with the |MIP|
     specifications and contains a single |MIP output variable| (along with
     coordinate/grid information, attributes and other metadata) from a single
     model and a single simulation (i.e., from a single ensemble member of a
     single climate experiment). Typically, there is one |output netCDF file|
     for each |MIP requested variable|.

   Package
     An identifier indicating the phase of |CDDS| processing.
     
   Request
     Information about a |simulation| used by all |CDDS| components. For more
     information, please see `Request`_.
   
   Request identifier
     A unique name to identify a |request|. A |request identifier| has the form
     ``<model_id>_<experiment_id>_<variant_label>``, where ``<model_id>`` is
     the |model identifier|, ``<experiment_id`` is the |experiment identifier|
     and ``<variant_label>`` is the |variant label|.

   Requested variables list
     A JSON file that describes which |MIP requested variables| can and will be
     produced for a given |MIP|-|experiment| combination from a specific
     version of the |data request|. For more information on the structure of
     the |requested variables list|, please see the `Requested variables list`_
     section in the `CDDS Prepare User Guide`_.

   Run identifier
     See |suite identifier|.

   Simulation
     A particular model run, with associated |suite identifier|, which is
     defined by an |experiment| and has an assigned |variant label|.
     
   STASH
     Spatial and Temporal Averaging and Storage Handling.

   STASH code
     A numerical code that represents a physical concept and is used to
     identify the data required for an |input variable|. A |STASH code| has the
     form ``m<MM>s<SS>i<III>``,  where ``<MM>`` is the model number, ``<SS>``
     is the section number and ``<III>`` is the item number.

   Stream
     A group of data from a modelling system typically organised by time (e.g.
     daily, monthly, etc.).

   Stream identifier
     The name of a |stream| in the form ``[a|o][d|p][a-z]``, where ``[a|o]``
     describes the aspect of the modelling system used to create the data in
     the |stream| i.e., ``a`` = atmosphere, ``o`` = ocean, ``[d|p]`` describes
     the status of the data i.e., ``d`` = dump and ``p`` = post processing, and
     ``a-z`` describes the grouping, e.g. ``m`` = monthly, ``s`` = seasonal,
     ``y`` = yearly.

   Suite identifier
     A text code (e.g. ``u-ar766``) that identifies a model run.

   UM version
     The version of the UM. The |UM version| can contain up to three
     components, i.e., ``<major>.<minor>.<micro>``, where ``<major>``,
     ``<minor>`` and ``<micro>`` are integers.

   User configuration file
     A text file that can be read by the Python `configparser`_, which is
     generated by CDDS Configure and used by MIP Convert. For more information
     on the structure of the |user configuration file|, please see the
     `User Configuration File`_ section in the `MIP Convert User Guide`_.

   Variant label
     A text code (e.g. ``r1i1p1f1``) that uniquely identifies a |simulation|.
     For CMIP6, see the `CMIP6 Global Attributes document`_.
