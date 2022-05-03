README

This folder contains four bash files for running tests on the CDDS packages. 

run_tests_all                  Run all test attributes including the doctests for the given packages.
run_tests_all_no_doctest       Run all test attributes excluding the doctests for the given packages.
run_tests_code_style           Run only the `style` tests for the given packages.
run_tests_quick                Run only the quick running tests and the doctests for the given packages.


SCRIPT USAGE

All four scripts will by default use the CDDS_PACKAGES environment variable unless a user specified list of packages is given as arguments to the script.

For example | $ ./run_tests_all | will run for all tests for all packages.

Or alternatively | $ ./run_tests_all cdds_prepare | would run all tests for just cdds_prepare.


BACKGROUND

These were created with the intention of being able to run certain attributes individually across all packages, as well as introducing the ability to run the tests on an installed version of the CDDS software.
Because the Py2 to Py3 migration may introduce breaking changes to the tests and test runner, these scripts are being shelved for now.
Once the existing tests have been migrated these scripts can be looked at again, and also finishing the functionality they were intended to bring.
For more context on the intended changes please see tickets #1529, #1489, and #1748.
