# CDDS Extract

The Extract package enables a user to extract a subset of climate model output files from the MASS tape archive. This is useful because raw atmosphere and ocean output is stored in massive files, containing multiple fields, and their large volume make all processing very slow. Before data transfer happens, Extract selects only relevant bits of output, necessary to produce the requested, CMORised variables.

Since CDDS 2.2, Extract is embedded within the `cdds_convert` script, and it is no longer necessary to run it as a separate process. It is also worth mentioning that despite working with only a subset of climate model output, data transfer from MASS is typically the longest step in the whole CDDS processing pipeline, can take many days, and is prone to failures caused by MASS misbehaviour.

## An overview of Extract

The user configures the extraction process using the `request` file.
The cdds_extract script then performs the following processing steps:

* retrieves the data dissemination configuration from the `request` file.
* retrieves the `requested variables list` for the experiment.
* retrieves the `model to MIP mapping` for each `MIP requested variable`
* logs information on the variables for which authorised mappings are available and variables/mappings that are not available and why.
* creates directories for holding the retrieved data from MASS, the post-processed data which will be disseminated and the directories used to hold the artifacts used by other cdds processes (e.g. log files)
* creates appropriate PP and netCDF variable filter files that are used to filter the data retrieved from MASS before it is copied to disk.
* checks that MASS holds the relevant data collections and constructs MOOSE commands that will retrieve the required model data from these data collections (optionally incorporating the relevant filter files)
* submits constructed MOOSE commands and reports progress in text logs
* performs validation on the retrieved data to check it meets processing requirement