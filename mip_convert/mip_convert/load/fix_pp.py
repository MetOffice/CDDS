# (C) British Crown Copyright 2016-2021, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`load.fix_pp` module contains the code to fix any PP field
header elements that are incorrect.
"""
import logging

from hadsdk.common import compare_versions
from hadsdk.pp import PP_HEADER_CORRECTIONS
from mip_convert.common import get_field_attribute_name


def fix_pp_field(field):
    """
    Fix any PP field header elements in a PP field that are incorrect.

    :param field: the PP field
    :type field: :class:`iris.fileformats.pp.PPField`
    """
    for stash_codes, correction_info in list(PP_HEADER_CORRECTIONS.items()):
        if field.lbuser[3] in stash_codes:
            FixPPField(field, correction_info[0], correction_info[1]).fix()


class FixPPField(object):
    """
    Fix incorrect values of PP field header elements in a PP field.
    """

    def __init__(self, field, version_with_expression, correction):
        """
        The correction provided to the ``correction`` parameter is a
        tuple of ``(current_values, correct_values)`` tuples, where
        ``current_values`` and ``correct_values`` are dictionaries. The
        ``current_values`` dictionary contains the PP field header
        element names and values to be matched in the ``field``, while
        the ``correct_values`` dictionary contains the PP field header
        element names to be fixed and the correct values to use.

        :param field: the PP field
        :type field: :class:`iris.fileformats.pp.PPField`
        :param version_with_expression: the version of the UM for which
            the ``correction`` is valid
        :type version_with_expression: string
        :param correction: the correction to be applied
        :type correction: tuple of tuples containing a pair of
            dictionaries
        """
        self.logger = logging.getLogger(__name__)
        self._field = field
        self._version_with_expression = version_with_expression
        self._correction = correction

    def fix(self):
        """
        Fix incorrect values of PP field header elements in a PP field.
        """
        if self._is_fix_required:
            self._fix()

    @property
    def _is_fix_required(self):
        return compare_versions(self._version_to_compare, self._version_with_expression)

    @property
    def _version_to_compare(self):
        if (self._field.lbsrce % 10000) == 1111:
            um_major = (self._field.lbsrce // 10000) // 100
            if um_major != 0:
                um_minor = (self._field.lbsrce // 10000) % 100
                version = '{:d}.{:d}'.format(um_major, um_minor)
            else:
                # Pre UM Version 5.3.
                version = '5.3'
        return version

    def _fix(self):
        for (current_values, correct_values) in self._correction:
            if self._match_values(current_values):
                self._fix_pp_field_attributes(current_values, correct_values)

    def _match_values(self, header_elements_values):
        match = [
            self._field_attribute_value(header_element_name) == value
            for (header_element_name, value) in list(header_elements_values.items())
        ]
        return len(set(match)) == 1 and True in set(match)

    def _field_attribute_value(self, header_element_name):
        return getattr(self._field, self._field_attribute_name(header_element_name))

    def _field_attribute_name(self, header_element_name):
        return get_field_attribute_name(header_element_name)[0]

    def _item_position(self, header_element_name):
        return get_field_attribute_name(header_element_name)[1]

    def _fix_pp_field_attributes(self, current_values, correct_values):
        self.logger.debug('Fixing PP field header elements {msg}'.format(msg=self._log_message(current_values)))

        for header_element_name, correct_value in list(correct_values.items()):
            if self._item_position(header_element_name) is not None:
                field_attribute_value = list(self._field_attribute_value(header_element_name))
                field_attribute_value[self._item_position(header_element_name)] = correct_value
                field_attribute_value = tuple(field_attribute_value)
            else:
                field_attribute_value = correct_value
            self._update_attribute(self._field_attribute_name(header_element_name), field_attribute_value)

    def _log_message(self, current_values):
        # Always log the STASH code.
        message = 'lbuser4={current_value}'.format(current_value=self._field.lbuser[3])
        for header_element_name, current_value in list(current_values.items()):
            template = '{msg}, {header_element_name}={current_value}'
            message = template.format(msg=message, header_element_name=header_element_name, current_value=current_value)
        return message

    def _update_attribute(self, attribute, value):
        self.logger.debug('    Setting {attribute}={value}'.format(attribute=attribute, value=value))
        setattr(self._field, attribute, value)
