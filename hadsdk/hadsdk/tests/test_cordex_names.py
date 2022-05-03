# (C) British Crown Copyright 2015-2021, Met Office.
# Please see LICENSE.rst for license details.

import io
import unittest

from hadsdk import cordex_name
from hadsdk.cordex_name import (CmorFilePath, CmorCordexFile, parse_args,
                                Response, Ok)


class FakeDataSet(object):
    atts = {'CORDEX_domain': 'AFR-44',
            'driving_model_id': 'ERA',
            'driving_experiment_name': 'evaluation',
            'driving_model_ensemble_member': 'r1i1p1',
            'model_id': 'HadRM3P',
            'rcm_version_id': 'v1',
            'frequency': 'day'}

    def __init__(self):
        self._missing = None

    def __getattr__(self, attname):
        if attname == self._missing:
            raise AttributeError()
        return self.atts[attname]

    def missing_att(self, attname):
        self._missing = attname

    def close(self):
        self.is_closed = True


class FakeResponse(object):
    def __init__(self, verbose):
        self._verbose = verbose
        self.error_msg = []
        self.info_msg = []

    def error(self, error_msg):
        self.error_msg.append(error_msg)

    def message(self, info_msg):
        self.info_msg.append(info_msg)


class BaseCmorPathTest(unittest.TestCase):
    def cmor_path(self, fname, verbose):
        self._verbose = verbose
        return CmorFilePath(fname, FakeResponse(verbose))


class TestCmorFileNames(BaseCmorPathTest):

    eg_input = 'tas_Amon_HadGEM2-ES_rcp85-rampdown_r2i1p1_210001-210001.nc'
    eg_output = (
        'tas_AFR-44_ERA_evaluation_r1i1p1_HadRM3P_v1_day_210001-210001.nc')

    def valid_name(self, fname):
        return self.cmor_path(fname, True).is_valid()

    def test_ok_names(self):
        for date in ('210001', '21002'):
            self.assertTrue(
                self.valid_name(
                    'tas_Amon_HadGEM2-ES_rcp85-rampdown_r2i1p1_%s-%s.nc' % (
                        date, date)))

    def test_fx_name(self):
        self.assertTrue(
            self.valid_name('orog_fx_HadGEM2-ES_rcp85-rampdown_r0i0p0.nc'))

    def test_fx_path(self):
        fname = self.cmor_path(
            '/dir_underscore/%s' %
            'orog_fx_HadGEM2-ES_rcp85-rampdown_r0i0p0.nc', True)
        fname.cds = CmorCordexFile(FakeDataSet())
        fname.cds._ds.atts['frequency'] = 'fx'
        self.assertTrue(fname.is_valid())
        self.assertEqual(
            '/dir_underscore/%s' %
            'orog_AFR-44_ERA_evaluation_r1i1p1_HadRM3P_v1_fx.nc',
            fname.cordex_path())

    def test_no_nc(self):
        self.assertFalse(self.valid_name((self.eg_input[:-3])))

    def test_new_path(self):
        fname = self.cmor_path('/dir_underscore/%s' % self.eg_input, True)
        fname.cds = CmorCordexFile(FakeDataSet())
        fname.cds._ds.atts['frequency'] = 'day'

        self.assertTrue(fname.is_valid())
        self.assertEqual(
            '/dir_underscore/%s' % self.eg_output, fname.cordex_path())


class StubCmorFile(object):
    def __init__(self):
        self.is_closed = False

    def check_cordex_att(self):
        return Ok()

    def close(self):
        self.is_closed = True


class TestIsGoodCMorNetCdf(BaseCmorPathTest):

    def false(self):
        return False

    def true(self):
        return True

    def assert_exit_message(self, cmor_path, msg):
        response = cmor_path.check_good_cmor_netcdf()
        self.assertFalse(response.ok())
        self.assertEqual(msg, response.msg)

    def test_not_valid(self):
        cmor_path = self.cmor_path('not-valid', True)
        cmor_path.is_valid = self.false
        self.assert_exit_message(
            cmor_path, 'error: "not-valid" does not look like cmor output')

    def test_no_exists(self):
        cmor_path = self.cmor_path('not-exist', True)
        cmor_path.is_valid = self.true
        cmor_path.exists = self.false
        self.assert_exit_message(
            cmor_path, 'error: "not-exist" does not exist')

    def test_not_netCDF(self):
        cmor_path = self.cmor_path('not-netcdf', True)
        cmor_path.is_valid = self.true
        cmor_path.exists = self.true
        cmor_path.is_netcdf = self.false

        self.assert_exit_message(
            cmor_path, 'error: "%s" file is not a NetCDF file' % 'not-netcdf')

    def test_ok(self):
        cmor_path = self.cmor_path('not-netcdf', True)
        cmor_path.is_valid = self.true
        cmor_path.exists = self.true
        cmor_path.is_netcdf = self.true
        cmor_path.cds = StubCmorFile()

        response = cmor_path.check_good_cmor_netcdf()
        self.assertTrue(response.ok())


class TestRename(BaseCmorPathTest):
    def cordex_name(self):
        return 'cordex_name'

    def true(self):
        return True

    def rename(self, source, dest):
        self.source = source
        self.dest = dest

    def test_mv_bad_file(self):
        filename = (
            'tas_AFR-44_ERA_evaluation_r1i1p1_HadRM3P_v1_day_210001-210001.nc')
        cmor_file = self.cmor_path(filename, True)
        response = cmor_file.rename()
        self.assertEqual(
            response.error_msg, [
                'error: "%s" does not look like cmor output' % filename])

    def test_mv_good_file(self):
        cmor_file = self.cmor_path(
            'tas_Amon_HadGEM2-ES_rcp85-rampdown_r2i1p1_210001-210001.nc', True)
        cmor_file._cordex_name = self.cordex_name
        cmor_file.is_valid = self.true
        cmor_file.exists = self.true
        cmor_file.is_netcdf = self.true
        cmor_file.cds = StubCmorFile()

        preserved1 = cordex_name.os.rename
        cordex_name.os.rename = self.rename

        response = cmor_file.rename()
        self.assertEqual([cmor_file.cordex_path()], response.info_msg)
        self.assertEqual(cmor_file.path, self.source)
        self.assertEqual(cmor_file.cordex_path(), self.dest)
        self.assertTrue(cmor_file.cds.is_closed)
        cordex_name.os.rename = preserved1


class TestCmorCordexFile(unittest.TestCase):

    def test_check_cordex_atts(self):
        missing = 'driving_model_id'
        f = CmorCordexFile(FakeDataSet())
        f._ds.missing_att(missing)
        result = f.check_cordex_att()
        self.assertFalse(result.ok())
        self.assertEqual(
            'error: file does not have "%s" global attribute' % missing,
            result.msg)

    def test_close(self):

        f = CmorCordexFile(FakeDataSet())
        f.close()
        self.assertTrue(f._ds.is_closed)


class StubCmorFilePath(object):
    def __init__(self, path, response):
        self.path = path
        self.verbose = response._verbose


class TestParseArgs(unittest.TestCase):
    _NO_EXIST_DIR = 'dirname'

    def isdir(self, dname):
        return dname == self._NO_EXIST_DIR

    def setUp(self):

        self.preserved2 = cordex_name.os.path.isdir
        cordex_name.os.path.isdir = self.isdir

        self.preserved3 = cordex_name.CmorFilePath
        cordex_name.CmorFilePath = StubCmorFilePath

    def tearDown(self):
        cordex_name.os.path.isdir = self.preserved2
        cordex_name.CmorFilePath = self.preserved3

    def test_file_exist(self):  # move somewhere else?
        cmor_file_path = parse_args(['cordex_name', 'existing-file'])
        self.assertEqual('existing-file', cmor_file_path.path)
        self.assertFalse(cmor_file_path.verbose)

    def test_args_giving_usage(self):
        for args in (['cordex_name'], ['cordex_name', '-x', 'existing-file']):
            result = parse_args(args)
            self.assertEqual('usage: cordex_name [-v] filename|dirname', result.msg)

    def test_verbose(self):
        cmor_file_path = parse_args(['cordex_name', '-v', 'existing-file'])
        self.assertEqual('existing-file', cmor_file_path.path)
        self.assertTrue(cmor_file_path.verbose)  # better test?


class TestDirofFiles(unittest.TestCase):
    def isdir(self, dname):
        return True

    def listdir(self, dname):
        return self.dirlist[dname]

    def setUp(self):
        self.responses = []

        self.preserved1 = cordex_name.os.listdir
        cordex_name.os.listdir = self.listdir

        self.preserved2 = cordex_name.os.path.isdir
        cordex_name.os.path.isdir = self.isdir

    def tearDown(self):

        cordex_name.os.listdir = self.preserved1
        cordex_name.os.path.isdir = self.preserved2

    def test_empty_dir(self):
        self.dirlist = {'empty': []}
        response = self.get_response()
        self.assert_error(
            response, ['error: "empty" appears to be an empty directory'])

    def test_renames(self):
        self.dirlist = {'a-dir': ['fname1', 'fname2']}
        response = self.get_response()
        self.assert_error(
            response, ['error: "a-dir/fname1" does not look like cmor output',
                       'error: "a-dir/fname2" does not look like cmor output'])

    def get_response(self):
        args = ['cordex_rename', list(self.dirlist.keys())[0]]
        cmor_dir = parse_args(args)
        cmor_dir._responses = FakeResponse(False)
        return cmor_dir.rename()

    def assert_error(self, response, msg):
        self.assertEqual(msg, response.error_msg)


class Exit(Exception):
    pass


class FakeSys(object):
    def __init__(self):
        self.code = 0
        self.stdout = io.StringIO()
        self.stderr = io.StringIO()

    def exit(self, code):
        self.code = code
        raise Exit()


class TestResponse(unittest.TestCase):

    def setUp(self):
        self.sys = FakeSys()
        self.preserve = cordex_name.sys
        cordex_name.sys = self.sys

    def tearDown(self):
        cordex_name.sys = self.preserve

    def test_no_responses_added(self):
        self.set_responder(True)
        try:
            self.response.exit()
            self.fail('exit does not exit')
        except Exit:
            self.assert_on_good_response('')

    def test_add_stdout_not_verbose(self):
        self.set_responder(False)
        try:
            self.add_good_message()
            self.assert_on_good_response('')

        except Exit:
            self.fail("exited, when shouldn't have")

    def test_add_stdout_verbose(self):
        self.set_responder(True)
        try:
            self.add_good_message()
            self.assert_on_good_response(self.stdout + '\n')
        except Exit:
            self.fail("exited, when shouldn't have")

    def test_exit_afterstdout(self):
        self.set_responder(False)
        try:
            self.add_good_message()
            self.response.exit()
            self.fail('exit does not exit')
        except Exit:
            self.assert_on_good_response('')

    def test_add_stderr(self):
        self.set_responder(True)
        try:
            self.add_error_message()
            self.assert_on_error_response()
        except Exit:
            self.fail("exited, when shouldn't have")

    def test_exit_after_stderr(self):
        self.set_responder(True)
        try:
            self.add_error_message()
            self.response.exit()
            self.fail('exit does not exit')
        except Exit:
            self.assert_on_error_response()

    def set_responder(self, verbose):
        self.response = Response(verbose)

    def add_good_message(self):
        self.stdout = 'message'
        self.response.message(self.stdout)

    def add_error_message(self):
        self.stderr = 'error'
        self.response.error(self.stderr)

    def assert_on_good_response(self, stdout):
        self.assertEqual(stdout, self.sys.stdout.getvalue())
        self.assertEqual('', self.sys.stderr.getvalue())
        self.assertEqual(0, self.response._code)

    def assert_on_error_response(self):
        self.assertEqual('', self.sys.stdout.getvalue())
        self.assertEqual('error\n', self.sys.stderr.getvalue())
        self.assertEqual(1, self.response._code)


if __name__ == '__main__':
    unittest.main()
