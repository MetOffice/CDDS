# Release Procedure

The changes needed for a release are first made on a deployment branch (denoted by `gh-issue_X.Y.Z` below) which are then merged in to the release branch via a pull request.

``` mermaid
gitGraph
   commit id: "some feature"
   branch vX.Y_release
   checkout vX.Y_release
   branch gh-issue_vX.Y.Z_release
   checkout gh-issue_vX.Y.Z_release
   commit id: "Disable Dev Mode"
   commit id: "Update CHANGES.md"
   checkout vX.Y_release
   merge gh-issue_vX.Y.Z_release tag: "vX.Y.Z"
   commit id: "Enable Dev Mode / Version"
   commit id: "Next micro release features (vX.Y.Z+1)"
   checkout main
   cherry-pick id: "Update CHANGES.md"
```

## Create the Deployment Branch

If this is a new major or minor release i.e `X.Y.0`, you will need to create a `vX.Y_release` branch from `main` if one does not already exist.

```bash
git checkout main
git checkout -b v<X.Y>_release
git push origin v<X.Y>_release
```

??? example

    ```bash
    git checkout main
    git checkout -b v3.2_release
    git push origin v3.2_release
    ```

Once the release branch has been created, or if it already exists, create the deployment branch for this release.

```bash
git checkout v<X.Y>_release
git checkout -b <gh-issue>_v<X.Y.Z>_release
git push -u origin <gh-issue>_v<X.Y.Z>_release
```

??? example

    ```bash
    git checkout v3.2_release
    git checkout -b 123_v3.2.1_release
    ```


## Prepare the Deployment Branch

Each of these steps should be made as separate commits to allow for cherry picking the `CHANGES.md` from
the release branch to `main`.

1. Update the `_DEV` flag in `cdds/cdds/__init__.py` and `mip_convert/mip_convert/__init__.py` to `False`
    ```bash
    sed -i "s/_DEV = True/_DEV = False/" */*/__init__.py
    ```

2. Set `_NUMERICAL_VERSION` in `cdds/cdds/__init__.py` and `mip_convert/mip_convert/__init__.py` to match 
    the release `X.Y.Z` you are preparing.

    !!! note
        This will likely have already been set correctly to the version you're preparing - in which case you can skip this step.

3. Update the `CHANGES.md` files with all the relevant changes from the last release.
    - Any new files added since the last release that do not have a `.py` extension are included in `MANIFEST.in` and `setup.py`.
    - The milestone issues filter can be useful to quickly view all the issues completed in the milestone you're releasing see [here](https://github.com/MetOffice/CDDS/issues?q=is%3Aclosed%20milestone%3A%22CDDS%20v4.0.4%22) for an example.
    - Double check with the rest of the team as to anything important that needs including.


## Merge Deployment Branch into Release Branch

Create a pull request for the changes. After the pull request is approved, merge the changes into the release branch, **but do not squash merge them**. 
This will allow you cherry-pick release notes from the release branch into main.


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

> **Note:** The default documentation version shown should always be the latest major release (e.g., `3.1`). In the above command, `<major_release_version>` refers to the version to set as default (e.g., `3.1`).

For more information on documentation, visit [documentation_practices.md](../documentation_practices.md).

If you have any doubts, please speak to Jared or Matthew.


## Create a tag

!!! danger
    You must remember to `git checkout` the `v3.X_release` branch and then `git pull` the changes that were merged via PR.

Only those that have admin permissions on the CDDS repository can create tags.

1. Switch to the branch you want to tag (normally, the release branch) and ***make sure you have pulled changes on github to your local branch – 
    failure to do this can lead to installation errors that manifest as failure to build wheels***
1. Create the tag:
        ```bash
        git tag <tagname> -a
        ```
        The `<tagname>` normally is the release version, e.g. `v3.1.0`.
        `vim` will require a commit message once you run that. Enter something like `v<X.Y.Z> release`, esc and :wq.
1. Push the tag to the branch:
        ```bash
        git push origin <tagname>
        ```
1. To show all tags and check if your tag is successfully created, run:
        ```bash
        git tag -l
        ```


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
    
    1. Ensure local copy of both `main` and `release_branch` are up to date.
    ```bash
    git checkout main
    git pull main
    git checkout vX.Y_release
    git pull checkout vX.Y_release
    ```

    1. On the main branch use
    ```bash
    git cherry-pick -n <hash_of_the_commit_of_the_release_notes_from_the_release_branch>
    ```
    to pull in just the `CHANGES.md` updates with release notes. Commit them.

=== "Using merge"
    
    If you are unable to use the cherry-pick for the changes then the following may be useful.
    
    - [x] `git merge` the release branch into the trunk e.g., `git merge v3.1_release --no-commit`
    - [x] Inspect the differences in the local copy of the main branch
    - [x] Revert any changes other than to the `CHANGES.md` file
    - [x] Commit and push changes to the main branch.


## Create a Release on GitHub

Create a release on github from the tag and make sure to include all major release notes.

Create a discussion announcement from the release.

!!! info
    Github has a good documentation about release processes, see: [Managing releases - GitHub Docs](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository)

!!! note
    There will be a box asking you to "attach binaries by dropping them here". This can be ignored. The binaries/assets will be generated automatically.


## Update Release Version on CDDS-simulation-metadata

!!! Note
    A release must be created on CDDS GitHub before doing the following.

Each time a new CDDS release is created, the front page of [CDDS-simulation-metadata](https://github.com/UKNCSP/CDDS-simulation-metadata) must be updated to ensure that it remains synchronised with [CDDS](https://github.com/MetOffice/CDDS).

1. Navigate to the actions tab of [CDDS-simulation-metadata](https://github.com/UKNCSP/CDDS-simulation-metadata/actions)

2. In the "workflows" sidebar on the left side of the page, select the [Update mappings](https://github.com/UKNCSP/CDDS-simulation-metadata/actions/workflows/update_mappings.yml) workflow.

3. Select the "run workflow" button on the top right hand side of the screen. Set the "use workflow from" dropdown menu to "main" if not done so automatically. Enter the most recent mappings tag as shown on [CDDS-CMIP7-mappings](https://github.com/UKNCSP/CDDS-CMIP7-mappings/releases) (this may be in the form `vYYY-MM-DD` OR `CDDS-vX-Y-Z`) and hit "Run workflow" at the bottom right of the page. This tag must be written exactly as it is shown on [CDDS-CMIP7-mappings](https://github.com/UKNCSP/CDDS-CMIP7-mappings/releases) otherwise the action will fail.
!!! note
    The above step must be completed even if the "current mappings file version" at the top of the readme.md on [CDDS-simulation-metadata](https://github.com/UKNCSP/CDDS-simulation-metadata) already matches the most recent tag on [CDDS-CMIP7-mappings](https://github.com/UKNCSP/CDDS-CMIP7-mappings/releases).

4. Confirm the action has completed successfully.

!!! important
    Do not attempt to manually update the readme.md by hand. This readme.md draws from a template in the repository that is populated within the `Update mappings` action: any manual updates will ultimately be lost/overwritten when the action is re run.

## Close Issue

1. Finally, close the release gh-issue once the installation has also been completed on JASMIN.

!!!important
    **Do not delete the release branch! (unless Matthew Mizielinski told you to)**
