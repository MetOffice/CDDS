# Installation

=== "On Azure (Met Office)"

    - [x] Login to the `cdds` account.
          ```bash
          xsudo -u cdds bash -l
          ```
    - [x] Activate the base `conda` environment
          ```bash
          conda activate
          ```
    - [x] Obtain the conda environment file
          ```bash
          wget https://raw.githubusercontent.com/MetOffice/CDDS/refs/tags/<tagname>/environment.yml
          ```
    - [x] Update locations pointed to within the environment file:
          ```bash
          sed -i "s/<location>/X.Y.Z/" environment.yml
          ```
    - [x] Create environment
          ```bash
          conda env create -f environment.yml -p $HOME/conda_environments/cdds-X.Y.Z
          ```
          where `X.Y.Z` is the new version number of CDDS

    - [x] Activate environment and set `CDDS_ENV_COMMAND` variable:
          ```bash
          conda activate cdds-X.Y.Z
          conda env config vars set CDDS_ENV_COMMAND="conda activate $HOME/conda_environments/cdds-X.Y.Z"
          ```
          where `X.Y.Z` is the new version number of CDDS

    - [x] Set the `CDDS_PLATFORM` and `CDDS_ETC` variables
          ```bash
          conda env config vars set CDDS_PLATFORM=AZURE
          conda env config vars set CDDS_ETC=$HOME/etc
          ```

    - [x] Confirm environment variables:
          ```bash
          echo $CYLC_VERSION
          echo $LC_ALL
          echo $TZ
          echo $CDDS_PLATFORM
          echo $CDDS_ETC
          echo $CDDS_ENV_COMMAND
          ```

          | Variable    | Value                                |
          | ----------- | ------------------------------------ |
          | `$CYLC_VERSION`     | `8` |
          | `$LC_ALL`           | `en_GB.UTF-8`  |
          | `$TZ`               | `UTC` |
          | `$CDDS_PLATFORM`    | `AZURE` |
          | `$CDDS_ETC`         | `$HOME/etc` |
          | `$CDDS_ENV_COMMAND` | `$conda activate $HOME/conda_environments/cdds-3.2.0` |



=== "On Jasmin"
    - [x] Login to one of the JASMIN [sci-servers](https://help.jasmin.ac.uk/docs/interactive-computing/sci-servers/#available-sci-servers) as the `cdds` user.

    - [x] Activate the `base` miniforge `conda` environment
          ```
          source $HOME/software/miniforge3/bin/activate
          ```
    - [x] Obtain the conda environment file for the release.
          ```bash
          wget https://raw.githubusercontent.com/MetOffice/CDDS/refs/tags/<tagname>/environment.yml
          ```
    - [x] Update locations pointed to within the environment file (omitting the leading `v`)
          ```bash
          sed -i "s/<location>/X.Y.Z/" environment.yml
          ```

    - [x] Create environment, where `X.Y.Z` is the new version number of CDDS
          ```bash
          conda env create -f environment.yml -p $HOME/conda_environments/cdds-X.Y.Z
          ```

    - [x] Set the `CDDS_PLATFORM` and `CDDS_ETC` variables
          ```bash
          conda activate cdds-X.Y.Z
          conda env config vars set CDDS_PLATFORM=JASMIN
          conda env config vars set CDDS_ETC=$HOME/etc
          ```

    - [x] Set the `CDDS_ENV_COMMAND` variable making sure to substitue `X.Y.Z` with the appropriate version number.
          ```bash
          conda env config vars set CDDS_ENV_COMMAND="$HOME/software/miniforge3/bin/activate $HOME/conda_environments/cdds-X.Y.Z"
          ```

    - [x] Deactivate the environment
          ```bash
          conda deactivate
          ```
    - [x] Confirm that the environment variables were set correctly.
          ```bash
          $HOME/software/miniforge3/bin/activate $HOME/conda_environments/cdds-X.Y.Z
          ```
          ```bash
          echo $CYLC_VERSION
          echo $LC_ALL
          echo $TZ
          echo $CDDS_PLATFORM
          echo $CDDS_ETC
          echo $CDDS_ENV_COMMAND
          ```

          | Variable    | Value                                |
          | ----------- | ------------------------------------ |
          | `$CYLC_VERSION`     | `8` |
          | `$LC_ALL`           | `en_GB.UTF-8`  |
          | `$TZ`               | `UTC` |
          | `$CDDS_PLATFORM`    | `JASMIN` |
          | `$CDDS_ETC`         | `$HOME/etc` |
          | `$CDDS_ENV_COMMAND` | `$HOME/software/miniforge3/bin/activate $HOME/conda_environments/cdds-X.Y.Z` |

## Ensure all the tests pass in the 'real live environment'

!!! warning
    Tests can only be run on Azure (Met Office).

- [x] The tests must be executed as the `cdds` user
- [x] Set the following environment variable, making sure to replace `X.Y.Z` with the relevant version.
      ```bash
      export SRCDIR=$HOME/conda_environments/cdds-X.Y.Z/lib/python3.10/site-packages
      ```
- [x] Run the following tests.
      ```bash
      echo "# Executing tests for cdds:"
      pytest -s $SRCDIR/cdds --doctest-modules -m 'not slow and not integration and not rabbitMQ and not data_request'
      pytest -s $SRCDIR/cdds -m slow
      pytest -s $SRCDIR/cdds -m integration
      pytest -s $SRCDIR/cdds -m data_request
      echo "# Executing tests for mip_convert:"
      pytest -s $SRCDIR/mip_convert --doctest-modules -m 'not slow and not mappings and not superslow'
      pytest -s $SRCDIR/mip_convert -m mappings
      pytest -s $SRCDIR/mip_convert -m slow
      ```

!!! info
    Slow unit tests for `transfer` and `cdds_configure` will display error messages to standard output. This is intentional, 
    and does not indicate the tests fail (see `transfer.tests.test_command_line.TestMainStore.test_transfer_functional_failing_moo()` 
    for details).


## Troubleshooting

!!! info 
      If the `wheel` installation fails then you can end up with `#!python` rather than the full paths – this is known to be caused by not having 
      `_DEV` updated in the packages, possibly due to tagging without pulling the release branch from the repository first
