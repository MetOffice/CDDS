!!! warning

    This documentation is currently under construction and may not be up to date.

Pytest is the testing framework used in `CDDS`.
It currently serves two main functions.

1. It acts as the testrunner, whereby it collects all the tests and executes them.
1. It is a unit testing library.

The version of `pytest` currently used within `cdds` is 7.1.2

- Link to the [pytest 7.1.x Documentation](https://docs.pytest.org/en/7.1.x/contents.html) 
- Link to the [pytest 7.1.x API](https://docs.pytest.org/en/7.1.x/reference/reference.html)

## Pytest Configuration

```cfg
[tool:pytest]
python_files = test_*.py
python_functions = test_*
console_output_style = progress
addopts = -m 'not slow and not integration and not rabbitMQ and not data_request'
markers =
    slow
    rabbitMQ
    data_request
    integration
    style
```

## Running pytest

CDDS already provides a script to run all tests via pytest:

Activate the conda environment:
```bash
source setup_env_for_devel
```

Run the run_all_tests script:

```bash
./run_all_tests
```

The script runs all unit tests including all integration and slow tests.
It does not run the RabbitMQ tests!
Tests failures will be logged in the cdds_test_failures.log file.

Run RabbitMQ tests
The RabbitMQ tests needs a proper RabbitMQ installation. Only, the server els055 and els056 have RabbitMQ properly installed for CDDS. 

RabbitMQ needs credentials that are specified in your home directory $HOME/.cdds_credentials and has following content:

```cfg
[rabbit]
host = <hostname>
port = <port number>
userid = <user id>
use_plain = true
vhost = dds_dev
password = <password>
For the correct values of the fields, please contact @Matthew Mizielinski .
```

Connect to one of the servers via ssh, e.g:

```bash
ssh els055
```

Go to your workspace directory for CDDS. (the same as on your local VM)

Activate the conda environment:

```bash
source setup_env_for_devel
```

Run the test script:

```bash
./run_rabbitmq_tests
```

Any test failures will be recorded in the cdds_rabbitmq_test_failures.log file.

Run single tests
Run all tests in a specific package

```bash
pytest -s <package-folder>
```

For example: run all tests in mip_convert:

```bash
pytest -s mip_convert
``` 

Run all tests in a specific module

```bash
pytest <test_module.py>
```

For example: Run tests in test_coding_standards.py:

```bash
pytest test_coding_standards.py
```

Run specific test in a TestCase class

One option is to us `-k`.
The `-k` command line option to specify an expression which implements a sub-string match on the test names:


```bash
pytest <test_module.py> -k <TestClass>
```

For example run all tests implemented in TestLoadCmipPlugin class in the module test_plugin_loader:

```bash
pytest test_plugin_loader.py -k TestLoadCmipPlugin
```

Additional, you can also use Node IDs to run all tests of a specific class. How to do this, see next section.

Run specific test
To run a specific test, pytest use Node IDs that is assigned to each collected test and which consists of the module filename followed by specifiers like class names, function names and parameters from parametrization separated by :: characters. 

A specific test implemented in a specific TestClass can be run by using

```bash
pytest <test_module.py>::<TestClass>::<test_method>
```

For example, run the test test_load_cdds_plugin in the module test_plugin_loader.py:

```bash
pytest test_plugin_loader.py::TestLoadPlugin::test_load_cdds_plugin
```

Node IDs are of the form module.py::class::method or module.py::function. Node IDs control which tests are collected, so module.py::class will select all test methods on the class. 


## Useful Command Line Options

There are many other options that can be used to configure pytest.

| Option             | Description                          |
| ------------------ | ------------------------------------ |
| `-h`               | show help message and configuration info  |
| `-k <expression>`  | only run tests which match the given substring expression |
| `-v`               | increase verbosity |
| `--no-summary`     | disable summary |
| `-r <chars>`       | show extra text summary info as specified by chars: (f)ailded, (E)rror, (s)kipped, (x)failed, (X)passed, (p)assed, (P)assed with output, (a)ll excepted passed (p/P), or (A)ll. (w)arnings are enabled by default. |
| `--disable-warnings` | disable warnings summary |
| `--tb=<style>`     | traceback print mode (auto/long/short/line/native/ no) |
| `-c <file>`        | load configuration from <file> |
| `--collect-only`   | only collect tests, don’t execute them |
| `--debug=[DEBUG_FILE_NAME]` | store internal tracing debug information in this log file. Default is pytestdebug.log |


## Pytest Annotations

Annotation

Description

Link

```python
@pytest.mark.skip(message)
```

Skip an executing test with the given message.

```python
@pytest.mark.parametrize(input_parameter, test_data)
```

It allows one to define multiple sets of arguments and fixtures at the test function or class.

Parametrizing fixtures and test functions — pytest documentation 


## Using nosetests attributes

We still use the nosetests attributes to specify slow tests, integration tests, etc. These attributes can still be used because of pytest-attrib 
Test can be run with an -a option:

```bash
pytest -a slow
```
This runs all slow tests.
If you want to not run the slow tests, you can do this as followed:

```bash
pytest -a "not slow"
```

The expression given in the -a argument can be even more complex, for example:

```bash
pytest -a "slow and integration"
```

## Plugins

Pytest has a large plugin ecosystem.

### pytest-cov

Usage.