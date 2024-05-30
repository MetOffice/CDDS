# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
from collections import OrderedDict

import cmor

from mip_convert.common import ObjectWithLogger


class CmorWrapper(ObjectWithLogger):
    """
    Thin wrapper class around the cmor module.

    This wrapper class exists to make testing of the main CMOR
    integration class simpler.  Can substitute in an alternative
    in test cases.

    Any instances of this class will share the same 'state' - current
    table and dataset as there is only one instance of the cmor global
    variables under the cover.

    (Could this be a singleton because of the above?)
    """

    def __init__(self):
        super(self.__class__, self).__init__()

    def __getattr__(self, attr):
        return getattr(cmor, attr)

    def _debug_on_args(self, routine, args, kwargs):
        for arg in args:
            self.logger.debug('%s arg: ["%s"] "%s"', routine, type(arg), self._summarise_list(arg))
        for (item, value) in list(kwargs.items()):
            self.logger.debug('%s kwargs: "%s": ["%s"] "%s"', routine, item, type(value), self._summarise_list(value))

    @staticmethod
    def _summarise_list(content):
        """
        Reduce amount of logging information by summarising large arrays using the
        first and last NCORNER elements. A little inelegant with 3D arrays
        (e.g. bounds for regional/ocean), but better than GB of log info.
        Simple lists are ignored.
        """
        NCORNER = 5

        def _summarise(x):
            return x[:NCORNER] + ['...'] + x[-NCORNER:]

        if isinstance(content, list) and isinstance(content[0], list) and len(content) > 3 * NCORNER:
            return_list = [_summarise(i) for i in content[:NCORNER]]
            return_list += [['...'] * (2 * NCORNER + 1)]
            return_list += [_summarise(i) for i in content[-NCORNER:]]
            return return_list
        else:
            return content

    def setup(self, *args, **kwargs):
        self._debug_on_args('setup', args, kwargs)
        cmor.setup(*args, **kwargs)

    def dataset(self, *args, **kwargs):
        self._debug_on_args('dataset', args, kwargs)
        cmor.dataset(*args, **kwargs)

    def dataset_json(self, *args, **kwargs):
        # Log the contents of the JSON file as well as the file name.
        kwargs = OrderedDict(sorted(list(kwargs.items()), key=lambda item: item[0]))
        self._debug_on_args('dataset_json', args, kwargs)
        cmor.dataset_json(args[0])

    def axis(self, *args, **kwargs):
        self._debug_on_args('axis', args, kwargs)
        my_id = cmor.axis(*args, **kwargs)
        self.logger.debug('axis id: %s', my_id)
        return my_id

    def variable(self, *args, **kwargs):
        self._debug_on_args('variable', args, kwargs)
        my_id = cmor.variable(*args, **kwargs)
        self.logger.debug('variable id: %s', my_id)
        return my_id

    def write(self, *args, **kwargs):
        # Don't use 'self._debug_on_args' here because printing the data uses a large amount of memory.
        cmor.write(*args, **kwargs)
        self.logger.debug('written')

    def close(self, *args, **kwargs):
        self._debug_on_args('close', args, kwargs)
        result = cmor.close(*args, **kwargs)
        self.logger.debug('close return "%s"', result)
        return result

    def grid(self, *args, **kwargs):
        self._debug_on_args('grid', args, kwargs)
        result = cmor.grid(*args, **kwargs)
        self.logger.debug('grid return "%s"', result)
        return result

    def load_table(self, *args, **kwargs):
        self._debug_on_args('load_table', args, kwargs)
        return cmor.load_table(*args, **kwargs)

    def set_cur_dataset_attribute(self, *args, **kwargs):
        self._debug_on_args('set_cur_dataset_attribute', args, kwargs)
        cmor.set_cur_dataset_attribute(*args, **kwargs)

    def set_grid_mapping(self, *args, **kwargs):
        self._debug_on_args('set_grid_mapping', args, kwargs)
        cmor.set_grid_mapping(*args, **kwargs)

    def zfactor(self, *args, **kwargs):
        self._debug_on_args('zfactor', args, kwargs)
        cmor.zfactor(*args, **kwargs)
