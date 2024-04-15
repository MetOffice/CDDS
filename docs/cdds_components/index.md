## List of Components

| Component Name   | Description                          |
| ---------------- | ------------------------------------ |
| `archive` | The cdds_transfer package enables a user to store the output data products in the MASS archive and make them available for download by the ESGF node run by CEDA.  |
| `common`    | The cdds_common package will supersedes the HadSDK component. It contains a collection of generic Python code used by one or more of the CDDS components. |
| `configure` | The cdds_configure package enables a user to produce the user configuration file for MIP Convert. |
| `convert` | - |
| `extract`          | The extract package enables a user to efficiently extract the climate data that will be used in the dissemination process from MASS.
| `mip_convert`      | The mip_convert package enables a user to produce the output netCDF files for a MIP using model output files.
| `misc`             | - |
| `prepare`          | The cdds_prepare package enables a user to create the requested variables list and directory structures in preparation for subsequent CDDS components to be run. |
| `qc`               | The cdds_qc package enables a user to check whether the output netCDF files conform to the WGCM CMIP standards. |


## Special Plugin Components

| Component Name     | Description                          |
| ------------------ | ------------------------------------ |
| QC CF1.7 Plugin    | The CF1.7 plugin (cdds_qc_plugin_cf17) is an extension of the original CF1.6 checker, providing some additional features and configurability. |
| QC CMIP6 Plugin    | The CMIP6 Compliance Checker Plugin (cdds_qc_plugin_cmip6) provides a suite of tests related to CMIP6 compliance. |
