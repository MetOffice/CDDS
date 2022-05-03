# (C) British Crown Copyright 2015-2021, Met Office.
# Please see LICENSE.rst for license details.
from getopt import getopt, GetoptError
from operator import eq, ne
import os
import sys

import netCDF4


class NullPath(object):
    def __init__(self, msg, response):
        self.msg = msg
        self.response = response

    def rename(self):
        self.response.error(self.msg)
        return self.response


class CommandLineArgs(object):

    _USAGE = 'usage: cordex_name [-v] filename|dirname'

    def __call__(self, args):

        if self._user_needs_usage(args):
            return NullPath(self._USAGE, Response(True))

        response = Response(self._is_verbose)
        if os.path.isdir(self._path):
            return DirOfCmorFiles(self._path, response)
        else:
            return CmorFilePath(self._path, response)

    @property
    def _path(self):
        return self.rarg[0]

    @property
    def _has_single_path(self):
        return len(self.rarg) == 1

    @property
    def _is_verbose(self):
        result = False
        for (opt, val) in self.opts:
            if opt == '-v':
                result = True
                break
        return result

    def _user_needs_usage(self, args):
        return not self._options_recognised(args) or not self._has_single_path

    def _options_recognised(self, args):
        result = True
        try:
            (self.opts, self.rarg) = getopt(args[1:], 'v')
        except GetoptError:
            result = False
        return result


def parse_args(args):
    cl = CommandLineArgs()
    return cl(args)


class Response(object):
    _NEW_LINE = '\n'

    def __init__(self, verbose):
        self._code = 0
        self._verbose = verbose

    def error(self, message):
        self._code = 1
        sys.stderr.write(message + self._NEW_LINE)

    def message(self, message):
        if self._verbose:
            sys.stdout.write(message + self._NEW_LINE)

    def exit(self):
        sys.exit(self._code)


class Ok(object):
    def ok(self):
        return True


class NotOk(object):
    def __init__(self, msg):
        self.msg = msg

    def ok(self):
        return False


class BaseCmorName(object):
    _COMP_SEP = '_'
    _VAR_IND = 0
    _END_IND = 5
    _EXT = '.nc'

    def __init__(self, fname):
        self._file_name = fname  # TODO: privatise this

    def _component(self, index):
        return self._components()[index]

    def _components(self):
        return self._file_name.split(self._COMP_SEP)

    def _number_components(self):
        return len(self._components())

    def _var(self):
        return self._component(self._VAR_IND)

    def cordex_name(self, cds):
        return self._COMP_SEP.join(
            [self._var()] + cds.components_in_order()) + self._cordex_tail()


class PotentialCmorName(BaseCmorName):
    def _is_componentiseable_nc(self):
        return (self._file_name.endswith(self._EXT) and
                self._COMP_SEP in self._file_name)

    def _fx_compare(self, cfunc, addlen):
        return (self._is_componentiseable_nc() and
                cfunc(self._component(1), 'fx') and
                self._number_components() == self._END_IND + addlen)

    def is_fx(self):
        return self._fx_compare(eq, 0)

    def is_cmor(self):
        return self._fx_compare(ne, 1)


class FxCmorName(BaseCmorName):
    def _cordex_tail(self):
        return self._EXT


class NoneFxCmorName(BaseCmorName):
    def _cordex_tail(self):
        return self._COMP_SEP + self._dates()

    def _dates(self):
        return self._component(self._END_IND)


class CmorFilePath(object):  # rename this?

    def __init__(self, fname, response):
        self.path = fname
        self.file_name = os.path.basename(fname)
        self.response = response
        self.cds = None
        self.namer = None

    def rename(self):
        status = self.check_good_cmor_netcdf()
        if not status.ok():
            self.response.error(status.msg)
        else:
            self._mv()
            self.cds.close()
        return self.response

    def _mv(self):
        os.rename(self.path, self.cordex_path())
        self.response.message(self._cordex_name())

    def _error(self, msg):
        return NotOk('error: "%s" %s' % (self.path, msg))

    def check_good_cmor_netcdf(self):
        if not self.is_valid():
            msg = self._error('does not look like cmor output')
        elif not self.exists():
            msg = self._error('does not exist')
        elif not self.is_netcdf():
            msg = self._error('file is not a NetCDF file')
        else:
            msg = self.cds.check_cordex_att()
        return msg

    def is_valid(self):
        result = True
        potential = PotentialCmorName(self.file_name)
        if potential.is_fx():
            self.namer = FxCmorName(self.file_name)
        elif potential.is_cmor():
            self.namer = NoneFxCmorName(self.file_name)
        else:
            result = False
        return result

    def is_netcdf(self):
        # logical looking - but side effects?
        result = True
        try:
            self.cds = CmorCordexFile(netCDF4.Dataset(self.path, 'r'))
        except:
            result = False

        return result

    def exists(self):
        return os.path.exists(self.path)

    def _cordex_name(self):
        return self.namer.cordex_name(self.cds)

    def cordex_path(self):
        return os.path.join(os.path.dirname(self.path), self._cordex_name())


class CmorCordexFile(object):

    _CORDEX_ATTS = ('CORDEX_domain',
                    'driving_model_id',
                    'driving_experiment_name',
                    'driving_model_ensemble_member',
                    'model_id',
                    'rcm_version_id',
                    'frequency')

    _MSG_FMT = 'error: file does not have "%s" global attribute'

    def __init__(self, dataset):
        self._ds = dataset

    def check_cordex_att(self):
        for att in self._CORDEX_ATTS:
            if not hasattr(self._ds, att):
                return NotOk(self._MSG_FMT % att)
        return Ok()

    def components_in_order(self):
        return [getattr(self._ds, att) for att in self._CORDEX_ATTS]

    def close(self):
        self._ds.close()


class DirOfCmorFiles(object):

    _EMPTY_DIR_FMT = 'error: "%s" appears to be an empty directory'

    def __init__(self, dname, responder):
        self._dname = dname
        self._responses = responder

    def rename(self):
        if self._empty():
            self._error(self._EMPTY_DIR_FMT % self._dname)
        else:
            self._loop_files()
        return self._responses

    def _error(self, msg):
        self._responses.error(msg)

    def _loop_files(self):
        for path in self._list_path():
            CmorFilePath(path, self._responses).rename()

    def _empty(self):
        return len(self._list()) == 0

    def _list_path(self):
        return [self._path(fname) for fname in self._list()]

    def _path(self, fname):
        return os.path.join(self._dname, fname)

    def _list(self):
        return os.listdir(self._dname)
