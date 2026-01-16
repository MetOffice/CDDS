!!! warning

    This documentation is currently under construction and may not be up to date.

1. Create a test class (pattern: test_<project_id>_<mip_table>_<variable>) in mip_convert.tests.test_functional.<project_id>.

1. Import the functional tests class for MIP convert tests

    ```python
    from mip_convert.tests.test_functional.test_command_line import AbstractFunctionalTests
    ```

1. Extends your test class from the `AbstractFuntionalTests`

1. Implement the `get_test_data` function:
    1. The function should return the test data as an TestData object (e.g. Cmip6TestData or AriseTestData)
    1. The available TestData objects are in  mip_convert.tests.test_functional.utils.configurations
    1. Specify the necessary individual values of the TestData object (like mip_table, variable, specific_info, etc.)
    1. For examples, see tests in  mip_covert/tests/test_functional

1. Implement your test method that runs check_convert.
This function will trigger MIP convert with your given test data. 
1. Mark your test as a slow test by add following annotation to your test method

    ```python
    @pytest.mark.slow
    ```

!!! note

    For debugging a MIP convert functional test, remove the slow annotation of the test. Afterwards you can run the test as usual in your IDE.
