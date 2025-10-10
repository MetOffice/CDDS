!!! warning

    This documentation is currently under construction and may not be up to date.

The `cdds.convert` component designed to check out, configure and run a copy of the suite, specified in the config.
Suite ​u-ak283 is currently set up for this purpose.

## Development workflow

To work on suite developments please follow the standard practices set out in the Development Workflow and use the --rose-suite-branch argument to cdds_convert to point at the branch you wish to use when running.

## Release procedure
Create a branch named cdds_<release number>, e.g. cdds_1.0.0 of the suite and make the change shown in changeset of the rose suite u-ak283.

Create a branch the config and modify the rose_suite_branch settings, e.g. to cdds_1.0.0@100752 if revision 100752 is appropriate, in the [convert] section of CMIP6.cfg. If a different suite id is being used then the rose_suite setting will also need altering.

Review config branch as per standard practises, merge to trunk and update config checkout on disk under the cdds account.