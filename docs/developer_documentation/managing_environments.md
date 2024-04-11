The following covers two particular aspects of managing conda environments.

1. Modification of dependencies in environment.yaml files.
1. Creation and naming of the conda development environments.

The changes are made to help

1. Eliminate the confusion when there are mismatches between a `cdds` version and cdds conda development environment name.
1. Prevent accidental creation of unsolvable environment.yaml files when merging from release branches into main or vice versa.
1. Avoid setup_env_for_devel script pointing to an environment that doesn't match that of the environment.yaml for any given commit.
1. Prevent having to modify existing installed cdds conda development environments.

## Modifying environment.yaml Files
If there are modifications to cdds needed that require a new environment then this should be managed in a consistent way. Examples of such changes could include

- a package version needs changing,
- new package(s) added
- old package(s) removed,
- a channel usage change

In the majority of cases, a change will normally be driven by a change to the cdds code base, so will have an existing JIRA issue. However, if this isn't the case then an issue should still be raised to cover any environment change (E.g. if a change to conda channels is needed but no package version changes thus no code changes are needed.). During the completion of the ticket in question, the process should be as follows. (This example assumes a new package is needed for new functionality within cdds and working on main)

Create a new conda environment for development work on this particular change.

This could be done on the cdds account, although modifying environments can sometimes be tricky.  Initially it would be better to do this on a user account first as this minimises the chance of accidentally modifying any existing cdds development environments. There are two approaches adding a package.

Update environment_dev.yaml specifying a particular version if this needed otherwise this can be left out and let the solver figure out the best version to use.

Create an environment using environment_dev.yaml and then install the package afterwards using conda install

Make the required code changes using this new environment e.g. add the new functionality that makes use of the new package.

When ready to create a pull request with these changes, create the next development environment on the cdds account using the correct naming convention cdds-X.X_dev-X 

Update setup_dev_env_for_development to point to the new environment on the cdds account.

Update the .yaml files based on what is in the installed version of cdds

Make sure all the tests are still passing.

By following this process it makes sure that

when the code changes are being reviewed the reviewer does not need to create their own environment.

the review will be using the actual environment that will be live once the PR is brought into main.

the existing development environment on main doesn't need to be modified in any way.

when the PR is brought into main the transition is seamless.

it is easy to remove the environment and start again if needs be based on feedback in the review without disrupting anything.

Adding a new environments should be fairly infrequent procedure, but make sure to be aware so when merging the PR back into 

By adhering to the above process, it should mean that the state of main is always consistent with the environment.yaml files it contains, and the setup script should also be always be pointing to the correct environment.  

Environment Changes on Bugfix Releases
If at all possible, changes to environments on bufix branches should be avoided as it will

increases the amount of work needed 

introduces more potential things to go wrong

Of course sometimes it is unavoidable so in such cases be aware of the following.

merging changes made to an enironment.yaml file on a release branch into main is almost always going to be a bad idea and increase the possibility of producing unsolvable environments unless the files are identical.

The normal practice of having a PR which brings changes from a dev branch (that branched from a release branch) into the release branch, and then cherry picking the squashed commit directly onto main may be a bad approach in this case.

I would suggest that when bringing such changes into main it would be better to create a new branch off of main, cherry pick the bugfix code changes onto branch but revert environment changes.

Managing Development Environments
Regarding point two, the naming conventions used for cdds development environments have been somewhat inconsistent and can at times lead to confusion. Here are a selection of cdds conda development environments.

```
cdds-2.1_dev-1
cdds-2.1_dev-1
cdds-2.3.2_dev
cdds-2.3_dev
cdds-2.4.0_dev
cdds-2.4.0_dev-1
cdds-2.4_dev_3
cdds-2.5.0_dev-1
```

A first step would be sticking with dev environments not being tied to specific hotfix versions. This is something that we have already done for some versions and not for others eg. 

Going forward I think it would be best to adopt the convention that does not reference a specific hotfix version such as (examples given for cdds version 2.5.0).

cdds-2.5_dev-0 or 

cdds-2.5.X_dev-0 (the X is not meant to be replaced)

This helps to avoid any confusion that can arise when there is a mismatch over the cdds version number specified in a given copy of cdds and the development environment that setup_env_for_development points to. Such situations can occur when there have been no updates to the environment for a period of time. It does not necessarily mean 

Additionally, particular attention should be paid to the change of version number on main following a maj/min release. This should be done immediately after the release.

Example
Here is a concrete example of the above starting from a 2.5.0 release.

The 2.5.0 release branch v2.5_release is created from main 

Update main by

Incrementing cdds version to 2.6.0

Creating a new environment called cdds-2.6_dev-0

Pointing setup_env_dev_for_development to this new cdds-2.6_dev-0 environment

As development proceeds on main over time new development environments are created in line with the practices described earlier in this document. E.g.

cdds-2.6_dev-1 - (change - added new package)

cdds-2.6_dev-2 - (change - added new package)

As development also proceeds on v2.5_release concurrently, and although it is not desirable, it may be necessary for a change to the environment. (For the purpose of this example we will assume the latest development environment was cdds-2.5_dev-1 when the v2.5_release branch was made.)

A new environment cdds-2.5_dev-2 is created for this change.

A new environment cdds-2.6_dev-3 is needed for development on main if this change needs to be brought over (this will almost always be the case).

When main reaches a state ready to release 2.6.0 the process continues as above.

The 2.6.0 release branch v2.6_release is created from main

Then update main by

Incrementing cdds version to 2.7.0

Creating a new environment called cdds-2.7_dev-0

Pointing setup_env_dev_for_development to cdds-2.7_dev-0

The resultant list of environments would look something like this.

```
cdds-2.5_dev-1
cdds-2.6_dev-0
cdds-2.6_dev-1
cdds-2.6_dev-2
cdds-2.5_dev-2
cdds-2.6_dev-3
cdds-2.7_dev-0
```

A downside of the above convention is that there will be a duplicated environment for every 2.X release which differs only in name. I.e, in the above example cdds-2.7_dev-0 and cdds-2.6_dev-3 should be exactly the same, aside from having different names. However, I think this an acceptable inefficiency for preventing confusion around environment versioning.

Conda Good to Know
When there are multiple channels defined in an environment.yaml there is an implicit priority based on their order, which if you are not aware of, conda may solve environments in ways you weren’t expecting.

See notes on --flexible_solve https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-channels.html#strict-channel-priority 

tldr flexible solve is the default and will prefer packages from higher priority channels even if there are more recent versions in other channels. 

Make use of mamba and the --dry-run option to speed your workflow up.

The same versioned package 