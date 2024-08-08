# Update Request Configuration

The request configuration consists of following different sections:

`inheritance`
:   contains a setting that specify a template for the request. This section is optional.

`metadata`
:   contains all metadata settings about the experiment that should be processed, like the model ID or the MIP era.

`common`
:   contains common setting like the path to the root data folder or the path to the external plugin.

`data`
:   contains all settings that are used to archive the data in MASS.

`inventory`
:   contains all settings that are need to connect to and manage the inventory database.

`conversion`
:   contains settings that specify how CDDS is run, e.g., skip any steps when running CDDS.

`netcdf_global_attributes`
:   contains all attributes that will be set in the global attributes section of the CMOR file.

`misc`
:   contains any settings that do not fit in any other section.