# Release Procedure

## Inform users of the upcoming change (if necessary)

!!! info
    Ask [Matthew Mizielinski](mailto:matthew.mizielinski@metoffice.gov.uk) if it is worth announcing the new version.

## Make the appropriate changes to the code

### Changes in the CDDS Project

#### Branch from the appropriate release branch

```bash
git checkout <release_branch>
git checkout -b <ticket_number>_v<tag>_release
```

where `<release_branch>` is the name of the release branch. If an appropriate release branch doesn't exist, create one:

```bash
git checkout main
git checkout -b v<release_version>_release
```

where `<release_version>` is e.g. `3.1`.

#### Modify the CDDS code

- [x] Update the development tag in `cdds/cdds/__init__.py` and `mip_covert/mip_convert/__init__.py`
    ```bash
    _DEV = False
    ```
    Use following command to do that:
    ```bash
    sed -i "s/_DEV = True/_DEV = False/" */*/__init__.py
    ```
- [x] Check `_NUMERICAL_VERSION` in `cdds/cdds/__init__.py` and `mip_covert/mip_convert/__init__.py`.
      It should be set to the current release version e.g. `3.1.0` (This must include any suffixes e.g. for
      release candidates)
- [x] Update any version numbers of dependencies that need updating in `setup_env_for_cdds`
- [x] Build the documentation
      1. Deploy the new version of the document:
         ```bash
         mike deploy <last_major_release_version>
         ```
         where `last_major_release_version` is the last major release version, e.g `3.1`
      2. Verify the new deployment works as expected.
         ```bash
         mike serve
         ```
      3. Publish the new documentation version:
         ```bash
         git push origin gh-pages
         ```
      For more information, see [Documentation](documentation.md). If you have any doubts, please speak to Jared or Matthew.
- [x] If releasing a new minor version of CDDS, e.g. `3.1.0`, update the development environment name in `setup_env_for_devel` to point to the new version, e.g. `cdds-3.1_dev`.
- [x] Ensure that:
    -  All changes  since the last release have been described in the relevant `CHANGES.md` files. These should be added as a separate commit to allow 
       cherry picking onto main later
    - Any new files added since the last release that do not have a `.py` extension are included in `MANIFEST.in` and `setup.py`.
- [x] Create a pull request for the changes. After the pull request is approved, merge the changes into the release branch, **but do not squash merge them**. 
      This will allow you cherry-pick release notes from the release branch into main.

!!! warning
    After changing this version number, the setup script won't work until the new version has been installed centrally in the cdds account. 


### Create a tag

=== "Using command line"

    Only those that have admin permissions on the CDDS repository can create tags.

    - [x] Switch to the branch you want to tag (normally, the release branch) and ***make sure you have pulled changes on github to your local branch – 
      failure to do this can lead to installation errors that manifest as failure to build wheels***
    - [x] Create the tag:
          ```bash
          git tag <tagname> -a
          ```
          The `<tagname>` normally is the release version, e.g. `v3.1.0`.
    - [x] Push the tag to the branch:
          ```bash
          git push origin <tagname>
          ```
    - [x] To show all tags and check if your tag is successfully created, run:
          ```bash
          git tag
          ```

=== "Using GitHub"

    !!! info
        Github has a good documentation about release processes, see: [Managing releases - GitHub Docs](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository)

### Install the code

Follow the instructions provided in the [CDDS installation]()

### Ensure all the tests pass in the 'real live environment'

- [x] The test must be executed as `cdds` user
      ```bash
      export SRCDIR=$HOME/software/miniconda3/envs/cdds-X.Y.Z/lib/python3.8/site-packages/
      echo "# Executing tests for cdds:"
      pytest -s $SRCDIR/cdds --doctest-modules -m 'not slow and not integration and not rabbitMQ and not data_request'
      pytest -s $SRCDIR/cdds -m slow
      pytest -s $SRCDIR/cdds -m integration
      pytest -s $SRCDIR/cdds -m data_request
      echo "# Executing tests for mip_convert:"
      pytest -s $SRCDIR/mip_convert --doctest-modules -m 'not slow and and not mappings and not superslow'
      pytest -s $SRCDIR/mip_convert -m mappings
      pytest -s $SRCDIR/mip_convert -m slow
      ```
      where `X.Y.Z` is the version number of CDDS.

!!! info
    Slow unit tests for `transfer` and `cdds_configure` will display error messages to standard output. This is intentional, 
    and does not indicate the tests fail (see `transfer.tests.test_command_line.TestMainStore.test_transfer_functional_failing_moo()` 
    for details).

### Restore development mode and bump version

- [x] Update the development tag and version number in `<cdds_component>/<cdds_component>/__init__.py`:
      ```bash
      _DEV = True
      _NUMERICAL_VERSION = '<next_version>'
      ```
      where `<next_version>` is the next minor version, e.g. `3.1.1`.
- [x] Commit and push the change directly to the release branch. The commit message should be:
      ```bash
      <ticket_number>: Restore development mode.
      ```

### Ensure release note changes propagate into the main branch

=== "Using cherry-pick"
    
    - [x] Ensure local copy of both `main` and `release_branch` are up to date.
    - [x] On the main branch use the `git cherry-pick` command to pull in just the `CHANGES.md` updates with release notes and commit them.

=== "Using merge"
    
    If you are unable to use the cherry-pick for the changes then the following may be useful.
    
    - [x] `git merge` the release branch into the trunk e.g., `git merge v3.1_release --no-commit`
    - [x] Inspect the differences in the local copy of the main branch
    - [x] Revert any changes other than to the `CHANGES.md` file
    - [x] Commit and push changes to the main branch.


!!!important
    **Do not delete the release branch! (expect Matthew Mizielinski told you so)**

### Create Release on GitHub

Create a release on github from the tag. Include all major release notes and ensure that all links back to Jira work as expected. 
Create a discussion announcement from the release.

### Close Jira ticket

Set the status of the Jira ticket to `Done`.

### Complete the milestone

For completing the milestone, have a chat with [Matthew Mizielinski](mailto:matthew.mizielinski@metoffice.gov.uk) which Jira epic needs 
to be updated or even closed.

!!!info
    The list of Milestone epics can be found at the [road map page](https://metoffice.atlassian.net/jira/software/projects/CDDSO/boards/634/roadmap) 
    in Jira.
