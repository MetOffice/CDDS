# Common issues seen running CDDS

This page attempts to describe ways in which we've seen things go wrong and their work around, and we'll attempt to update it as new problems are observed.

## 1. MASS error OPERATION_FAILED

We think this means that MASS is struggling to handle the complexity of a select command. 
Until further notice use the following process to work around this.

### Deactivate a set of variables in the correponding stream.

Edit the variables file indicated in the request file and prefix a number of lines (e.g. 10) with `#` and
then run the command

```
prepare_generate_variable_list <request config file> -r
```

and then retrigger the failed task

Note that if this leaves some of the MIP Convert tasks with no work to do, they will fail and modifications to the `rose-suite.conf` file will be needed.
In this case contact the CDDS team (@UKNCSP/cdds)

## 2. Insufficient matching coordinate metadata

e.g.

    Loading data for "CMIP7_seaIce.json: siconca_tavg-u-hxy-u"
    Unable to produce MIP requested variable "siconca_tavg-u-hxy-u" for "CMIP7_seaIce": error time_bnds have gaps between them
    error time_bnds have gaps between them
    Traceback (most recent call last):
    ...


We've seen this when the STASH configuration been set up incorrectly with the same STASH variables at multiple frequencies included in the same stream.
CDDS cannot handle this at all, so the only option is to deactivate the corresponding variables, i.e. comment them out of the variables list and run


    prepare_generate_variable_list <request config file> -r


before retriggering the failed task.

## 3. Extract validation failure

e.g. the following appears in the extract_validate log for the ap5 stream


    As a result, these variables cannot be produced:
	landIce: sbl_tavg-u-hxy-lnd, snm_tavg-u-hxy-lnd


This means that CDDS didn't find STASH codes it was expecting in the stream being extracted and therefore cannot produce the listed variables.

To deactivate these variables

1. Run `update_variables_from_validate <request file>` to automatically comment the variables from the variable list
2. Run `prepare_generate_variable_list <request file> -r` to update the config files within CDDS
3. Retrigger the corresponding `validate_extract_<stream>` task 

The cdds_convert workflow should then proceed.

## 4. QC task failure: `Cannot retrieve further_info_url` (exclusive to CMIP6/CMIP6Plus processing)

e.g.

        "mip_table": "APmon",
        "checker": "cmip6",
        "error_message": "Global attributes check: Cannot retrieve global attribute further_info_url",
        "affected_files": 2,
        "affected_vars": "ps"

It's likely that `further_info_url` was not set as described [here](cmip6.md#further_info_url_required).

You have two options:

1. If you have only processed a small amount of data (for instance if you're just experimenting), you can rerun the workflow with the corrected `request.cfg` file (see above).
2. If you don't wish to process the data from scratch again, contact the CDDS team and we can provide you with a script that you can run on your processed outputs that will fix them. You can then retrigger the QC step that previously failed and it should pass.
