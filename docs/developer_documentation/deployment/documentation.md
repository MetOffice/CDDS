# Documentation

CDDS uses an `X.Y.Z` versioning system for releases but for documentation we only publish the most recent bugfix release. For example, we would publish `1.0.0` as `1.0` and any following bugfix releases e.g., `1.0.1` would overwrite that existing `1.0` deployment.

It is also not necessary to only publish the documentation as part of the release process.
If documentation needs to be added or corrected this can be done independently of a release, as long as it does not reference any change or functionality that has not yet been released.

## Deployment Procedure

1. Checkout the required release branch for deployment.
   ```bash
   git checkout vX.Y_release
   ```
2. Confirm the branch is up to date.
   ```bash
   git pull
   ```
3. Active the CDDS environment.
   ```bash
   source setup_env_for_devel
   ```
4. Inspect the current list of deployed versions.
  ```bash
  mike list 
  ```
1. Deploy the new/updated version of the documentation. (This command should overwrite any existing existing deployments with the same name.)
   ```bash
   mike deploy X.Y
   ```
2. Verify the new deployment works as expected.
   ```bash
   mike serve
   ```
3. Push the local commit made by `mike` to the `gh-pages` branch to github.
   ```bash
   git push origin gh-pages
   ```
