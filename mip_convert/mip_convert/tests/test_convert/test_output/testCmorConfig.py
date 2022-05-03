# (C) British Crown Copyright 2015-2021, Met Office.
# Please see LICENSE.rst for license details.

import unittest
from configparser import RawConfigParser

from mip_convert import model_date

from mip_convert.save.cmor.config_file import CmorDatasetConf
from mip_convert.save.cmor.cmor_lite import CmorDatasetCall


class TestConfigContext(unittest.TestCase):
    OUTPATH = 'an_outpath'
    DEFAULT_SECTION = 'data_source'

    def dataset(self, *args, **kwargs):
        """
        stub cmor
        """
        self.dataset_args = args
        self.dataset_kwargs = kwargs

    def makeOptions(self):
        self._options = {
            'experiment_id': 'historical',
            'source': 'HadCM3 (2003)',
            'calendar': '360_day',
            'institution': 'MOHC (Met Office Hadley Centre)',
            'runs': 'runid1 runid2'
        }
        for option in self._options:
            self._parser.set(self.DEFAULT_SECTION, option, self._options[option])

    def getExpectedKeyWords(self):
        return {
            'outpath': self.OUTPATH,
            'history': self.app_history,
        }

    def getExpectedArgs(self):
        return (
            self._options['experiment_id'],
            self._options['institution'],
            self._options['source'],
            self._options['calendar']
        )

    def assertOnArgs(self, args, kwargs):
        self.assertEqual(args, self.dataset_args)
        self.assertEqual(kwargs, self.dataset_kwargs)

    def addToDefaultSection(self, option, value):
        self._options[option] = value
        self._parser.set(self.DEFAULT_SECTION, option, value)

    def addOptionAndKeyword(self, optional, value, expected_keywords):
        self.addToDefaultSection(optional, value)
        expected_keywords[optional] = self._options[optional]

    def nullAdder(self, options, expected_keywords):
        pass

    def addStringOptionals(self, options, expected_keywords):
        for optional in options:
            self.addOptionAndKeyword(optional, '%s-value' % optional, expected_keywords)

    def addIntOptionals(self, options, expected_keywords):
        for (index, optional) in enumerate(options):
            self.addToDefaultSection(optional, str(index))
            expected_keywords[optional] = index

    def addOptionalParentInfo(self, options, expected_keywords):
        parent_base_date = '1889-01-01-00-00-00'
        branch_date = '1889-02-01-00-00-00'
        self.addStringOptionals(('parent_experiment_id', 'parent_experiment_rip'), expected_keywords)
        self.addToDefaultSection('branch_date', branch_date)
        self.addToDefaultSection('parent_base_date', parent_base_date)
        expected_keywords['branch_time'] = 30

    def _reset_parser(self):
        for option in self._parser.options(self.DEFAULT_SECTION):
            self._parser.remove_option(self.DEFAULT_SECTION, option)

    def execute(self, options, adder):
        self.makeOptions()
        expected_args = self.getExpectedArgs()
        expected_kw = self.getExpectedKeyWords()
        adder(options, expected_kw)

        dataset = CmorDatasetCall(self)
        dataset(self.context)

        self.assertOnArgs(expected_args, expected_kw)

    def setUp(self):
        self.app_history = 'application_history'
        self._parser = RawConfigParser()
        self._parser.add_section(self.DEFAULT_SECTION)
        self.context = CmorDatasetConf(self._parser, self.app_history, model_date, self.OUTPATH)

    def testAttributes(self):
        self.makeOptions()
        self.assertEqual('historical', self.context.experiment_id)

    def testNoAttributeException(self):
        try:
            self.context.experiment_id
            self.fail('Attribute Error exception not raised')
        except AttributeError as e:
            self.assertEqual("type object 'CmorDatasetConf' has no attribute 'experiment_id'", str(e))

    def testconfigureDataSet(self):
        example_options = [
            ((), self.addStringOptionals),
            (('contact',), self.addStringOptionals),
            (('contact', 'references',), self.addStringOptionals),
            (('comment', 'model_id', 'institute_id', 'forcing'),
             self.addStringOptionals),
            (('realization', 'physics_version', 'initialization_method',),
             self.addIntOptionals),
            ((), self.addOptionalParentInfo),
        ]
        for (options, adder) in example_options:
            self.execute(options, adder)
            self._reset_parser()

    def testProlepticGregorian(self):
        self.makeOptions()
        self.addToDefaultSection('calendar', 'proleptic_gregorian')
        expected_arguments = self.getExpectedArgs()
        expected_keywords = self.getExpectedKeyWords()

        dataset = CmorDatasetCall(self)
        dataset(self.context)

        self.assertOnArgs(expected_arguments, expected_keywords)

    def testNotApplicableDates(self):
        self.execute((), self.addNotApplicableDates)

    def addNotApplicableDates(self, options, expected_keywords):
        self.addStringOptionals(('parent_experiment_id',), expected_keywords)
        self.addToDefaultSection('branch_date', 'N/A')
        self.addToDefaultSection('parent_base_date', 'N/A')
        expected_keywords['branch_time'] = 0


if __name__ == '__main__':
    unittest.main()
