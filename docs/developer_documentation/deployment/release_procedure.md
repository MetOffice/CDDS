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
```

??? example

    ```bash
    git checkout v3.2_release
    git checkout -b 123_v3.2.1_release
    ```


## Prepare the Deployment Branch

Each of these steps should be made as separate commits to allow for cherry picking the `CHANGES.md` on to `main`.

1. Update the `_DEV` flag in `cdds/cdds/__init__.py` and `mip_covert/mip_convert/__init__.py` to `False`
    ```bash
    sed -i "s/_DEV = True/_DEV = False/" */*/__init__.py
    ```

2. Check that `_NUMERICAL_VERSION` in `cdds/cdds/__init__.py` and `mip_covert/mip_convert/__init__.py` matches the release `X.Y.Z` you are preparing.
      It should be set to the current release version e.g. `3.1.0` (This must include any suffixes e.g. for
      release candidates)

3. Update the `CHANGES.md` files with all the relevant changes from the last release.
    - Any new files added since the last release that do not have a `.py` extension are included in `MANIFEST.in` and `setup.py`.


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
For more information, see [Documentation](documentation.md). If you have any doubts, please speak to Jared or Matthew.


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

    1. On the main branch use the `git cherry-pick` command to pull in just the `CHANGES.md` updates with release notes and commit them.

=== "Using merge"
    
    If you are unable to use the cherry-pick for the changes then the following may be useful.
    
    - [x] `git merge` the release branch into the trunk e.g., `git merge v3.1_release --no-commit`
    - [x] Inspect the differences in the local copy of the main branch
    - [x] Revert any changes other than to the `CHANGES.md` file
    - [x] Commit and push changes to the main branch.


## Create a Release on GitHub

Create a release on github from the tag. Include all major release notes and ensure that all links back to Jira work as expected. 
Create a discussion announcement from the release.

!!! info
    Github has a good documentation about release processes, see: [Managing releases - GitHub Docs](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository)


## Close Issue

1. Finally, close the release gh-issue.

!!!important
    **Do not delete the release branch! (expect Matthew Mizielinski told you so)**
