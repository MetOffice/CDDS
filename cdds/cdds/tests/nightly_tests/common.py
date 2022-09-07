# (C) British Crown Copyright 2021, Met Office.
# Please see LICENSE.rst for license details.
import os


def makedirs(path):
    """
    Creates the dictionaries recursively for the given path if they do not exist.

    Parameters
    ----------
    path: :str
        Path to the dictionary (and it's parent) that should be created.
    """
    if not os.path.exists(path):
        os.makedirs(path)


class NameListFilter:
    """
    Class storing filter functions for a namelist in a Rose configuration
    """

    @classmethod
    def enabled(cls, name_list_item):
        """
        Filters all items that have a property `enabled` and that
        property value is `true`

        Parameters
        ----------
        name_list_item: :dict
            Current item of a name list

        Returns
        -------
        :bool
            Indicates if the item's property `enabled` is set to `true`
        """
        return name_list_item['enabled'].lower() == 'true'

    @classmethod
    def task_suite(cls, name_list_item, task_package):
        """
        Filters all items that property `enabled` is true and the property
        `test_package` equals to the given task package.

        Parameters
        ----------
        name_list_item: :dict
            Current item of a name list

        task_package: str
            The current cylc task package

        Returns
        -------
        :bool
            Indicates if the item matches the conditions or not
        """
        return cls.enabled(name_list_item) and name_list_item['test_package'] == task_package
