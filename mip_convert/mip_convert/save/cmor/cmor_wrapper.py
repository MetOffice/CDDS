# (C) British Crown Copyright 2009-2025, Met Office.
# Please see LICENSE.md for license details.
from collections import OrderedDict
import os
import json

import cmor

from mip_convert.common import ObjectWithLogger


class CmorWrapper(ObjectWithLogger):
    """Thin wrapper class around the cmor module.

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
        """Reduce amount of logging information by summarising large arrays using the
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

    def set_frequency(self, frequency, **kwargs):
        self._debug_on_args('frequency', [frequency], kwargs)
        cmor.cmor.set_cur_dataset_attribute('frequency', frequency)

    def apply_cell_measures(self, mip_era, mip_table_dir, realm, variable, frequency, region, variable_id):
        # self._debug_on_args('apply_cell_measures', [mip_table_dir])
        """
        Add cell measures read from json file in with mip tables
        """

        cell_measures_file = os.path.join(mip_table_dir, f'{mip_era}_cell_measures.json')

        if os.path.exists(cell_measures_file):
            with open(cell_measures_file) as fh:
                cell_measures = json.load(fh)
            if 'cell_measures' not in cell_measures:
                self.logger.debug(f'"cell_measures" key not found in {cell_measures_file}')
                return
            cell_measures = cell_measures['cell_measures']

            root_label, branding = variable.split('_')
            key = f'{realm}.{root_label}.{branding}.{frequency}.{region}'
            if key in cell_measures:
                retval = cmor.cmor.set_variable_attribute(
                    variable_id,
                    'cell_measures',
                    'c',
                    cell_measures[key])
                if retval != 0:
                    self.logger.debug('cell_measures assignment failed. Check cmor log file for details')
        else:
            self.logger.debug(f'Cell_measures file "{cell_measures_file}" not found. Continuing')
