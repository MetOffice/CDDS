!!! warning

    This documentation is currently under construction and may not be up to date.

## Python Code

### Style Guide
* Use the [Style Guide for Python Code](http://www.python.org/dev/peps/pep-0008)
    * Exception - Limit all lines to a maximum of 120 characters for docstrings and comments. (79 in the the PEP 8 guidelines ([reference](https://peps.python.org/pep-0008/#maximum-line-length))).
- All `CDDS` packages should contain a `package_name/package_name/tests/test_coding_standards.py` module that uses the [pycodestyle](https://pycodestyle.pycqa.org/en/latest/) package to check PEP 8 conformance.
- In addition to this, it is recommended to use a tool that checks for errors in Python code, coding standard (e.g., PEP 8) conformance and general code quality e.g., [pylint](http://www.pylint.org/).
    * However, some [PEP 8](http://www.python.org/dev/peps/pep-0008) guidelines are not checked by these tools; please also:
    * Be consistent within a module or function ([reference](https://peps.python.org/pep-0008/#a-foolish-consistency-is-the-hobgoblin-of-little-minds)).
    * In Python, single-quoted strings and double-quoted strings are the same; pick a rule and stick to it ([reference](https://peps.python.org/pep-0008/#string-quotes)).
    * Use Python's implied line continuation inside parentheses, brackets and braces to wrap long lines, rather than using a backslash 
    * Add a new line before a binary operator, rather than after ([reference](https://peps.python.org/pep-0008/#should-a-line-break-before-or-after-a-binary-operator)).
    * Use blank lines in functions, sparingly, to indicate logical sections ([reference](https://peps.python.org/pep-0008/#blank-lines)).
    * Always use double quote characters for triple-quoted strings """ to be consistent with the docstring conventions in PEP 257 and PEP 8.
    * Write comments using complete sentences ([reference](https://peps.python.org/pep-0008/#comments)).
    * Use the [`str.format()`](https://docs.python.org/3.8/library/stdtypes.html#str.format) method to perform a string formatting operation, e.g., `'Coordinates: {latitude}, {longitude}'.format(latitude='37.24N', longitude='-115.81W')`, i.e. avoid using the `%` operator on strings.
    * Include the line `(c) British Crown Copyright [year of creation in the form <YYYY>]-[year of last modification in the form <YYYY>], Met Office.` as a comment at the top of every module.

### Naming Conventions
- Abstract Base Classes should have a name that contains Abstract for clarity.
- Nouns should be used when naming classes.
- Use descriptive names that clearly convey a meaning; refrain from using overly general / ambiguous names e.g., data.
- Use the `.cfg` extension for configuration files, e.g. those read by configparser.

### Imports
- Use [absolute imports](https://www.python.org/dev/peps/pep-0328/#rationale-for-absolute-imports) as they are recommended by PEP 8. Also, being able to tell immediately where the function comes from greatly improves code readability and comprehension (Readability Counts). Example:
  - `import my_package.my_subpackage.my_module` and use the `my_module.my_function syntax`, e.g., `import os; os.walk`.
  - `from my_package.my_subpackage.my_module import my_function` and use `my_function` directly.
- group imports, with a blank line between each group, in the following order: standard library imports, related third party imports, local application/library specific imports ([reference needed]()).
- Within each import group (see above), order the imports alphabetically.
- place module level "dunders" after the module docstring but before any import statements except `from __future__ imports` ([reference needed]()).
- Use the pattern `import numpy as np`.

### Typing
- Use [typing](https://docs.python.org/3/library/typing.html) for adding type hints and annotations.
- Use [mypy](https://mypy.readthedocs.io/en/stable/) for running static code analysis using aforementioned type hints.

### Docstrings

!!! warning

    Historically CDDS used several different doc string formats so there is a mix of styles. If in doubt use the same format as the module 

    as of 2022 the PEP-257 format was adopted.
    This means there is currently a mix of docstring formats used
    throughout the `CDDS` code.

- Docstrings should now be written using [NumPy](https://numpy.org/doc/1.19/docs/howto_document.html).
- A detailed example of NumPy style docstrings can be found [here](https://numpy.org/doc/1.19/docs/howto_document.html)
    - Use double backticks `` around argument names 
    - Use the appropriate substitutions for glossary terms.
    - Make use of the [docstring conventions](http://www.python.org/dev/peps/pep-0257).
    - The docstring is a phrase ending in a period and prescribes the function or method's effect as a command, not as a description [reference needed]().
- It is not necessary to write docstrings for non-public classes, methods and functions, see `cdds/pylintrc` and `mip_convert/pylintrc`. (The maintenance overhead is reduced when refactoring non-public classes, methods and functions).

Below is an example NumPy Docstring Example docstring incorporating all of the guidelines above.

```python
def my_function(my_param1: float, my_param2: str) -> int:
    """
    Return something.

    Here's a longer description about the something that is returned.
    It's so long, it goes over one line!

    Parameters
    ----------
    my_param1: float
        Description of the first parameter ``my_param1``.
    my_param2: string
        Description of the second parameter ``my_param2``.

    Returns
    -------
    int
        Description of anonymous integer return value.

    Raises
    ------
    ValueError
        If ``my_param1`` is less than 0.
    """
```

## Doctest
- [Doctests](https://docs.python.org/3.8/library/doctest.html) have been included historically in MIP Convert and CDDS, but we recommend adding code to test modules instead

## Entry Point Scripts
- Script names should not have an extension, should be lowercase, and with words separated by underscores as necessary to improve readability, e.g., just_do_it.
- It is recommended that scripts call a main() function located in an importable module so that it is possible to run the code in the script from the Python interpreter / a test module e.g., `import my_module; my_module.main()`.
- [Argparse](https://docs.python.org/3.8/library/argparse.html) should be used to parse command line options.

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
- Use the [Google Styleguide](https://google.github.io/styleguide/shellguide.html) for bash scripts as recommended by the [Cylc documentation](https://cylc.github.io/cylc-doc/stable/html/workflow-design-guide/general-principles.html#coding-standards)
- Run scripts through [Shellcheck](https://www.shellcheck.net/) for catching possible bad practice. (The latest version can be installed using conda for easier access and improvements over the centrally installed version)
