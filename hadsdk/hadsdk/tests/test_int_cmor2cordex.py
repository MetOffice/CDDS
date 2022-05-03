# (C) British Crown Copyright 2015-2021, Met Office.
# Please see LICENSE.rst for license details.

import copy
from nose.plugins.attrib import attr
import os
import shutil
from subprocess import Popen, PIPE
import tempfile
import unittest

import netCDF4


class UnixOutput(object):
    """
    Class to represent the output of a unix command
    """
    def __init__(self, returncode, stdout, stderr):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode

    def __repr__(self):
        return '%s(%d, %s, %s)' % (
            self.__class__.__name__, self. returncode, self.stdout,
            self.stderr)

    def __eq__(self, other):
        """
        Return True if self and other are exactly the same
        """
        return (self._stderr_eq(other) and self._stdout_eq(other) and
                self._returncode_eq(other))

    def equal_stderr_line_order_irrelevant(self, other):
        """
        Return True if self and other look the same
          the comparison of stderr ignores the ordering of the lines
        """
        return (self._stderr_sort_eq(other) and self._stdout_eq(other) and
                self._returncode_eq(other))

    def _stderr_eq(self, other):
        return self.stderr == other.stderr

    def _stdout_eq(self, other):
        return self.stdout == other.stdout

    def _returncode_eq(self, other):
        return self.returncode == other.returncode

    def _stderr_sort_eq(self, other):
        return self._sorted_copy_stderr == other._sorted_copy_stderr

    @property
    def _sorted_copy_stderr(self):
        lines = copy.copy(self.stderr).split('\n')
        lines.sort()
        return lines


class UnixAndExpected(object):
    UTIL = ['cordex_name']

    def __init__(self, args, stdout, stderr, retcode):
        self.expected = UnixOutput(retcode, stdout, stderr)
        self.unix = self.run_unix(args)

    def run_unix(self, args):
        proc = Popen(self.UTIL + args, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        out_mess, err_mess = proc.communicate()
        return UnixOutput(proc.returncode, out_mess, err_mess)


class TestCordexName(unittest.TestCase):

    def assert_on_unix(self, args, stdout, stderr, retcode):
        result = UnixAndExpected(args, stdout, stderr, retcode)
        self.assertEqual(result.expected, result.unix)

    def assert_on_unix_stderr_order_irrelevant(self, args, stdout, stderr,
                                               retcode):
        result = UnixAndExpected(args, stdout, stderr, retcode)
        self.assertTrue(
            result.expected.equal_stderr_line_order_irrelevant(result.unix))

    def assert_err(self, args, msg):
        self.assert_on_unix(args, '', msg, 1)

    def assert_pass(self, args, stdout):
        self.assert_on_unix(args, stdout, '', 0)

    def assert_err_line_order_irrelevant(self, args, err):
        self.assert_on_unix_stderr_order_irrelevant(args, '', err, 1)


class TestUserErrorsWithNoFiles(TestCordexName):

    @attr('integration')
    def test_error_with_no_filename(self):
        self.assert_err([], 'usage: cordex_name [-v] filename|dirname\n')

    @attr('integration')
    def test_error_when_not_cmor_filename(self):
        self.assert_err(
            ['any-old-file.nc'],
            'error: "any-old-file.nc" does not look like cmor output\n')

    @attr('integration')
    def test_file_does_not_exist(self):
        self.assert_err(
            ['tas_Amon_HadGEM2-ES_rcp85-rampdown_r2i1p1_210001-210001.nc'],
            'error: "tas_Amon_HadGEM2-ES_rcp85-rampdown_r2i1p1_210001-210001'
            '.nc" does not exist\n')


class TestCordexNameFile(TestCordexName):

    def setUp(self):
        self.tdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tdir)

    def path(self, fname):
        return os.path.join(self.tdir, fname)

    def create_file(self):
        f = open(self._path, 'w')
        f.close()

    def create_nc(self, nc_file):
        f = netCDF4.Dataset(self.path(nc_file.cmor_name), 'w')
        for att_name, value in list(nc_file.atts.items()):
            setattr(f, att_name, value)
        f.close()


class SampleDataset(object):
    def __init__(self, cmor_name, cordex_name, atts):
        self.cmor_name = cmor_name
        self.cordex_name = cordex_name
        self.atts = atts


class TestFileExamples(TestCordexNameFile):

    @property
    def _path(self):
        return self.path(self._cmor_name())

    def path(self, fname):
        return os.path.join(self.tdir, fname)

    def _atts(self):
        return {'CORDEX_domain': 'AFR-44',
                'driving_model_id': 'ERA',
                'driving_experiment_name': 'evaluation',
                'driving_model_ensemble_member': 'r1i1p1',
                'model_id': 'HadRM3P',
                'rcm_version_id': 'v1',
                'frequency': 'day'}

    def _cordex_name(self):
        return 'tas_AFR-44_ERA_evaluation_r1i1p1_HadRM3P_v1_%s.nc' % (
            self._freq_date())

    def _cmor_name(self):
        return 'tas_day_HadGEM2-ES_rcp85-rampdown_r2i1p1_210001-210001.nc'

    def _freq_date(self):
        result = self._atts()['frequency']
        if self._atts()['frequency'] != 'fx':
            result += '_210001-210001'
        return result

    def nc_file(self, atts=None):
        if atts is None:
            atts = self._atts()
        return SampleDataset(self._cmor_name(), self._cordex_name(), atts)

    @attr('integration')
    def test_fails_if_no_netcdf(self):
        self.create_file()
        self.assert_err(
            [self._path],
            'error: "%s" file is not a NetCDF file\n' % self._path)

    @attr('integration')
    def test_fails_if_missing_cordex_att(self):
        self.create_nc(self.nc_file({'driving_model_id': 'ERA'}))
        self.assert_err(
            [self._path],
            'error: file does not have "CORDEX_domain" global attribute\n')

    @attr('integration')
    def test_moves_file_in_verbose(self):
        self._run_test(['-v'], '%s\n' % self._cordex_name())

    @attr('integration')
    def test_moves_file_no_verbose(self):
        self._run_test([], '')

    @attr('integration')
    def test_fx_file_moved(self):
        atts = self._atts()
        atts['frequency'] = 'fx'
        atts['driving_model_ensemble_member'] = 'r0i0p0'
        nc_file = SampleDataset(
            'orog_fx_HadGEM2-ES_rcp85-rampdown_r0i0p0.nc',
            'orog_AFR-44_ERA_evaluation_r0i0p0_HadRM3P_v1_fx.nc', atts)
        self.create_nc(nc_file)

        self.assert_pass([] + [self.path(nc_file.cmor_name)], '')
        self.assertTrue(self.exists(nc_file.cordex_name))
        self.assertFalse(self.exists(nc_file.cmor_name))

    def _run_test(self, opts, stdout):
        self.create_nc(self.nc_file())

        self.assert_pass(opts + [self._path], stdout)
        self.assertTrue(self.exists(self.nc_file().cordex_name))
        self.assertFalse(self.exists(self.nc_file().cmor_name))

    def exists(self, fname):
        return os.path.exists(self.path(fname))


class TestDirectoryExamples(TestCordexNameFile):
    _DIR_NAME = 'output_files'

    def setUp(self):
        super(TestDirectoryExamples, self).setUp()
        self.mk_sub_dir()

    def mk_sub_dir(self):
        self.dirname = os.path.join(self.tdir, self._DIR_NAME)
        os.mkdir(self.dirname)

    def path(self, fname):
        return os.path.join(self.dirname, fname)

    @attr('integration')
    def test_empty_dir(self):
        self.assert_err(
            [self.dirname],
            'error: "%s" appears to be an empty directory\n' % self.dirname)

    @attr('integration')
    def test_dir_with_bad_file(self):
        self._path = self.path('bad-file.nc')
        self.create_file()
        self.assert_err(
            [self.dirname],
            'error: "%s" does not look like cmor output\n' % self.path(
                'bad-file.nc'))

    @attr('integration')
    def test_dir_with_bad_files(self):
        fnames = ['file1', 'file2']
        for fname in fnames:
            self._path = self.path(fname)
            self.create_file()

        self.assert_err_line_order_irrelevant(
            [self.dirname], self._err_lines(fnames))

    def _err_lines(self, fnames):
        return ''.join(
            ['error: "%s" does not look like cmor output\n' %
             self.path(fname) for fname in fnames])


if __name__ == '__main__':
    unittest.main()
