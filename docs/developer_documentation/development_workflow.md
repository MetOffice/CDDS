!!! warning

    This documentation is currently under construction and may not be up to date.

## Create a Github Issue

Each change should be described in a Github issue.
Before submitting an issue, make sure that the issue explains the purpose of the changes and what changes should be done.
New issues will be reviewed by the development team at daily stand ups to identify reviewer and release target. These will be added to the todo status on the corresponding project board (only for use by CDDS developers)
Before creating a new issue, look through the current issues and milestones to confirm that it doesn't already exist.

## Start Working on an Issue

- Assign the issue to yourself
- Move the issue to in progress in the corresponding project board
- Create a new branch for the issue

### Create a New Branch

#### Create a new branch for an issue

Identify where your new branch should start from, e.g. is this for an update going into the next bug fix or is this targetted at the next minor version of CDDS.
For a bugfix ensure that you are working off the corresponding release branch, e.g

```bash
git switch v3.2_release
```
while for a larger developments switch to `main`.

The branch name should be start with the issue number and has a brief description of the task.
Use underscores in the branch name to separate words.

```bash
git checkout -b <issue_number>_<brief_description>
```

The commit message should be:

```
<issue_number>: Create a new branch for <brief_description>
```

Don’t wrap the line of the commit message and don’t use more than 72 characters.
If you need a longer commit message.
Leave one empty line after the first line and then give a more detailed description (now you can wrap this description).
After creating the branch, your working copy is already on this branch (provided you used the `-b` option).



### Code

- Modify the code on the “issue“ branch

- Regularly, commit your changes locally and remotely using:

The commit messages should always start with the issue number and have a short description what changed.

Be aware, that the requirements for commit message are:

Not more than 72 characters per line

The first line should start with the issue number and have a really short brief description

If more descriptions are necessary, leave an empty line and then write more text, e.g.

```
Issue #109 Merge fixing duplicate coordinates error from cmor
* Add functional tests for ARISE model
* Simplify mean cube calculation
```

Push changes to github using

```bash
git push origin
```

To be more explicit, you can add the branch name you want to commit to:

```bash
git push origin <branch_name_to_commit_to>
```

### Tests

Make sure that unit tests covers your code changes and pass! the `run_all_tests` script at the root of the repository should take around 10-15 minutes to run all tests, but commands such as `pytest cdds` can be used during development.

Any changes in the submission code (check with CDDS team) should be done with extreme care and frequent testing.

It is a good approach to ensure that every time you push a commit to the repository that the tests pass successfully.

### Documentation

- Document your code. Try to be short but precise.
- Briefly describe the work on the Github issue

## Reviews

1. For coding reviews, we use the pull requests functionality of Github
1. Go to Github and the pull requests for the cdds-project: https://github.com/MetOffice/cdds/pulls
    1. Click on New pull request (green box on the right)
    1. Choose as base branch the branch you branched from (often: main or one of the release branches)
    1. Choose your branch as the  compare branch 
    1. Click on Create pull request
    1. Describe the change, reference the issue and add  other useful information for the reviewers
    1. Reference your PR from the issue.
1. Put your issue into Review
1. Assign it to the main reviewer
1. Mention in the team channel that the issue is now ready to review. So, everyone has the change to review your changes.
1. You need at least an approved of the main review before merging the issue

1. If you need to do any changes, assign the issue back to you and put it back into In progress.
1. If the main reviewer is happy with the changes and no comments or issues are needed to addressed anymore, the issue will moved to Approved and re-assigned to you. Now, you can merge your changes

## Merge changes
You have two possibilities how to merge a branch - via command line or using Github. Where possible please merge using github and use "squash and merge".

### Merge to parent branch

#### Via Command Line

Go to the parent branch to merge to (normally: main or the release branch)

```bash
git checkout <branch_to_merge_to>
```

Make sure that the branch is up-to-date:

```bash
git pull
```

Merge the issue branch:

```bash
git merge <your_branch_to_merge>
```

As commit message for a merge use:

```bash
<issue-number>: Completed work to <short_brief_description_of_task>
```

You could face merging conflicts that you need to solve before you can end the merge.

#### Using Github

1. Go to the `Pull Requests` view of your branch in Github
1. If your review is approved, there is a green `Merge Branch` button at the bottom of the page. Click on it.
    1. If the this button does not appear or is not clickable, check if your review is really approved and if there is no conflicts you need to solved first.
    1. For solving conflicts, Github provides you help with a UI tool

1. remove branch if working on `main`

### Cherry pick changes to main branch (or any other branches)

If your parent branch is a release branch, you also need to merge the changes into the main branch. Therefore, cherry picking is the best to do. You can do this after merging your changes into the release branch.

Cherry picking into other branches are following the same pattern!

#### Via Command Line

Find the commit id of the merge commit into the parent branch, you have done in the previous step:

Go to the parent branch

```bash
git checkout <parent-branch>
```

Find your commit ID:

```bash
git log
```

This list all the previous commits in decreasing order. Each merge entry looks like:


```
commit <commit-id> (<merge-branches>)
Merge: <merge-ids>
Author: <author-details>
Date:   <timestamp>
<commit-message>
Use the <commit-id> of your merge commit.
```

Remember your <commit-id>! You will need it for the next steps.

Do the cherry pick:

Go to the branch you want to cherry-pick to:


```bash
git checkout <branch-to-cherry-pick-to>
```

Cherry pick:

```bash
git cherry-pick <commit-id> --no-commit
```

This will add the commit’s changes to your working copy without directly committing them. You need to do a git commit by yourself.

Commit the changes and check if everything is fine:

Check the changes. If they are fine, commit them:

```bash
git commit
```

Use the key-word cherry-pick in your commit message to make clear that this commit is a cherry-pick.

Check if all (unit) tests succeed!

Push the changes 

#### Using Github

For using cherry-picking, see Cherry-picking a commit in GitHub Desktop - GitHub Docs 

## tidy up

Please delete your branches from github once they are no longer needed.
