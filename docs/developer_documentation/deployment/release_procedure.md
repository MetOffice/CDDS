# Release Procedure

The changes necessary for the release are first made on a "deployment" branch which are then merged in to the release branch via a pull request.
The following diagram gives an overview of the steps that follow.

``` mermaid
gitGraph
   commit id: "some feature"
   branch v3.1_release
   checkout v3.1_release
   branch CDDSO-X_3.1.0_release
   checkout CDDSO-X_3.1.0_release
   commit id: "Disable Dev Mode"
   commit id: "Update CHANGES.md"
   checkout v3.1_release
   merge CDDSO-X_3.1.0_release tag: "v3.1.0"
   commit id: "Enable Dev Mode / Version"
   commit id: "New 3.1.1 features"
   checkout main
   cherry-pick id: "Update CHANGES.md"
```


## Create a Deployment Branch


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


## Prepare the Deployment Branch

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
- [x] Ensure that:
    - All changes  since the last release have been described in the relevant `CHANGES.md` files. These should be added as a separate commit to allow 
       cherry picking onto main later
    - Any new files added since the last release that do not have a `.py` extension are included in `MANIFEST.in` and `setup.py`.

## Publish the Documentation

1. Deploy the new version of the documentation.
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
4. If a major version is released then the new documentation version must be set as default:
    ```bash
    mike deploy <major_release_version> latest --update-aliases --push
    ```
For more information, see [Documentation](documentation.md). If you have any doubts, please speak to Jared or Matthew.

## Merge Deployment Branch into Release Branch

- [x] Create a pull request for the changes. After the pull request is approved, merge the changes into the release branch, **but do not squash merge them**. 
      This will allow you cherry-pick release notes from the release branch into main.

!!! warning
    After changing this version number, the setup script won't work until the new version has been installed centrally in the cdds account. 


## Create a tag

!!! danger
    You must remember to `git checkout` the `v3.X_release` branch and then `git pull` the changes that were merged via PR.

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
          git tag -l
          ```

=== "Using GitHub"

    !!! info
        Github has a good documentation about release processes, see: [Managing releases - GitHub Docs](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository)

## Install the code

Follow the instructions provided in the [Installation](cdds_installation.md) guide.


## Restore development mode and bump version

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

## Propagate Release Note to main

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

## Create Release on GitHub

Create a release on github from the tag. Include all major release notes and ensure that all links back to Jira work as expected. 
Create a discussion announcement from the release.

## Close Jira ticket

Set the status of the Jira ticket to `Done`.
