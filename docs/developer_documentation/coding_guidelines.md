!!! warning

    This documentation is currently under construction.

# Coding Guidelines

## Code Style
* Use the "Style Guide for Python Code" http://www.python.org/dev/peps/pep-0008.
* CDDS packages should contain a package_name/package_name/tests/test_coding_standards.py module that uses the https://pypi.python.org/pypi/pep8 package to check PEP 8 conformance.
* In addition to this, it is recommended to use a tool that checks for errors in Python code, coding standard (e.g., PEP 8) conformance and general code quality e.g., http://www.pylint.org/.
* However, some http://www.python.org/dev/peps/pep-0008 guidelines are not checked by these tools; please also:
* Be consistent within a module or function [reference].
* In Python, single-quoted strings and double-quoted strings are the same; pick a rule and stick to it [reference].
* Limit all lines to a maximum of 120 characters and ?? for docstrings and comments. (Originally this was 79 as per the PEP 8 guidelines [reference]).
* Use Python's implied line continuation inside parentheses, brackets and braces to wrap long lines, rather than using a backslash [reference].
* Add a new line before a binary operator, rather than after [reference].
* Use blank lines in functions, sparingly, to indicate logical sections [reference].
* Always use double quote characters for triple-quoted strings """ to be consistent with the docstring conventions in PEP 257 and PEP 8.
* Write comments using complete sentences [reference].
* Use the https://docs.python.org/3.8/library/stdtypes.html#str.format str.format() method to perform a string formatting operation, e.g., 'Coordinates: {latitude}, {longitude}'.format(latitude='37.24N', longitude='-115.81W'), since it is the new standard in Python 3 and is preferred to the % formatting.
* Include the line (c) British Crown Copyright [year of creation in the form <YYYY>]-[year of last modification in the form <YYYY>], Met Office. as a comment at the top of every module.

## Imports
* Use absolute imports https://www.python.org/dev/peps/pep-0328/#rationale-for-absolute-imports as they are recommended by PEP 8. Also, being able to tell immediately where the function comes from greatly improves code readability and comprehension (Readability Counts). Example:
o import my_package.my_subpackage.my_module and use the my_module.my_function syntax, e.g., import os; os.walk.
o from my_package.my_subpackage.my_module import my_function and use my_function directly.
* group imports, with a blank line between each group, in the following order: standard library imports, related third party imports, local application/library specific imports [reference].
* Within each import group (see above), order the imports alphabetically.
* place module level "dunders" after the module docstring but before any import statements except from __future__ imports [reference].
* Use the pattern import numpy as np.

## Naming Conventions
* Abstract Base Classes should have a name that contains Abstract for clarity.
* Nouns should be used when naming classes.
* Use descriptive names that clearly convey a meaning; refrain from using overly general / ambiguous names e.g., data.
* Use the .cfg extension for configuration files, e.g. those read by configparser.

## Typing
* Use https://docs.python.org/3/library/typing.html for adding type hints and annotations.
* Use https://mypy.readthedocs.io/en/stable/ for running static code analysis using aforementioned type hints.

## Docstrings

!!! warning

    Historically CDDS used the NumpyDoc format for all docstrings.
    As of 2022 the pep-257 was adopted.
    This means there is a mix of docstrings formats used. 



* Docstrings should now be written using https://docutils.sourceforge.io/rst.html as recommended by https://www.python.org/dev/peps/pep-0287/, and is rendered using Sphinx.
* An detailed example of the reStructuredText style docstrings can be found here https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html
o Use double backticks `` around argument names so that they are rendered as code in the HTML produced by Sphinx
o Use the appropriate substitutions for glossary terms.
o Make use of the docstring conventions http://www.python.org/dev/peps/pep-0257.
o The docstring is a phrase ending in a period and prescribes the function or method's effect as a command, not as a description [reference].
* It is not necessary to write docstrings for non-public classes, methods and functions, see cdds/pylintrc and mip_convert/pylintrc. (The maintenance overhead is reduced when refactoring non-public classes, methods and functions).
reStructuredText Docstring Example
Below is an example docstring incorporating all of the guidelines above.

```python
def my_function(my_param1: float, my_param2: str) -> int:
    """
    Return something.

    Here's a longer description about the something that is returned.
    It's so long, it goes over one line!

    :param my_param1: Description of the first parameter ``my_param1``.
    :type my_param1: float
    :param my_param2: Description of the second parameter ``my_param2``.
    :type my_param2: string
    :raises ValueError If ``my_param1`` is less than 0.
    :return: Description of anonymous integer return value.
    :rtype: int
    """
```

## Doctests
* Where appropriate, a https://docs.python.org/3.8/library/doctest.html should be included in an Examples section of the docstring https://numpydoc.readthedocs.io/en/latest/format.html#docstring-standard.
* When multiple examples are provided, they should be separated by blank lines. Comments explaining the examples should have blank lines both above and below them.
Scripts
* Script names should not have an extension, should be lowercase, and with words separated by underscores as necessary to improve readability, e.g., just_do_it.
* It is recommended that scripts call a main() function located in an importable module so that it is possible to run the code in the script from the Python interpreter / a test module e.g., import my_module; my_module.main().
* https://docs.python.org/3.8/library/argparse.html should be used to parse command line options.

```python
def main(args):
    # Parse the arguments.
    args = parse_args(args)

    # Create the configured logger.
    configure_logger(args.log_name, args.log_level, args.append_log)

    # Retrieve the logger.
    logger = logging.getLogger(__name__)

    try:
        exit_code = my_func(args)
    except BaseException as exc:
        exit_code = 1
        logger.exception(exc)

    return exit_code
```

## Bash Scripts
* Use the Google https://google.github.io/styleguide/shellguide.html for bash scripts, as recommended by the Cylc documentation https://cylc.github.io/cylc-doc/stable/html/workflow-design-guide/general-principles.html#coding-standards
* Run scripts through https://www.shellcheck.net/ for catching possible bad practice. (The latest version can be installed using conda for easier access and improvements over the centrally installed version)
