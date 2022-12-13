.. (C) British Crown Copyright 2015-2016, Met Office.
.. Please see LICENSE.rst for license details.

:orphan:

.. _batch_cmor_user_guide:

**********
User Guide
**********

.. include:: common.txt
.. contents:: Table of Contents
   :depth: 2

Outline
=======

This document is a draft user guide for the CMIP5 pp to |netCDF|
conversion processor. As a draft it is lacking in many ways - it grew
out of a set of notes on the BADC-MO developed code used in ENSEMBLES,
and is gradually morphing into a user guide.

Software Description
====================

The converter takes a set of UM output files (as pp files) and
produces |netCDF| files using the |CMOR| software package.

The production of multi-dimensional |netCDF| files from pp fields
requires the identification of which pp fields belong to a given
multi-dimensional variable.  The converter handles this by allowing
the user to specify a set of search criteria that are used to match
which pp-headers are used in a multi-dimensional |netCDF| variable.
The converter reads the search specifications from a set of variable
request files.  The content of these files is described later in this document.

In some cases the required MIP variables are not present in the UM
STASH output.  A set of mappings can be given that relate the MIP
variables to STASH output.  The converter can handle mappings of two
kinds:

  1. mappings that involve arithmetic combinations of STASH output, or
     STASH output with scalars.  These mappings are handled by the
     converter itself.

  2. complex mappings provided by third party IDL scripts.
     In this case the converter simply calls out to the
     third party script and reads the output file it produces (which
     must be a pp file).

Not all meta-data needed by |CMOR| is present in a pp file.  The
converter will read the extra meta-data from a configuration file.
The converter does not impose any policies or conventions on this
meta-data: it does not manage the dependencies between some meta-data
elements like ``model_id`` and ``source``.  It is left to the producer
of the configuration file to do this.  `CMIP5 metadata requirements`_ are
available.

Currently each run of the converter will work against only one |CMOR|
dataset (roughly a model experiment).  If you want to run against more
than one |CMOR| dataset then put the calls to the converter in a loop.


Installation
============

For installation instructions and dependencies see the INSTALL.TXT
file in the distribution.  This includes instructions on suggested
software layout, and the configuration files which remain unchanged
between runs of ``batch_cmor.py``.  (See section 6 of the install guide.)  It
also gives information on the logging of the packages used by
``batch_cmor.py``.

TODO: figure out the best place to talk about logging.

Running the converter
=====================

Prerequisites
-------------

In most cases the converter assumes that the input files are in a
directory structure based around ``runid/stream/filename.pp``.  For
instance::

  ../ajhoh/apa/ajhoha.pak5jun.pp
               ajhoha.pak5mar.pp
               ajhoha.pak5may.pp
               ajhoha.pak5nov.pp
               ajhoha.pak5oct.pp
               ajhoha.pak5sep.pp
                    :
  ../ajhoh/apm/ajhoha.pmk5jun.pp
               ajhoha.pmk5mar.pp
               ajhoha.pmk5may.pp
               ajhoha.pmk5nov.pp
               ajhoha.pmk5oct.pp
               ajhoha.pmk5sep.pp
                    :

The file names should conform to the `Naming of Output Files in the UM`_. The
names are currently used in determining what times are present in the files.
Version 7.9 of the UM introduced what are sometimes called new file naming
conventions. These use full years as numbers rather than using the letter
encoded years.  The conversion code assumes all model version after and
including 8.0 use this new convention.  (This does not quite work for 7.9 as
the file naming convention was optional at that version.  If this is a problem
let us know and we can try to find time fix the code.)

The exception to this file naming convention is in TAMIP experiments
 - see Appendix on TAMIP naming conventions.

For both standard UM naming convention and TAMIP conventions the
converter also supports the idea of an ancillary stream.  This stream
can hold pp versions of any ancillary files used as part of the model
run. The support for ancillary streams is limited (see release
notes).  If you encounter problems let us know.  The ancillary stream
is treated differently to other streams, this is covered in the
documentation on the ``cmor_project`` file.

The converter runs by converting every file in a stream before moving
onto the next stream.

The files should be pp files including FORTRAN record markers that
give the length of the record in bytes.  All testing has been done
with unpacked  32-bit big endian pp files. 

Time series data
----------------

The conversion of timeseries data is a bit fragile and is largely hard
coded to HadGEM2-ES and the CFMIP project run as part of CMIP5.  If
you want to processes time series data for any other model or project
please contact us.  The 'fragility' is associated with a number of
factors, including:

  1. hard coded vertical hybrid height level values as the pp header
  for timeseries does not include the values (as far as we could see).

  2. hard coded association of section 1, 2 radiation diagnostics with
  the capability to support the idea of radiation half levels. (This
  actually applies, but maybe less rigidly) to non-time series fields.

  3. (close to) hard coded association of the timeseries/station locations and
  orography with the HadGEM2-ES grid, and the CFMIP requirements.


Running the converter
---------------------

Steps involved:

 1. choose a directory to hold the configuration for this run of the
    converter.

 2. copy the default configuration files to a chosen directory
    (``<configdir>``).  A set of default configuration files will be
    distributed with the converter in the directory ``etc``.

 3. edit the configuration files reflect the project and conversion
    you want to do.  Roughly you will need to edit the
    ``cmor_project`` file to amend any |CMOR| set up, data location and
    data set meta-data information, and the ``<stream>_variable``
    files to say which MIP variables you are trying to produce as part
    of this run of the converter.

 4. run using ``$ batch_cmor.py <configdir>`` or
    ``$ multi_batch_cmor.py -b <run_bounds_file> <configdir>``. See the
    next subsection for hints on use of the latter script.

 5. check your output, the logs etc. and re-jig the configuration or
    report a bug.

Use of the multi_batch_cmor.py script
-------------------------------------

The ``batch_cmor.py`` script can only generate |netCDF| output files for
a single uninterrupted time period, as specified by the ``run_bounds``
property in the ``cmor_project`` file. The ``multi_batch_cmor.py`` script
is a basic wrapper around the ``batch_cmor.py`` script which enables
multiple discontinuous time periods to be processed. This is useful, for
instance, for handling CMIP5 experiments which require output for individual
years or decades.

The ``multi_batch_cmor.py`` script requires a template project config file
plus a text file containing the desired run bounds. By convention these files
are called ``cmor_project_`` and ``run_bounds``, respectively. They usually
reside in the ``<configdir>`` directory, alongside other configuration files.

The format of the run bounds definitions in the ``run_bounds`` file is exactly
the same as for the ``run_bounds`` property in a regular ``cmor_project`` file.
Hence, an example ``run_bounds`` file might look thus::

  1959-12-01-00-00-00 1960-12-01-00-00-00
  1969-12-01-00-00-00 1970-12-01-00-00-00
  1979-12-01-00-00-00 1980-12-01-00-00-00

which would generate output for the 3 model years 1960, 1970 & 1980. It's
possible to specify the run bounds via stdin, but normal practice is to record
them in a text file, as above.

The ``cmor_project_`` template file is identical to the regular
``cmor_project`` file. The latter is simply generated from the former by 
overwriting the ``run_bounds`` property in turn with each time period specified
in the aforementioned run_bounds file. Thus, you don't need to create a
separate ``cmor_project`` file - if one does exist it will simply get
overwritten at the first pass. 

So, assuming that you have used the default names for the aforementioned
configuration files, then you can invoke the ``multi_batch_cmor.py`` script
as follows::

  $ multi_batch_cmor.py -b etc/run_bounds etc

For further usage information invoke the script with just the ``--help``
option. 

Note
----

Much of the testing and running of the converter so far has been done
be a few users in a fairly limited environment.  You are likely to
find errors.  In the first instance e-mail any errors to
``jamie.kettleborough@metoffice.gov.uk``.

Errors and Exceptions
=====================

The converter has been developed mainly for use by technical users,
and there is an underlying assumption that these users do not mind
seeing exceptions and stack traces.  Much of the error handling is via
exceptions that are not caught.  These exceptions will result in a
non-zero return code of the ``batch_cmor.py`` command.

The  converter, on  the whole,  also follows a fail-early
(fail  often)  philosophy and  makes  few  attempts to recover from
errors.  A motivation for this is that making the  failures explicit
hopefully gives information on the root cause of the failure, rather
than hiding it behind an error recovery mechanism.

In some cases the fail-early, fail often philosophy does not carry
over particularly well into a more 'production' environment and it can
cause frustration and slower processing.  If the converter has a
problem reading or writing a single variable from a file it will turn
off the processing of that variable for this run of the converter.  In
this case, although the converter will complete without an exception
it will print messages to stdout, send messages to a logger, and
return a non-zero error code to the shell.  The non-zero error code
reflects the fact that not all the variables for all the times asked
for were converted. 

In addition to the error handling in the converter code there is
underlying error handling in |CMOR|.  The behaviour of |CMOR| on errors
can be configured through the ``cmor_project`` file.  There are
occasions when the |CMOR| messages can be confusing: if the converter
has to turn off the processing of a variable (after a failed read or
write) |CMOR| does not see this and so prints encouraging messages to
stdout or the |CMOR| log files.  You should scan the entire log and
stdout, not just the |CMOR| log to understand the full behaviour of the
converter.

Logging
-------

The converter uses the Python :mod:`logging` module with a naming convention
applied to the loggers.  The logger names are given by the
package.classname of the class being logged (with some exceptions -
though these are being squeezed out).

There are two contexts in which loggers are used.  The first is to
help programmer debugging, the second is to send messages to or record
information for the person doing the conversion.  There are two
loggers of particular importance for the person doing the conversion:

convert.context.CommandLine
  this logger records variables that have been turned off during
  processing.  The messages should include the exception that caused
  the variable processing to be turned off.
 
convert.request.request_variable.PpRequestVariable
  this logger records where variable values that have gone out of
  bounds and have been reset.

Configuration Files
===================

The ``batch_cmor.py`` script uses a number of configuration files.
Almost all of these files are of the 'ini' file type, as described by
in the Python :mod:`ConfigParser` documentation.

The exception is the stash_mappings.txt table which
originated from wiki markup.


cmor_project file
-----------------

Each run of the ``batch_cmor.py`` script uses a ``cmor_project``
configuration file.  This defines.

1. the um data source characteristics
2. other configuration options such as |CMOR| MIP table location.


Sections
~~~~~~~~

The ``cmor_project`` file contains three sections: ``general``
for specification of things like the |CMOR| setup, ``data_source``
sections for specification of the input UM runids, and the extra CMIP5
experiment meta-data, and ``global_attributes`` which is an optional
section specifying any non-|CMOR| global attributes you want in all output
files. 

general section
~~~~~~~~~~~~~~~

mappings
  the full path to the stash to MIP variable (usually has a filename
  of ``stash_mappings.txt``) mapping file.

inpath
  path to where the MIP tables reside (used to initialise |CMOR|, and
  the map between the internal data model and the MIP tables)

netcdf_file_action
  optional - see |CMOR| setup documentation

set_verbosity
  optional - see |CMOR| setup documentation (tested with default)

exit_control
  optional - see |CMOR| setup documentation (tested with default)

logfile
  optional - see |CMOR| setup documentation (tested with default)

create_subdirectories
  optional - see |CMOR| setup documentation

outdir
  output directory to use for the |netCDF| files.

orography_path
  name of file containing the orography.  This is used in the
  definition of the meta-data for the hybrid_height coordinate.  This
  file should contain the orography on all the grids needed by the
  variables in the request.  We have orography for HadGEM2.

base_date
  this date must be supplied and is used as the base date in the time
  coordinate output time.  The format is ``yyyy-mm-dd-hh-mm-ss`` (just as
  for run_bounds).


For ``netcdf_file_action``, ``set_verbosity``, ``exit_control`` use
the constant names given in the |CMOR| documentation,
e.g. ``CMOR_PRESERVE_3`` to turn on |netCDF| output.  You should have a
copy of the |CMOR| documentation in the |CMOR| distribution. 

*Note* you only need to provide a valid ``orography_path`` if the you have
a model with hybrid height coordinates and you are converting model
level diagnostics.  In other cases you need to provide and
``orography_path``, but it need not be for the model grid you are
using (the file gets read, but never used - this may change at later
versions of the code).

data_source section
~~~~~~~~~~~~~~~~~~~
  
sourcedir
  base dir for the location of the data.  ``batch_cmor.py`` will look for
  files in ``sourcedir/runid/stream/filename``, where filename is
  given by the UM naming conventions.

ancil 
  space separated list of the path names of the ancillary files.
  (in practice these should all be in the same directory).  I expect
  the form of this will be temporary.  Important if running IDL based
  processors: see the section on environment variables.

runs
  space separated list of um runids making up this experiment/data
  set

versions
  space separated list, one entry for every runid.  Gives the relevant
  um version for the corresponding runid in the runs list.  It is used
  to determine which mapping to use (as this can be um version
  dependent).
  Although a
  version can contain major, minor, and micro separated by ``.`` only
  the major version is used in determining which mappings to use.

run_bounds
   space separated list of times in the format ``yyyy-mm-dd-hh-mm-ss``.
   There should be one more run_bound that there is runs. The
   converter runs from the first run_bound in the list to the last
   run_bound in the list.  The converter 
   will look for files from the runid whose run_bounds contains the
   time currently being converted.

streams
  space separated list that defines the streams present for this
  model experiment.  Each stream appearing in streams should have a
  stream configuration file associated with it.  The order of the streams
  determines the order in which the data is processed.  If you are
  including an ancillary stream then you must give it the name ``ancil``.

stream_reinitialisation_in_hours
  space separated list giving the
  reinitialised period of each stream (how many hours are in each file
  in the stream).  Ignored for climate mean streams, but must still be
  present (suggest enter as 0, though it is not used).  There should
  be one entry per stream in the streams option

atm_timestep_in_seconds
  the atmosphere model timestep (in seconds) for this run.  This is needed
  for atmospheric tendency diagnostics which use mappings depending on
  the model timestep.  You will need to set this even if you are not
  producing tendency diagnostics (though it could be set to 0. in this
  case).

file_suffix
  the suffix or extension for input pp files.  This defaults to
  ``.pp``.  This can be used when the pp files have been run though one
  of the precis tools to say remove the rim (e.g. ``.rr8.pp``).  The
  ``file_suffix`` should include any ``.``.

cfmip_nsites
  For CFMIP site-based time-series datasets, optionally specifies the
  number of sites represented in each PP field.  If this property is
  specified then it is used to cross-check that the number of sites
  read in from each input PP field is correct.  The number of sites
  for standard CFMIP experiments is 119, while the number for
  aquaplanet experiments is 73 (these are the latest known values, and
  may be subject to change).

cfmip_min_site_id
  For CFMIP site-based time-series datasets, optionally specifies the
  minimum (or starting) site ID. Other sites in the sequence are then
  numbered sequentially from this value. The default value is 1. For
  aquaplanet experiments the site IDs are numbered from 1000001 so the
  ``cfmip_min_site_id`` property should be set to that value when
  processing such experiments. This parameter and the ``cfmip_site_ids``
  parameter (see next entry) are mutually exclusive.

cfmip_site_ids
  For CFMIP site-based time-series datasets, optionally specifies the
  integer identifiers for the sites encoded in such datasets. The value
  of this parameter must evaluate to a Python sequence, i.e. when parsed
  by the eval() function. Typical examples might be ``range(1000002,1000073)``
  or, more verbosely, ``[1000002, 1000003, ..., 1000072]`` to specify a subset
  of aquaplanet site IDs. This parameter and the ``cfmip_min_site_id``
  parameter (see previous entry) are mutually exclusive.

cfmip_coord_file_url
  For CFMIP site-based time-series datasets, optionally specifies the
  URL of the text file containing latitude, longitude and height coordinates
  for each CFMIP site. The file format is CSV, with each line containing
  the values Site ID, Longitude, Latitude, Height, Site Name. At MOHC the
  default file location is ``/project/cdds/etc/cfmip2/cfmip2-sites-orog.txt``

The following attributes are all used by |CMOR|, for use see the |CMOR|
and meta data requirements documentation for CMIP5.

   * institution (C)
   * institute_id (C)
   * experiment_id (C)
   * forcing (C)
   * calendar (C)
   * source (C)
   * model_id  (C) 
   * contact		
   * references
   * realization
   * physics_version
   * initialization_method 
   * parent_experiment_id
   * parent_experiment_rip
   * comment

Those marked with a C are compulsory for the converter, others are
optional for the converter, but may be imposed by the MIP.  (Note this
is in part historical I realise this is a bit frustrating - having
things specified as optional in more than one place - I'll try and
tidy this up.)  Note we have reserved the history attribute for
application use.  We also advise that comment should be used to record
any perturbed physics details.

The calendar can take the value ``360_day`` or ``proleptic_gregorian``,
although at this version of the software support for
``proleptic_gregorian`` is limited to short TAMIP experiments.  An error
will be thrown if the calendar does not match that indicated by lbtim
in the pp headers.

The ``experiment_id`` is used to determine the naming conventions used
for the source pp files.  If the ``experiment_id`` starts with ``tamip``
then the TAMIP naming conventions will be used, while all other
``experiment_id`` will use the source naming conventions outlined in
the prerequisites section.

The |CMOR| dataset attribute ``branch_time`` is dealt with in a slightly
different way to the other |CMOR| attributes.  This is calculate from
the ``datasource`` section items:

parent_base_date
   the base date of the ``parent_experiment_id``.

branch_date
   the date in the ``parent_experiment_id`` from which the experiment
   branches.  The |CMOR| dataset ``branch_time`` is calculated by
   taking the difference (in days) between the ``branch_date`` and the
   ``parent_base_date``.  If branch_date is ``N/A`` then ``parent_base_date``
   is ignored and the |CMOR| dataset ``branch_time`` will be set to 0. 

global_attributes section
~~~~~~~~~~~~~~~~~~~~~~~~~

The ``global_attributes`` section provides a place to add in any
information that you would like to become |netCDF| global attributes.
There is one special option in this section called ``preserve_case``.
All other options in this section simply get interpreted as attribute
names and their values the attribute values. All values are currently
string values.  (Note: any options provided in the ``DEFAULT`` section
will not become |netCDF| global attributes).

preserve_case
  this is a space separated list of option/|netCDF| global attribute
  names.  Any name appearing in this list and as another option in
  this section will appear in the |netCDF| file with the case of letters
  as they appear in preserve_case.  

  This is a bit of a funny option as it is mainly there to overcome
  the fact that the Python ini file parser converts all options to
  lower case by default.  Although this can be changed, it cannot - as
  far as I can tell - be changed on a section by section basis, which
  is what we wanted to avoid breaking old ``cmor_project`` files.

Examples of the ``global_attributes`` section::

 [global_attributes]
 preserve_case: CORDEX_domain
 CORDEX_domain: AFR-44

Would result in a |netCDF| file with a global attribute::

  	:CORDEX_domain = "AFR-44" ;


Note there is no cross checking between global attributes reserved (even if
optional) by |CMOR| and attributes given in the ``global_attributes`` section.
The advice is to use the |CMOR| reserved attribute where ever possible.

There is also no checking to ensure that all the items in the
``preserve_case`` list are used.  This means you'll need to check the
spelling of these items.

stream file
-----------

Each pp stream has a request variables configuration file that
contains the variables required from this stream.  Each variable has a
section in the configuration file. The name of the section determines
the MIP variable that the request applies to *e.g.* a MIP variable
``tas`` is requested in the section ``[tas]``.  To support cases where
MIP variables from different MIP tables are provided by the same UM
stream the variable name in the section can be appended with an ``_``
followed by an integer, *e.g.* ``[tas_1]``.

Each variable request section provides information on the selection
criteria for that variable (level, time processing etc).  Some of
these values are common to all variables and so are given in the
DEFAULT section.

The stream files are based around pp streams as produced by the UM,
not MIP tables.  There is some implied knowledge in the formation of
the stream files - for instance that ``apm`` contains monthly means,
whereas ``apa``, ``ape`` tend to contain sub monthly fields.

Note: some of the information in the stream file is closely associated
with the mappings of STASH to MIP variables (lbproc for tasmax/tasmin,
blev sampling for some soil variables etc).  The conversion software
takes a simplistic view of the complexity of the relationships between
MIP variables with pp header elements.  For diagnostic that are
derived from either one to one mappings with STASH or arithmetic
relationships between STASH codes uses the following simple
philosophy:

   1. The stash_mapping.txt table is used to say what STASH codes
   (lbuser4, lbuser7) are needed for a MIP variable.

   2. The stream files deal with selection of pp fields based on lbtim,
   lbproc, and blev.  

For some MIP variables there may be informational guidance in the
stash_mapping.txt to help the user decide which blev or lbproc to
choose.

For more complex mappings that require IDL code this simple model can
break down.  The IDL code itself takes on the responsibility of
selecting stash codes and on lbtim etc.  Any values given in the
stream files are ignored.

Variable request section
~~~~~~~~~~~~~~~~~~~~~~~~

Depending on the set up of stash in the UM to get a particular
quantity you may need to sub select the stash codes depending on other
pp header elements.  The variable section allows optional selection on
other header elements.

mip_table
  the MIP table id for this request

mapping_id specifies the STASH to MIP variable mapping to be used for
  this variable.  It is optional - if not present it is inferred from
  the mip_table and section name. This should refer to an entry in the
  ``published`` column in the stash_mappings.txt file.  (Not ideal and
  may change in future - the decision to use this is based on the fact
  it was good enough to get something working.)

lbtim
  select the pp headers that match lbtim

lbproc
  select the pp headers that match lbproc 

lbuser5
  select the pp headers that match this pseudo level (note in the
  config file it really is lbuser5 at the moment - an 'alias' to
  pseudo level would be clearer, and may get implemented in time).

blev
  select the pp headers that match blev.  blev can be a space
  separated list.  In this case headers which match any of the levels
  in the list will be selected.  Note the values used for blev may not be
  the raw blev values in the pp files.  The UM does not always write
  the appropriate level codes and values for some diagnostics.  The
  conversion code overwrites the UM values with usable values, and
  these are the values seen by the selection code.  The values are
  found in the module convert.input.pp_fixed. (This was the
  easiest thing at implementation time - it can be modified if it's
  causing problem).

blev_tol
  the tolerance to use when comparing a pp fields blev value with the
  blev required (as specified in the entry above). Default value is 1.e-6.

delta_time_in_days
  select headers with this delta_time_in_days between
  the first 6 and second 6 header elements.  Can be used to
  distinguish between daily and ten day means in the same files.  (Can
  be a float value for sub-daily selection.  There is no 'tolerance'
  applied in the compare though as the initial implementation was to
  pick out 3 hourly means from 6 hourly means and 3 hourly is 1/8 of a
  day - an exact binary fraction.

first_only
  *this is a fudge* to get us going with a certain HadCM3 stash set
  up.  It is different to the other selection options in it is applied
  last to headers already selected by other criteria (lbtim etc).
  Given a list of preselected headers it selects only the first field
  from the list.  This is a simple proxy for 'remove duplicate
  fields' and works only for single level fields.

outputs_per_file (optional). 
  The number of output times in each file. This option is ignored if
  the MIP tables are CORDEX or NILE2.  These use their own scheme for
  determining the number of outputs in each file (see the CORDEX_
  documentation).
  outputs_per_file can be used to prevent output |netCDF| files from becoming
  too large.  Omitting this option will result in one output |netCDF| file
  per MIP variable.  If using this option you should note the
  following.  First the units of this variable are simply the number
  of outputs per file, and are not real time units.  For instance if
  you want a years worth of monthly means set this to 12, but for a
  years worth of daily means set to 360.  Second this option has been
  implemented to keep files to manageable file sizes.  For ease of
  implementation it assumes that each pp file in the sequence contains
  fewer output times than the number of outputs required in the output
  |netCDF|, and that the number of output times is a whole number of the
  number of outputs in the pp file.  The code will throw an exception
  if this is not true.  For instance if you have a UM stream
  containing daily output with a reinitialisation of 30 days then you
  should use outputs_per_file as a whole number multiple of 30 days.
  Third there is no special handling if you use |CMOR| in append mode (I
  never use this).  Finally the implementation does nothing in the
  case of your run length not being a whole number multiple of the the
  outputs_per_file.  If it is not you will end up with a final file
  that has a different number of outputs in it to the rest of the
  series. For instance if you run for a year and a half, with daily
  outputs and `outputs_per_file` set to 360 you will end up with the
  first file with 360 days, and the second with 180 days.  You will be
  able to see this from the |CMOR| file names.

.. _CORDEX: http://cordex.dmi.dk/joomla/images/CORDEX/cordex_archive_specifications.pdf

valid_min (optional)
  Defines the minimum valid value that an output variable can take.
  This property is used if either or both of the tol_min_action or
  oob_action properties are defined (see below).

valid_max (optional)
  Defines the maximum valid value that an output variable can take.
  This property is used if either or both of the tol_max_action or
  oob_action properties are defined.

tol_min (optional)
  Defines the minimum tolerance value for an output variable. This
  property is required if the tol_min_action property is defined.

tol_max (optional)
  Defines the maximum tolerance value for an output variable. This
  property is required if the tol_max_action property is defined.

tol_min_action (optional)
  Specifies the action to take if a data value lies between tol_min
  and valid_min.  Permissible values, and their actions, are as follows:
  
  - PASS_VALUE : pass value on, i.e. do nothing
  - SET_TO_VALID_VALUE : sets the value to **valid_min**
  - SET_TO_FILL_VALUE : sets the value to the **fill value**
  - RAISE_EXCEPTION : raise an OutOfBoundsError exception

  For tol_min_action to have any effect, tol_min and valid_min must be
  defined. Also, *tol_min must be < valid_min*.

tol_max_action (optional)
  Specifies the action to take if a data value lies between valid_max
  and tol_max.  Permissible values, and their actions, are as described
  for the tol_min_action property, with the exception of:

  - SET_TO_VALID_VALUE : sets the value to **valid_max**
  
  For tol_max_action to have any effect, tol_max and valid_max must be
  defined. Also, *tol_max must be > valid_max*.

oob_action (optional)  
  Specifies the action to take if a data value is totally out of bounds, i.e.
  below valid_min or above valid_max (or tol_min and tol_max if those
  are specified).  Permissible values, and their actions, are as follows:

  - PASS_VALUE : pass value on, i.e. do nothing
  - SET_TO_FILL_VALUE : sets the value to the **fill value**
  - RAISE_EXCEPTION : raise an OutOfBoundsError exception


stash_mappings.txt
------------------

The form of the stash_mappings.txt file is in part
historical.  It is not optimal, and is very likely to change.  The form of the
table is a number of ``|`` delimited columns.   The columns are as
follows:

standard_name
  this should be a name in the CF standard_name table.  It
  is currently unused, and if there is a corresponding MIP table entry
  then the standard_name will be taken from the MIP table.

cell_methods
  this is the CF cell_methods that accompany a standard_name to give
  a particular MIP table entry.  (unused and will be taken from the
  MIP table)

units
  should be the units of the quantity produced by the
  mapping. (e.g. after any scaling).  Note: I don't think this has
  been applied consistently in  the tables we have - we'll ween these
  out as we discover issues.

positive
  direction of the variable if it is the vertical component of a
  flux.  This is the direction of the quantity produced by the
  mapping.  If a MIP variable has a positive attribute in the MIP
  table then the positive field must be present.

STASH mapping
  a expression representing how to calculate the MIP table entry
  variable from STASH variables.  STASH code should be given in the
  form ``mMMsSSiIII`` where ``MM`` is the model id, ``SS`` is the section
  number and ``III`` is the item number.  Simple algebra can be automatically
  processed by ``batch_cmor.py``.  In general the code will test to see
  that the space-time coordinates of any variables in operations are
  consistent.   For subtraction (ask if you need more) only this can
  be relaxed using a method call in the mapping expression.  For
  instance ``mMMsSSiIII.sub_no_check(mXXsYYiZZZ, ['Z'])`` will subtract
  ``mXXsYYiZZZ`` from ``mMMsSSiIII``, with no checking
  to see that they are on the same vertical level.   The suggestion is
  that although this relaxed subtraction is available you should use
  it only when you understand why you have to.
  If you have the UKMO IDL/TIDL libraries available to you then you
  can also call out to IDL.  Two methods are supported - either IDL
  returns a pp file (main use) or IDL can write global mean quantities
  to stdout as csv.  These are relatively specialist use so talk to
  us, or look at the source code to understand how to do this.

LBPROC
  the pp processing code used along side the stash code to determine
  which pp fields to use in the mapping (not used).  But include if
  necessary for future reference.

UM version
  half of a comparison expression that determines which um version
  this mapping is valid for.  e.g. ``< 5.0`` for old dynamics, ``>= 5.0`` for
  new dynamics models.  Leave blank if a mapping is valid for all
  versions of the model.

Published
  the published field is of the form: project (table,
  table_entry) where project is the MIP project that this variable has
  been used for, table is the MIP table id within that project and
  table_entry is the variable entry for the table.  This is used as
  the mapping identifier in the variable request configuration files.

Notes
  add a note on who added the mapping, why, whether there are cases
  you'd use this mapping over another.  You can also add any other
  special cases notes here.

Comments
  If the mapping needs a comment to appear in the output |netCDF| file
  then add it here.  You might need to add a comment to qualify the
  details of the diagnostic, add health warnings etc.

Some variable table_entries appear twice in the table.  This can have
several causes.  The first is simply history - the original wiki table
had the mapping entry for a number of different MIP tables (e.g. at
different meaning periods).  The second is that the preferred mapping
expression may be UM version dependent.  The third is that there may
be alternative mappings depending on the model parametrisation scheme
set up.  The fourth is that there may be alternatives depending on
the STASH diagnostic set up of the model run.  In the current version
of the code all versions of the mapping that are not needed are
commented out with a # at the beginning of the line.  I don't think
this is a long term solution, but it gets us going.  Long term I
think we should have different mapping_ids for each entry, and the
user explicitly chooses which mapping_id to use (but that's longer term.) 

Note on UM version post 5. and CMIP5 CMOR
-----------------------------------------

The MIP tables for CMIP5 add references to an ``areacella`` diagnostic in
the ``cell_measures`` attribute.  This is refers to the area of a grid
cell, and the relevant values of the area are stored in the file
``areacella`` from the ``fx`` table.  There is only one ``areacella`` which
means if the model produces diagnostics on a staggered grid then only
diagnostics on one of the the 'sub-grids' can have the ``areacella``.
The intent is that this should be the primary 'physics' grid - so the
grid that Temperature, radiation diagnostics etc are on.

In UM versions greater than 5. the some pressure level time mean
'physics' diagnostics are on a different grid to the other 'physics'
diagnostics.  This is associated with the way that the model STASH
system accounts for the fact that pressure levels can go underground.
The model does this by recording the Heaviside function at the
relevant time meaning period.

These time mean pressure level diagnostics would be assigned a
``cell_measures`` attribute that points (incorrectly - as they are on
a different grid) at the ``areacella`` file.  To avoid this the
converter makes |CMOR| calls to delete this reference.  The logic used
to determine whether the deletion should be done is a bit fragile - it
simply looks for the Heaviside stash code at the end of the mapping
expression.  This will fail if the mapping expression is in fact an
IDL call out.

Environment Variables
=====================

There is a small problem when using IDL derived diagnostics.
Occasionally an IDL diagnostic will need to get fields from the
ancillary files, not just the files associated with the model run.
An easy mechanism to support this is to have ``batch_cmor.py`` set some
environment variables that contain the name of the ancillary files.
The environment variables used are UMOROGPATH and UMLANDFRACPATH.
These should not be set by the calling process - but left to
``batch_cmor.py`` to infer them from the ``ancil`` option in the
``cmor_project`` file.

``batch_cmor.py`` relies on a simple naming convention to determine which
of the files in the ancil list is orography and which is land
fraction.  (It could be cleverer, but the naming convention was
easiest in the time available).  A path in the ancil list containing
``orog`` in its basename will be assigned to the UMOROGPATH environmental
variable.  A path in the ancil list containing ``mask_frac`` in its
basename will be assigned to the UMLANDFRACPATH.

Some history
============

The software grew out of that used for production of files
contributing to the ENSEMBLES project.

Appendix TAMIP file naming conventions
======================================

The file naming convention adopted for TAMIP is off the form
``sourcedir/[YYYYMMDDHHMM]__qwp[stream_letter].T[validity_time].pp``, 
where ``[YYYYMMDDHHMM]`` is the start date of the run, ``[stream_letter]`` is
``a`` for the ``apa`` stream , ``b`` for the ``apb`` stream etc. and the
``[validity_time]`` is the last time in the file.
