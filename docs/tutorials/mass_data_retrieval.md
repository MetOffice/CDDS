# **Archived data retrieval tools**

We provide two command line tools for retrieving archived data from MASS. They can both be used at the Met Office, or via JASMIN:

1. [`cdds_retrieve_archived_variables`](#cdds_retrieve_archived_variables) Retrieves CMIP6 data using a list of variables provided by the user.

2. [`cdds_retrieve_archived_dataset`](#cdds_retrieve_archived_dataset) Retrieves a single CMIP6 or CMIP7 dataset based on the version number (recommended for CREPP users).

# **cdds_retrieve_archived_variables**

It's benefits include:

- Can be used locally or via SPICE.
- Copies the directory structure associated with the files.
- Customisable chunking to reduce load on infrastructure during retrieval.
- A dry run option to print actions without retrieving the files.

## Using it from the command line

The tool takes six arguments:

1. **moose_base_location (optional)**: The base moose path for the data. It's default is set to moose:/adhoc/projects/cdds/production/
2. **base_dataset_id:** e.g. CMIP6.CMIP.MOHC.UKESM1-0-LL.piControl.r1i1p1f2
3. **variables_file:** File containing the list of variables you would like to retrieve.
4. **destination_directory:** Where you would like the data extracted to.
5. **--chunk-size (optional):** The chunk size (in GB) for extraction. Default set to 100
6. **--dry-run (optional):** To do a test run without extracting the data.

???example
    ```
    cdds_retrieve_archived_variables CMIP6.CMIP.MOHC.UKESM1-0-LL.piControl.r1i1p1f2 variables_file desired/output/directory
    ```

## Usage via SPICE

Below is a template example script that would be run via a sbatch command.

???example
    ```bash
    #!/bin/bash -l

    #SBATCH --mail-type=END
    #SBATCH --mem=5G
    #SBATCH --qos=normal
    #SBATCH --time=30

    cdds_retrieve_archived_variables CMIP6.CMIP.MOHC.UKESM1-0-LL.piControl.r1i1p1f2 variables_file desired/output/directory
    ```

# **cdds_retrieve_archived_dataset**

This tool retrieves or lists a single dataset from MASS, identified by its full
dataset_id (including version), e.g.
`CMIP6.CMIP.MOHC.UKESM1-0-LL.piControl.r1i1p1f2.Amon.tas.gn.v20200828`. Unlike
`cdds_retrieve_archived_variables`, it does not require a variables file - it
operates on a single, fully-specified dataset.

It's benefits include:

- No dependency on the rest of CDDS (e.g. variables files, bulk retrieval).
- A `ls` action to list a dataset's files, sizes and checksums as JSON without retrieving them.
- Copies the directory structure associated with the files (optional).
- Customisable chunking to reduce load on infrastructure during retrieval.
- A dry run option to print actions without retrieving the files.

## Using it from the command line

The tool takes an action, followed by a dataset_id and (for `get`) a destination:

1. **action:** `get` retrieves files, `ls` lists them as JSON.
2. **dataset_id:** Full dataset_id, e.g. `CMIP6.CMIP.MOHC.UKESM1-0-LL.piControl.r1i1p1f2.Amon.tas.gn.v20200828`.
3. **destination (required for `get` only):** Destination directory.
4. **--create-directories-false (optional):** With `get`, do not mirror the DRS directory structure under destination.
5. **--mass-root (optional):** Root location in MASS. Defaults to `moose:/adhoc/projects/cdds/production/`.
6. **--dry-run (optional):** Print actions without retrieving files.
7. **--chunk-size (optional, `get` only):** The chunk size (in GB) for extraction. Default set to 100.

### Exit codes

- `0`: success
- `1`: dataset or version not found in MASS
- `2`: credentials/permissions error
- `3`: other error

???example "List a dataset's files as JSON"
    ```
    cdds_retrieve_archived_dataset ls CMIP6.CMIP.MOHC.UKESM1-0-LL.piControl.r1i1p1f2.Amon.tas.gn.v20200828
    ```

???example "Retrieve a dataset"
    ```
    cdds_retrieve_archived_dataset get CMIP6.CMIP.MOHC.UKESM1-0-LL.piControl.r1i1p1f2.Amon.tas.gn.v20200828 desired/output/directory
    ```

## Usage via SPICE

Below is a template example script that would be run via a sbatch command.

???example
    ```bash
    #!/bin/bash -l

    #SBATCH --mail-type=END
    #SBATCH --mem=5G
    #SBATCH --qos=normal
    #SBATCH --time=30

    cdds_retrieve_archived_dataset get CMIP6.CMIP.MOHC.UKESM1-0-LL.piControl.r1i1p1f2.Amon.tas.gn.v20200828 desired/output/directory
    ```