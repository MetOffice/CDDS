## Variable Mappings for CDDS

The following pages are constructed from the Mappings held in MIP convert:

* [UKESM1 Mappings](https://code.metoffice.gov.uk/doc/cdds/mappings_viewer/mappings_view_UKESM1.html)
* [HadGEM3 Mappings](https://code.metoffice.gov.uk/doc/cdds/mappings_viewer/mappings_view_HadGEM3.html)

## Mapping Hierarchy

The mappings within MIP Convert are arranged in a hierarchy with names in the following forms

1. ``common_mappings.cfg``
2. ``<mip_table>_mappings.cfg``
3. ``<base_model>_mappings.cfg``
4. ``<base_model>_<mip_table_id>_mappings.cfg``
5.  ``<model_id>_mappings.cfg``
6.  ``<model_id>_<mip_table_id>_mappings.cfg``

where `<base_model>` refers to the section of the model id before the first dash `-`, e.g. `"UKESM1"` or `"HadGEM3"`. 

Mappings in files furthest down this list overload those specified in files at the top.


## Model to MIP Mapping Configuration Files

Each of the above model to MIP mapping configuration files contains the following sections.

1. `[DEFAULT]`
2. `[COMMON]`
3. `[variable name]`


### The `[DEFAULT]` Section

The `[DEFAULT]` section contains options that are propagated to
all other sections. This is useful for setting a default value for a option for
all sections. A value provided for the same option in any other section will be
used for that section over the default value defined in the
`[DEFAULT]` section. 


### The `[COMMON]` Section

The `[COMMON]` section contains options that may be used by other
sections by using the syntax ``${COMMON:<option>}``. This is useful for setting
values for comments or notes that would otherwise be repeated multiple times in
the model to MIP mapping configuration files.


### The `[variable name]` Section(s)

The `[variable name]` sections provide the model to MIP mapping corresponding to the specified MIP requested variable and contains the following required options:

| <div style="width:110px">Required Options</div> |                                   Description                                                         | Notes  |
|--------------------------------------|------------------------------------------------------------------------------------------------------------------|--------|
| `dimension`                          | The dimensions of the MIP requested variable.                                                                    |        |
| `expression`                         | The expression required to convert the input variable / input variables to the MIP requested variable.           |        |
| `mip_table_id`                       | A space-separated list of MIP table identifiers that the model to MIP mapping is valid for.                      |        |
| `positive`                           | The direction of a vertical energy (heat) flux or surface momentum flux (stress) input; use 'up' or 'down' depending on whether the direction is positive when it is directed upward or downward, respectively. This argument is required for vertical energy and salt fluxes, for flux correction fields, and for surface stress.| [1]   |
| `status`                             | The status of the MIP requested variable. Valid values are `ok` and `embargoed`.                                 | [2][3] |
| `units`                              | The units of the data of the MIP requested variable i.e., after the `expression` has been applied.               |        |


**Notes**

1. This information is used by CMOR to determine whether a sign change is necessary to make the data consistent with the MIP requirements. For more information, please see the [cmor_variable](https://cmor.llnl.gov/mydoc_cmor3_api/#cmor_variable) section in the CMOR Documentation.
1. The MIP requested variables are reviewed to ensure they have been produced correctly, MIP requested variables that have not passed review will not be submitted to ESGF and so will not be available for other institutes to use.
1. This is used by CDDS, but does not affect MIP Convert behaviour

The following options are optional:

| Optional Options |                                   Description                                                        | Notes |
|------------------|------------------------------------------------------------------------------------------------------|-------|
| ``comment``      | The details relating to the model to MIP mapping that should be written to the output netCDF file, e.g., to qualify the details of the model to MIP mapping, add health warnings,etc.                    |       |
| ``notes``        | Any details relating to the model to MIP mapping that should not be written to the output netCDF file, e.g., who added the model to MIP mapping, why, reasons for using this model to MIP mapping over another in certain cases, any other special cases notes, etc.               |       |
| ``component``    | A space-separated list of components that the model to MIP mapping is valid for.                     |       |
| ``valid_min``    | The minimum valid value for the data of the MIP requested variable; values in the data lower than this value are replaced with zero. |       |

### Constructing an Expression

Each input variable in an expression must contain one of the following:

| <div style="width:110px">Expression Items</div>  | File Type |                                       Description                                       | Notes |
|-------------------|-----------|-----------------------------------------------------------------------------------------|-------|
| ``stash``         | PP        | LBUSER(4), STASH Code, see Chapter 4 (page 25) of UMDP F03    |       |
| ``variable_name`` | netCDF    | The name of the data variable in the model output files that is used to create the input variable.   |       |

!!! example "Example 1. One to One Mapping"

    * ``expression = m01s03i236``
    * ``expression = sitemptop``

!!! example "Example 2a. Constants and Arithmetic"

    Expressions can use numerical values and constants (which must be written using
    upper case letters; constants are available in
    :mod:`mip_convert.process.constants`):
    
    * ``expression = rain_ai * 100. * SECONDS_IN_DAY``

!!! example "Example 2b. Constants and Arithmetic"

    For atmospheric tendency diagnostics, the atmospheric model timestep must be
    specified (the value of the atmospheric model timestep is obtained from the 
    user configuration file, please see the `request_section` in the
    `user_guide`):
    
    * ``expression = m01s30i181 / ATMOS_TIMESTEP``

!!! example "Example 3a. Constraints"
    To specify additional constraints, use square brackets:
    
    * ``expression = m01s08i223[blev=0.05]``
    * ``expression = pbo[cell_methods=time: mean (interval: 120 s)]``

!!! example "Example 3b. Constraints"
    Multiple values for a single constraint should be separated by spaces:
    
    * ``expression = m01s30i201[blev=850.0 500.0 250.0]``

!!! example "Example 3c. Constraints"
    Multiple constraints within the square brackets should be separated by commas:
    
    * ``expression = m01s02i204[lbplev=4, lbtim=122]``

!!! example "Example 4. Processor"
    In cases where it is not possible to describe the conversion of the
    input variable / input variables to the MIP requested variable using a
    basic expression like the ones above, a function can be specified:
    
    * ``expression = my_function_name(m01s03i236)``
    
    The values of the arguments of the function must follow the same syntax as the
    basic expression.
    
The following constraints can currently be used in an ``expression``:

| Expression Items  | File Type |                                       Description                                       | Notes |
|-------------------|-----------|-----------------------------------------------------------------------------------------|-------|
| ``blev``          | PP        | BLEV, level, see Chapter 4 (page 26) of UMDP F03                                        |       |
| ``cell_methods``  | netCDF    | The [cell methods](https://cfconventions.org/cf-conventions/v1.6.0/cf-conventions.html#cell-methods)          |       |
| ``depth``         | netCDF    | Value of the depth coordinate                                                           |       |
| ``lbplev``        | PP        | LBUSER(5), pseudo level, see Chapter 4 (page 25) of UMDP F03                            |       |
| ``lbproc``        | PP        | LBPROC, processing code, see Chapter 4 (page 21) of UMDP F03                            |       |
| ``lbtim``         | PP        | LBTIM, time indicator, see Chapter 4 (page 17) of UMDP F03                              |       |
| ``lbtim_ia``      | PP        | IA component of LBTIM (sampling frequency)                                              |       |


## How to Add a New Model to MIP mapping

!!! note
    If you want to contribute your changes to CDDS then you must follow the development workflow.
    See the [Developer Documentation](../developer_documentation/development_practices.md) pages for guidance.


### Requried Information

1. the MIP requested variable name and the MIP table identifier.
1. the constraints, i.e., the data to be read from the model output files to create the input variables.
1. an expression describing how to process the input variables to produce a MIP output variable.
1. the units of the MIP output variable after the expression has been applied.
    1. It is not necessary to include the units in model to MIP mappings used for netCDF model output files if the expression consists of a single constraint.
1. the component, which is the domain as described ​here.


### Determine which configuration file the model to MIP mapping should be added to

1. Model to MIP mapping configuration files are located in the `mip_convert/process` sub package (their names end in `_mappings.cfg`).
2. if there is currently no entry for the MIP requested variable name in the model to MIP mapping configuration files (use, e.g. `grep <mip_requested_variable_name> <branch>/mip_convert/mip_convert/process/*_mappings.cfg`), add the model to MIP mapping to common_mappings.cfg.
3. if there is already an entry in `common_mappings.cfg`, add the model to MIP mapping to the appropriate `<mip_table_id>_mappings.cfg`` configuration file.
4. for multiple model to MIP mappings for the same MIP requested variable name, any expressions containing `lbproc=128` should be added to `common_mappings.cfg`, while others should be added to the appropriate `<mip_table_id>_mappings.cfg`` configuration file.
5. if there are any issues, please ask Matthew Mizielinski.


### Add the model to MIP mapping to the appropriate configuration file.

1. The sections in the model to MIP mapping configuration files are the MIP requested variable names and are listed in alphabetical order.
1. If the expression continues beyond the 120 character line limit, add a new line before a binary operator, see ​PEP8.
1. If the expression contains a function and an appropriate function does not already exist, add the function to `mip_convert/process/processors.py`​. The function:
    1. can have any number of arguments, each corresponding to a cube.
    2. should work directly on the cube(s) (i.e., do not make a copy of the cube(s) or the data).
    3. should not update the standard_name or long_name of the cube(s) (the ​MIP table contains this information and will be automatically added to the output netCDF files by CMOR).
    4. must return a single cube.


### Test the Model to MIP Mapping

Test and verify all mappings before submitting a pull request.
