# Release Procedure

## Inform users of the upcoming change (if necessary)

!!! info
    Ask [Matthew Mizielinski](mailto:matthew.mizielinski@metoffice.gov.uk) if it is worth announcing the new version.

## Make the appropriate changes to the code

### CDDS Convert Suite (u-ak283)

If there have been [any changes](https://code.metoffice.gov.uk/trac/roses-u/diff?new_path=%2Fa%2Fk%2F2%2F8%2F3%2Ftags%2F1.1.1&old_path=%2Fa%2Fk%2F2%2F8%2F3%2Ftrunk&new_rev=121711&old_rev=126177) 
to the [CDDS Convert suite](https://code.metoffice.gov.uk/trac/roses-u/browser/a/k/2/8/3/) since the last tag, tag the CDDS Convert suite:

```bash
fcm copy --parents https://code.metoffice.gov.uk/svn/roses-u/a/k/2/8/3/cdds_release_<release_branch_version> https://code.metoffice.gov.uk/svn/roses-u/a/k/2/8/3/tags/<tag>
```

where `<tag>` is the CDDS version number, e.g. `1.0.1` and `<release_branch_version>` is major or minor version numbers, e.g. `1.0`.

If the suite release branch for this version does not yet exist, create a release branch from the trunk as follows:

```bash
fcm bc cdds_release_<release_branch_version> https://code.metoffice.gov.uk/svn/roses-u/a/k/2/8/3/trunk
```

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

where `<release_version>` is e.g. `1.0`.

#### Modify the CDDS code

- [x] Update the development tag in `cdds/cdds/__init__.py` and `mip_covert/mip_convert/__init__.py`
    ```bash
    _DEV = False
    ```
    Use following command to do that:
    ```bash
    sed -i "s/_DEV = True/_DEV = False/" */*/__init__.py
    ```
- [x] Update any version numbers of dependencies that need updating in `setup_env_for_cdds`
- [x] Build the documentation

!!! warning
    There is no release process defined for the new documentations. Please, speak with Jared and Matthew how to release the documentations.

- [x] If releasing a new minor version of CDDS, e.g. `2.1.0`, update the development environment name in `setup_env_for_devel` to point to the new version, e.g. `cdds-2.1_dev`.
- [x] Update the default CDDS Convert suite value in the conversion section of the request configuration
- [x] Ensure that:
    -  All changes  since the last release have been described in the relevant `CHANGES.rst` files. These should be added as a separate commit to allow 
       cherry picking onto main later
    - Any new files added since the last release that do not have a `.py` extension are included in `MANIFEST.in` and `setup.py`.
- [x] Create a pull request for the changes. After the pull request is approved, merge the changes into the release branch, **but do not squash merge them**. 
      This will allow you cherry-pick release notes from the release branch into main.

!!! warning
    After changing this version number, the setup script won't work until the new version has been installed centrally in the cdds account. 
    The installation process is documented at [CDDSInstallation2](https://code.metoffice.gov.uk/trac/cdds/wiki/CDDSInstallation2).

### Create a tag

=== "Using command line"

    Only those that have admin permissions on the CDDS repository can create tags.

    - [x] Switch to the branch you want to tag (normally, the release branch) and ***make sure you have pulled changes on github to your local branch – 
      failure to do this can lead to installation errors that manifest as failure to build wheels***
    - [x] Create the tag:
          ```bash
          git tag <tagname> -a
          ```
          The `<tagname>` normally is the release version, e.g. `v2.1.2`.
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
      where `<next_version>` is the next minor version, e.g. `2.1.2`.
- [x] Commit and push the change directly to the release branch. The commit message should be:
      ```bash
      <ticket_number>: Restore development mode.
      ```

### Ensure release note changes propagate into the main branch

=== "Using cherry-pick"
    
    - [x] Ensure local copy of both `main` and `release_branch` are up to date.
    - [x] On the main branch use the `git cherry-pick` command to pull in just the `CHANGES.rst` updates with release notes and commit them.

=== "Using merge"
    
    If you are unable to use the cherry-pick for the changes then the following may be useful.
    
    - [x] `git merge` the release branch into the trunk e.g., `git merge v2.3_release --no-commit`
    - [x] Inspect the differences in the local copy of the main branch
    - [x] Revert any changes other than to the `CHANGES.rst` file
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
