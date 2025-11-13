# Mass data retrieval

Data can be retrieved from MASS using our cdds_retrieve_data tool. This
can be used locally or via SPICE.

It's benefits include:

- Copying the directory structure associated with the files.
- Customisable chunking to reduce load on infrastructure during retrieval.
- A dry run option to print actions without retrieving the files.

!!!Note
    For JASMIN users, this tool is not currently functional, as it requires the use of recursive listings - which are not permitted on JASMIN.

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
    cdds_retrieve_data CMIP6.CMIP.MOHC.UKESM1-0-LL.piControl.r1i1p1f2 variables_file desired/output/directory
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

    cdds_retrieve_data CMIP6.CMIP.MOHC.UKESM1-0-LL.piControl.r1i1p1f2 variables_file desired/output/directory
    ```


