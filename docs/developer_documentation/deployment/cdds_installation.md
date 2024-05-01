# CDDS Installation

!!! warning
    This page is still work-in-progress! Please work closely with the CDDS team when installing CDDS.

=== "On Met Office"

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
    - [x] Set default branch name for CDDS Convert workflow (`u-ak283`). At the Met Office this will be `tags/X.Y.W` where 
          `X.Y.W` is the most recent tag of the workflow (this is not updated for every version of CDDS)
          ```bash
          conda env config vars set CDDS_CONVERT_WORKFLOW_BRANCH="tags/X.Y.W"
          ```
    - [x] Set default branch name for CDDS Processing workflow (`u-cy526`). At the Met Office this will be `tags/X.Y.W` where 
          `X.Y.W` is the most recent tag of the workflow (this is not updated for every version of CDDS)
          ```bash
          conda env config vars set CDDS_PROCESSING_WORKFLOW_BRANCH="tags/X.Y.W"
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
          echo $CDDS_CONVERT_WORKFLOW_BRANCH
          echo $CDDS_PROCESSING_WORKFLOW_BRANCH
          ```
          You should see `en_GB.UTF-8` for `LC_ALL` plus the command set above for `CDDS_ENV_COMMAND` and the value for 
          `CDDS_CONVERT_WORKFLOW_BRANCH` and the value for `$CDDS_PROCESSING_WORKFLOW_BRANCH`.

=== "On Jasmin"
    !!! warning
        This section will be updated soon

    !!! info
        The recommended location for installation is `miniconda3` environment under `/gws/smf/j04/cmip6_prep/cdds-env-python3/miniconda3`

    - [x] Login to the `sciX` JASMIN server.
    - [x] Activate conda without loading an environment
          ```bash
          . /gws/smf/j04/cmip6_prep/cdds-env-python3/miniconda3/bin/activate
          ```
    - [x] Obtain environment file
          ```bash
          wget https://github.com/MetOffice/CDDS/blob/<tagname>/environment.yml
          ```
          or download it manually from Github
    - [x] Update locations pointed to within the environment file:
          ```bash
          sed -i "s/<location>/X.Y.Z/" environment.yml
          ```
    - [x] Create environment
          ```bash
          conda env create -f environment.yml -n cdds-X.Y.Z
          ```
          where `X.Y.Z` is the new version number of CDDS
    - [x] Activate environment and set `CDDS_ENV_COMMAND` variable
          ```bash
          conda activate cdds-X.Y.Z
          conda env config vars set CDDS_ENV_COMMAND="source /gws/smf/j04/cmip6_prep/cdds-env-python3/miniconda3/bin/activate cdds-X.Y.Z"
          ```
    - [x] Set default branch name for CDDS Convert workflow (`u-ak283`). At the Met Office this will be `tags/X.Y.W` where 
          `X.Y.W` is the most recent tag of the workflow (this is not updated for every version of CDDS)
          ```bash
          conda env config vars set CDDS_CONVERT_WORKFLOW_BRANCH="tags/X.Y.W"
          ```
          on JASMIN the tag used, and set here should have an `_JASMIN` suffix.
    - [x] Set default branch name for CDDS Processing workflow (`u-cy526`). At the Met Office this will be `tags/X.Y.W` where 
          `X.Y.W` is the most recent tag of the workflow (this is not updated for every version of CDDS)
          ```bash
          conda env config vars set CDDS_PROCESSING_WORKFLOW_BRANCH="tags/X.Y.W"
          ```
          on JASMIN the tag used, and set here should have an `_JASMIN` suffix.
    - [x] Install `nco` library
          ```bash
          conda install -c conda-forge nco
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
          echo $CDDS_CONVERT_WORKFLOW_BRANCH
          echo $CDDS_PROCESSING_WORKFLOW_BRANCH
          ```
          You should see `en_GB.UTF-8` for `LC_ALL` and the command set above for `CDDS_ENV_COMMAND` and the value for 
          `CDDS_CONVERT_WORKFLOW_BRANCH` and the value for `$CDDS_PROCESSING_WORKFLOW_BRANCH`.
