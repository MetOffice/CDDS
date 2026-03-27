!!! warning

    This documentation is currently under construction and may not be up to date.

## Modifying and Building the CDDS Documentation

This page gives an overview of the general philosophy of the CDDS documentation.
The current documentation is based upon `mkdocs` and is built and managed using two main packages.

1. `mkdocs-material` - A particular `mkdocs` theme which also extends the base functionality.
2. `mike` - A tool for managing multiple independent versions of documentation on a particular branch.

For most purposes it is only neccessary to reference the `mkdocs-material` package documentation and the mike documentation.


## Working with `mkdocs`

The source files are written in markdown, and are kept in the `docs` directory of the repository.
Configuration of the building of mkdocs is done using the `mkdocs.yml` file.

Whilst editing or adding documentation you can preview changes in realtime using by starting a local server.

```
mkdocs serve
```

To generate the actual site that can be uploaded to a web server you would use.

```
mkdocs build
```

However, it should not be needed to run this command directly in order to build and deploy the docs.
This is done using the `mike` package (see next section).


## Working with `mike`

It is worth familiarising with the overview of `mike` here.
In short though, `mike` makes it relatively straightforward to manage multiple versions of docs by running the `mkdocs build` command and automatically commiting this to the `gh-pages` branch.

```
mike deploy 3.0
```

Similarly to `mkdocs serve`, you can use the following command to start a local server to preview the docs.

```
mike serve
```

However, rather than displaying the docs in your `CWD`, this will serve the docs from the `gh-pages` branch.


## Managing Versions and Deployment in Practice


### Documentation Versioning Policy

CDDS uses an `X.Y.Z` versioning system for releases, but for documentation, only the most recent bugfix release is published. For example, `1.0.0` is published as `1.0`, and any following bugfix releases (e.g., `1.0.1`) overwrite the existing `1.0` deployment.

Documentation can be published independently of the release process, as long as it does not reference unreleased changes or functionality.

### How to Set the Latest Version

The default documentation version shown should always be the latest major release (e.g., `3.1`). If you need to change this, update the default version as follows:

1. Deploy the newest documentation as the default:
    ```bash
    mike deploy X.Y latest --update-aliases
    ```
    where `X.Y` is the version to set as default (e.g., `3.1`).
2. Verify the default documentation is set as expected:
    ```bash
    mike serve
    ```
3. Push the local commit by `mike` to the `gh-pages` branch:
    ```bash
    git push origin gh-pages
    ```
