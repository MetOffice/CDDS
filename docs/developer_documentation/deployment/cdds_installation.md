# Installation

=== "On Azure (Met Office)"

    !!! note
        This installation process requires a Conda installation of at least `v4.9`, earlier versions will raise errors around the setting of environment
        variables as part of the Conda environment creation commands

    - [x] Login to the `cdds` account (please see [Science Shared Accounts](http://www-twiki/Main/ScienceSharedAccounts) for more details):
          ```bash
           xsudo -u cdds bash -l
           ```
    - [x] Activate Conda environment (to make installation quicker):
          ```bash
          conda activate
          ```
    - [x] Obtain environment file:
          ```bash
          wget https://github.com/MetOffice/CDDS/blob/<tagname>/environment.yml
          ```
          or download it manually from Github.
    - [x] Update locations pointed to within the environment file:
          ```bash
          sed -i "s/<location>/X.Y.Z/" environment.yml
          ```
    - [x] Create environment
          ```bash
          conda env create -f environment.yml -p $HOME/conda_environments/cdds-X.Y.Z
          ```
          where `X.Y.Z` is the new version number of CDDS

    !!! note
        This has been updated following the roll out of Conda to MO systems. If the `-p` option is omitted then the installation will end up 
        under `$HOME/.conda` and will not be visible to other users.

    !!! info 
        If the `wheel` installation fails then you can end up with `#!python` rather than the full paths – this is known to be caused by not having 
        `_DEV` updated in the packages, possibly due to tagging without pulling the release branch from the repository first

    - [x] Activate environment and set `CDDS_ENV_COMMAND` variable:
          ```bash
          conda activate cdds-X.Y.Z
          conda env config vars set CDDS_ENV_COMMAND="conda activate $HOME/conda_environments/cdds-X.Y.Z"
          ```
          where `X.Y.Z` is the new version number of CDDS
          ```
    - [x] Set platform in the `CDDS_PLATFORM` variable:
          ```bash
          conda activate cdds-X.Y.Z
          conda env config vars set CDDS_PLATFORM=AZURE
          ```
    - [x] Confirm environment variables:
          ```bash
          # get out of cdds environment
          conda deactivate
          # load environment again
          conda activate cdds-X.Y.Z
          # print environment variables
          echo $LC_ALL
          echo $CDDS_ENV_COMMAND
          echo $CDDS_PARTITION
          ```
          You should see `en_GB.UTF-8` for `LC_ALL` plus the command 
          set above for `CDDS_ENV_COMMAND` and the `CDDS_PARTITION`.

=== "On Premise (Met Office)"

    !!! note
        This installation process requires a Conda installation of at least `v4.9`, earlier versions will raise errors around the setting of environment
        variables as part of the Conda environment creation commands

    - [x] Login to the `cdds` account (please see [Science Shared Accounts](http://www-twiki/Main/ScienceSharedAccounts) for more details):
          ```bash
           xsudo -u cdds bash -l
           ```
    - [x] Activate Conda mamba environment (to make installation quicker):
          ```bash
          . $HOME/software/miniconda3/bin/activate mamba
          ```
    - [x] Obtain environment file:
          ```bash
          wget https://github.com/MetOffice/CDDS/blob/<tagname>/environment.yml
          ```
          or download it manually from Github.
    - [x] Update locations pointed to within the environment file:
          ```bash
          sed -i "s/<location>/X.Y.Z/" environment.yml
          ```
    - [x] Create environment
          ```bash
          mamba env create -f environment.yml -p $HOME/software/miniconda3/envs/cdds-X.Y.Z
          ```
          where `X.Y.Z` is the new version number of CDDS

    !!! note
        This has been updated following the roll out of Conda to MO systems. If the `-p` option is omitted then the installation will end up 
        under `$HOME/.conda` and will not be visible to other users.

    !!! info 
        If the `wheel` installation fails then you can end up with `#!python` rather than the full paths – this is known to be caused by not having 
        `_DEV` updated in the packages, possibly due to tagging without pulling the release branch from the repository first

    - [x] Activate environment and set `CDDS_ENV_COMMAND` variable:
          ```bash
          conda activate cdds-X.Y.Z
          conda env config vars set CDDS_ENV_COMMAND="source $HOME/software/miniconda3/bin/activate cdds-X.Y.Z"
          ```
          where `X.Y.Z` is the new version number of CDDS
          ```
    - [x] Set platform in the `CDDS_PLATFORM` variable:
          ```bash
          conda activate cdds-X.Y.Z
          conda env config vars set CDDS_PLATFORM=EXETER
          ```
    - [x] Confirm environment variables:
          ```bash
          # get out of cdds environment
          conda deactivate
          # load environment again
          conda activate cdds-X.Y.Z
          # print environment variables
          echo $LC_ALL
          echo $CDDS_ENV_COMMAND
          echo $CDDS_PARTITION
          ```
          You should see `en_GB.UTF-8` for `LC_ALL` plus the command 
          set above for `CDDS_ENV_COMMAND` and the `CDDS_PARTITION`.

=== "On Jasmin"
    - [x] Login to one of the JASMIN science [servers](https://help.jasmin.ac.uk/docs/interactive-computing/sci-servers/#available-sci-servers) as the `cdds` user
    - [x] Activate the `base` miniforge `conda` environment
          ```
          source $HOME/software/miniforge3/bin/activate
          ```
    - [x] Obtain the conda environment file
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
    - [x] Uncomment the `cdds` and `mip_convert` python pip install lines.
          ```bash
            #- git+ssh://git@github.com-deploy/MetOffice/CDDS.git@v<location>#egg=cdds&subdirectory=cdds
            #- git+ssh://git@github.com-deploy/MetOffice/CDDS.git@v<location>#egg=mip_convert&subdirectory=mip_convert
          ```
    - [x] Set the `CDDS` variables making sure to replace `X.Y.Z` with the appropriate version number.
          ```bash
          conda env config vars set CDDS_PLATFORM=JASMIN
          conda env config vars set CDDS_ETC=$HOME/etc
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
