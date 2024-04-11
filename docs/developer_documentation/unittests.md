## Running Unit Tests

The CDDS code base includes a comprehensive set of unit and integration tests covering mode of the source code. Tests can be run in several ways.

1. Start by navigating to the root directory of the CDDS source code.
2. Ensure the development environment is correctly setup by running:

```bash
source setup_env_for_devel
```
Then, you can run on of the following commands to run tests:

Run all tests on SPICE: 

```bash
sbatch submit_run_all_tests.batch
```

Run all tests locally:

```bash
./run_all_tests
```

Run tests for a particular package `cdds` 

```bash
pytest cdds
pytest mip_convert
```

Run tests for a particular test module:

```bash
py.test hadsdk/hadsdk/tests/test_common.py
```

## Writing Unit Tests

On some occasions Coding Guidelines WIP | Doctests may be sufficient as unit tests.

!!! note "Location and naming conventions"

    Unit tests should be located in a parallel directory structure to the modules they are testing!

    For example: tests for the my_package/my_subpackage/my_module.py module should be located in the my_package/tests/my_subpackage/ directory in a test module with the name test_my_module.py

!!! note "Unit tests should not have docstrings."

    The log produced by pytest prints the name of the test in the form test_my_test_description (test_my_module.TestMyClass) if the test does not have a docstring, which is more helpful than the information that can fit into the first line of a docstring (which is printed if it exists).

    The pylint: disable = missing-docstring comment tells pylint not to warn about missing docstrings in the test module.

Unit Test Example

`my_module.py`

```python
# (C) British Crown Copyright 2015-2016, Met Office.
# Please see LICENSE.rst for license details.
"""
My module.
"""
def my_function():
    [...]
class MyClass():
    def my_method1(self):
        [...]
    def my_method2(self):
        [...]
```

`test_my_module.py`

```python
import unittest
class TestMyClass(unittest.TestCase):
    """
    Tests for MyClass in my_module.py.
    """
    def test_<class_test_description>(self):
        [...]
    def test_my_method1_<test_description>(self):
        [...]
    def test_my_method2_<test_description>(self):
        [...]
class TestMyFunction(unittest.TestCase):
    """
    Tests for my_function in my_module.py.
    """
    def test_<first_test_description>(self):
        [...]
    def test_<second_test_description>(self):
        [...]
if __name__ == '__main__':
    unittest.main()
```
