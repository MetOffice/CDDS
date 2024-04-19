

## Model to MIP Mapping Configuration Files

The |model to MIP mapping configuration files| contains the following sections:

1. `DEFAULT <DEFAULT>`
2. `COMMON <COMMON>`
3. `<mip_requested_variable_name> <variable_name>`



### The ``DEFAULT`` Section


The `DEFAULT <DEFAULT>` section contains options that are propagated to
all other sections. This is useful for setting a default value for a option for
all sections. A value provided for the same option in any other section will be
used for that section over the default value defined in the
`DEFAULT <DEFAULT>` section. 



### The ``COMMON`` Section

The `COMMON <COMMON>` section contains options that may be used by other
sections by using the syntax ``${COMMON:<option>}``. This is useful for setting
values for comments or notes that would otherwise be repeated multiple times in
the |model to MIP mapping configuration files|.


### The ``<mip_requested_variable_name>`` Sections

The `<mip_requested_variable_name> <variable_name>` sections provide the
model to MIP mapping corresponding to the specified MIP requested variable
and contain the following required options:

|           Required Options           |                                   Description                                    | Notes |
|--------------------------------------|----------------------------------------------------------------------------------|-------|
| ``dimension``                        | The dimensions of the MIP requested variable.                                  |       |
| ``expression``                       | The expression required to convert the input variable / input variables to the MIP requested variable.      |       |
| ``mip_table_id``                     | A space-separated list of MIP table identifiers that the model to MIP mapping is valid for.                      |       |
| ``positive``                         | The direction of a vertical energy (heat) flux or surface momentum flux (stress) input; use 'up' or 'down' depending on whether the direction is positive when it is directed upward or downward, respectively. This argument is required for vertical energy and salt fluxes, for flux correction fields, and for surface stress.| [1]   |
| ``status``                           | The status of the MIP requested variable. Valid values are ``ok`` and ``embargoed``.         | [2]   |
| ``units``                            | The units of the data of the MIP requested variable i.e., after the ``expression`` has been applied.           | [3]   |


[1] This information is used by CMOR to determine whether a sign change is
necessary to make the data consistent with the MIP requirements. For more
information, please see the `cmor_variable`_ section in the
`CMOR Documentation`_.

[2] The MIP requested variables are reviewed to ensure they have been
produced correctly. MIP requested variables that have not passed review will
not be submitted to ESGF and so will not be available for other institutes to
use.

[3] See the documentation for the
:func:`mip_convert.new_variable.Variable.process` method.

The following options are optional:

| Optional Options |                                   Description                                                        | Notes |
|------------------|------------------------------------------------------------------------------------------------------|-------|
| ``comment``      | The details relating to the model to MIP mapping that should be written to the output netCDF file, e.g., to qualify the details of the model to MIP mapping, add health warnings,etc.                    |       |
| ``notes``        | Any details relating to the model to MIP mapping that should not be written to the output netCDF file, e.g., who added the model to MIP mapping, why, reasons for using this model to MIP mapping over another in certain cases, any other special cases notes, etc.               |       |
| ``component``    | A space-separated list of components that the |model to MIP mapping| is valid for.                   |       |
| ``valid_min``    | The minimum valid value for the data of the MIP requested variable; values in the data lower than this value are replaced with zero. |       |

Each |input variable| in an expression must contain one of the following:

| Expression Items  | File Type |                                       Description                                       | Notes |
|-------------------|-----------|-----------------------------------------------------------------------------------------|-------|
| ``stash``         | PP        | LBUSER(4), |STASH Code|, see Chapter 4 (page 25) of `Input and Output File Formats`_    |       |
| ``variable_name`` | netCDF    | The name of the data variable in the model output files that is used to create the input variable.   |       |

For example:

* ``expression = m01s03i236``
* ``expression = sitemptop``

Expressions can use numerical values and constants (which must be written using
upper case letters; constants are available in
:mod:`mip_convert.process.constants`):

* ``expression = rain_ai * 100. * SECONDS_IN_DAY``

For atmospheric tendency diagnostics, the atmospheric model timestep must be
specified (the value of the atmospheric model timestep is obtained from the 
user configuration file, please see the `request_section` in the
`user_guide`):

* ``expression = m01s30i181 / ATMOS_TIMESTEP``

To specify additional constraints, use square brackets:

* ``expression = m01s08i223[blev=0.05]``
* ``expression = pbo[cell_methods=time: mean (interval: 120 s)]``

Multiple values for a single constraint should be separated by spaces:

* ``expression = m01s30i201[blev=850.0 500.0 250.0]``

Multiple constraints within the square brackets should be separated by commas:

* ``expression = m01s02i204[lbplev=4, lbtim=122]``

In cases where it is not possible to describe the conversion of the
|input variable| / |input variables| to the |MIP requested variable| using a
basic expression like the ones above, a function can be specified:

* ``expression = my_function_name(m01s03i236)``

The values of the arguments of the function must follow the same syntax as the
basic expression.

The following constraints can currently be used in an ``expression``:

| Expression Items  | File Type |                                       Description                                       | Notes |
|-------------------|-----------|-----------------------------------------------------------------------------------------|-------|
| ``blev``          | PP        | BLEV, level, see Chapter 4 (page 26) of `Input and Output File Formats`_                |       |
| ``cell_methods``  | netCDF    | The `cell methods`_                                                                     |       |
| ``depth``         | netCDF    | Value of the depth coordinate                                                           |       |
| ``lbplev``        | PP        | LBUSER(5), pseudo level, see Chapter 4 (page 25) of `Input and Output File Formats`_    |       |
| ``lbproc``        | PP        | LBPROC, processing code, see Chapter 4 (page 21) of `Input and Output File Formats`_    |       |
| ``lbtim``         | PP        | LBTIM, time indicator, see Chapter 4 (page 17) of `Input and Output File Formats`_      |       |
| ``lbtim_ia``      | PP        | IA component of LBTIM (sampling frequency)                                              |       |




## How to Add a New Model to MIP mapping

!!! note
    If you like to add permanently your changes to the CDDS project, then you must follow the common development workflow, see: Development Workflow Using Jira. 

### Requried Information
1. the MIP requested variable name and the MIP table identifier.
1. the constraints, i.e., the data to be read from the model output files to create the input variables.
1. an expression describing how to process the input variables to produce a MIP output variable.
1. the units of the MIP output variable after the expression has been applied.
    1. It is not necessary to include the units in model to MIP mappings used for netCDF model output files if the expression consists of a single constraint.
1. the component, which is the domain as described ​here.


### Determine which configuration file the model to MIP mapping should be added to:
2. the model to MIP mapping configuration files are located in the mip_convert/process sub package (their names end in _mappings.cfg).
3. if there is currently no entry for the MIP requested variable name in the model to MIP mapping configuration files (use, e.g. grep <mip_requested_variable_name> <branch>/mip_convert/mip_convert/process/*_mappings.cfg), add the model to MIP mapping to common_mappings.cfg.
4. if there is already an entry in common_mappings.cfg, add the model to MIP mapping to the appropriate <mip_table_id>_mappings.cfg configuration file.
5. for multiple model to MIP mappings for the same MIP requested variable name, any expressions containing lbproc=128 should be added to common_mappings.cfg, while others should be added to the appropriate <mip_table_id>_mappings.cfg configuration file.
6. if there are any issues, please ask Matthew Mizielinski.


### Add the model to MIP mapping to the appropriate configuration file.
2. The sections in the model to MIP mapping configuration files are the MIP requested variable names and are listed in alphabetical order.
3. If the expression continues beyond the 120 character line limit, add a new line before a binary operator, see ​PEP8.
4. If the expression contains a function and an appropriate function does not already exist, add the function to mip_convert/process/processors.py​. The function:
    1. can have any number of arguments, each corresponding to a cube.
    2. should work directly on the cube(s) (i.e., do not make a copy of the cube(s) or the data).
    3. should not update the standard_name or long_name of the cube(s) (the ​MIP table contains this information and will be automatically added to the output netCDF files by CMOR).
    4. must return a single cube.


### Test the model to MIP mapping

Locate the model output files that contain the necessary constraints.

Setup the environment to use the branch containing the new model to MIP mapping:

```bash
source setup_env_for_devel
mip_convert
```

