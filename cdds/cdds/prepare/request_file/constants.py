# (C) British Crown Copyright 2020-2021, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = no-member
UKESM_URL = 'https://ukesm.ac.uk/cmip6'

BASE_DATE = '1850-01-01-00-00-00'

ROSE_SUITE_BRANCH = 'cdds'
ROSE_SUITE_FILENAME = 'rose-suite.info'
CONFIG_VERSION = '1.0.1'

# Controlled vocabulary file name
CV_FILENAME = '{}_CV.json'

# License template
CMIP6_MOHC = ('CMIP6 model data produced by the {} is licensed under a '
              'Creative Commons Attribution-ShareAlike 4.0 International '
              'License (https://creativecommons.org/licenses). Consult '
              'https://pcmdi.llnl.gov/CMIP6/TermsOfUse for terms of use '
              'governing CMIP6 output, including citation requirements and '
              'proper acknowledgment. Further information about this data, '
              'including some limitations, can be found via the '
              'further_info_url (recorded as a global attribute in this file) '
              'and at https://ukesm.ac.uk/cmip6. The data producers and data providers make no '
              'warranty, either express or implied, including, but not '
              'limited to, warranties of merchantability and fitness for a '
              'particular purpose. All liabilities arising from the supply of '
              'the information (including any liability arising in '
              'negligence) are excluded to the fullest extent permitted by '
              'law.')

# Keys in controlled vocabulary
CV_EXPERIMENT_ID = 'experiment_id'

GCMODELDEV_MOHC = ('GCModelDev model data produced by the {} is licensed under '
                   'a Creative Commons Attribution.* 4.0 International '
                   'License. https://creativecommons.org/licenses.')

LICENSES = {'CMIP6': CMIP6_MOHC,
            'GCModelDev': GCMODELDEV_MOHC}

# Keys in rose suite
ROSE_SUITE_EXPERIMENT_ID = 'experiment-id'
ROSE_SUITE_CV = 'controlled-vocabulary'
ROSE_SUITE_PROJECT = 'project'
ROSE_SUITE_SOURCE_TYPE = 'source-type'


class Messages(object):
    """
    Messages for rose  suite value checks
    """

    @classmethod
    def source_types_failed(cls, allowed_types):
        return 'Not all source types are allowed. Only allow: {}'.format(', '.join(allowed_types))

    @classmethod
    def source_types_passed(cls):
        return 'All source types are allowed and supported'

    @classmethod
    def value_allowed_failed(cls, actual, allowed_values):
        return 'Value "{}" must be in "[{}]"'.format(actual, ', '.join(allowed_values))

    @classmethod
    def value_allowed_passed(cls):
        return 'Value is valid'

    @classmethod
    def mip_allowed_failed(cls, actual, allowed_values):
        return 'Value {} does not match activity-id from CV. Expected {}'.format(actual, allowed_values)

    @classmethod
    def mip_allowed_passed(cls):
        return 'MIP is valid'

    @classmethod
    def all_values_in_failed(cls, actuals_as_string, allowed_elements):
        return 'All values in "[{}]" must also be in "{}"'.format(', '.join(allowed_elements), actuals_as_string)

    @classmethod
    def all_values_in_passed(cls):
        return 'Values are all valid'

    @classmethod
    def parent_failed(cls, actual, expected):
        return 'Parent {} is not valid for this experiment. Expect: {}'.format(actual, expected)

    @classmethod
    def parent_passed(cls):
        return 'Parent is set correctly.'

    @classmethod
    def one_year_after_failed(cls, actual, reference):
        return 'Year of {} must be exactly one year after {}'.format(actual, reference)

    @classmethod
    def one_year_after_passed(cls, actual):
        return 'Year of date {} is valid.'.format(actual)

    @classmethod
    def year_failed(cls, actual, expected):
        return 'Year of date {} must be equal to {}.'.format(actual, expected)

    @classmethod
    def year_passed(cls, actual):
        return 'Year of date {} is valid.'.format(actual)
