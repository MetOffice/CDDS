# (C) British Crown Copyright 2015-2025, Met Office.
# Please see LICENSE.md for license details.
"""
The :mod:`save.cmor.cmor_lite` module provides a lightweight interface
to |CMOR|.

Using |CMOR| requires three main stages. The first is to setup the
|CMOR| configuration options and define the |dataset| meta-data. This
first stage needs doing only once. The second is to define which
|MIP requested variables| are going to be written to this |dataset|.
The final stage is to actually write the data.

This is demonstrated with an example::

  from cmor_lite import setup_and_dataset, get_saver

  # define the dataset for the variables
  setup_and_dataset(conf, meta_data)

  # define the MIP requested variables to be written into this
  # dataset
  for variable in variables:
      variable.saver = get_saver(variable.mip_table_id,
                                 variable.variable_name)

  # example of writing the data
  for time_period in periods(start_time, end_time, period_length):
      for variable in variables:
           variable.saver(variable.data[time_period])

For more details see the individual function documentation in the
`CMOR Documentation`_.

Note: it is possible to call :func:`dataset` more than once for each
call to ``cmor.setup``, in practice this tends not to be done as a
single :func:`dataset` call gives a big enough 'block of work' to
manage.
"""
from mip_convert.save.cmor.cmor_wrapper import CmorWrapper
from mip_convert.save.cmor.cmor_outputter import saverFactory, CmorOutputError
from mip_convert import model_date

_CMOR = CmorWrapper()
_FACTORY = None


def setup(setup_conf):
    """
    Call ``cmor.setup`` with arguments from setup_conf.

    :param setup_conf: an object with attributes that contain the
                       options for the call to ``cmor.setup``.

    The ``setup_conf`` can have any of the attributes that are needed
    as options for the ``cmor.setup`` call. In this implementation, and
    unlike the underlying ``cmor.setup``, ``setup_conf`` must have an
    attribute ``inpath``.

    All other attributes are optional. If an attribute is missing then
    the corresponding function argument will be absent when
    ``cmor.setup`` is called. The optional attributes are:
    ``netcdf_file_action``, ``set_verbosity``, ``exit_control``,
    ``logfile`` and ``create_subdirectories``. The last three of these
    can be given as the named |CMOR| constants, for example
    ``CMOR_REPLACE``.

    An example implementation of a ``setup_conf`` is given in the class
    :class:`mip_convert.save.cmor.config_file.CmorSetupConf`.
    """
    global _FACTORY   # simplifies user interface to module

    CmorSetupCall(_CMOR)(setup_conf)
    _FACTORY = saverFactory(setup_conf.inpath, _CMOR)


def dataset(meta_data):
    """
    Call ``cmor.dataset`` with arguments taken from ``meta_data``
    attributes.

    :param meta_data: an object with attributes that contain the
                      options for the call to ``cmor.dataset``.

    The ``meta_data`` object has some compulsory attributes, and some
    optional attributes. These attributes are used in calls to
    ``cmor.dataset``. It should also have a ``global_attributes``
    method that returns key, value pairs of global attribute names and
    their values.

    The compulsory attributes are: ``experiment_id``, ``institution``,
    ``source``, ``calendar``, ``outpath`` and ``history`` (note
    ``outpath`` and ``history`` are compulsory even though they are
    optional in the underlying ``cmor.dataset`` call. The optional
    arguments are, largely, the remainder of the ``cmor.dataset``
    arguments: ``realization``, ``contact``, ``comment``,
    ``references``, ``leap_year``, ``leap_month``, ``month_lengths``,
    ``model_id``, ``forcing``, ``initialization_method``,
    ``physics_version``, ``institute_id``, ``parent_experiment_id``,
    ``branch_time``, ``parent_experiment_rip``

    Rather than passing in the ``cmor.dataset`` ``branch_time``, the
    ``meta_data`` can have a ``branch_date``, ``parent_base_date``, and
    ``TIME_FORMAT`` attributes. If ``branch_date`` is not present then the
    ``branch_time`` is set appropriately. If ``branch_date`` is
    present, then ``parent_base_date`` should also be present. These
    are then used (along with ``calendar``) to calculate the
    ``branch_time``. When present, ``branch_date`` and
    ``parent_base_date`` are strings of the format defined by
    ``TIME_FORMAT`` which should be a format string as described in
    :func:`time.strftime`.

    Note although an attribute of ``meta_data`` may be an optional
    argument to ``cmor.dataset`` the |MIP tables| may insist on some
    options being present.

    An example implementation of a ``meta_data`` class can be found in
    :class:`mip_convert.save.cmor.config_file.CmorDatasetConf`.
    """
    CmorDatasetCall(_CMOR)(meta_data)


def setup_and_dataset(setup_conf, meta_data):
    """
    Initialise |CMOR|: both the setup configuration and the |dataset|
    meta-data.

    :param setup_conf: the |CMOR| setup configuration options
    :param meta_data: the meta-data for the |dataset| to be written to

    See the documentation for :func:`setup` and :func:`dataset` for
    more information on the ``setup_conf`` and ``meta_data`` arguments.
    """
    setup(setup_conf)
    dataset(meta_data)


def get_saver(mip_table_id, variable_name, outputs_per_file=None):
    """
    Return a saver callable for this ``variable_name`` from the
    ``mip_table_id``.

    The returned callable when called with a |MIP requested variable|
    (data and meta-data) will write that |MIP requested variable| using
    |CMOR|.

    :param mip_table_id: the |MIP table identifier|
    :type mip_table_id: string
    :param variable_name: the |MIP requested variable name|
    :type variable_name: string
    :param outputs_per_file: the number of time slices of a variable to
                             write to each |output netCDF file|
    :type outputs_per_file: int
    :return: a function with signature function(data)
    :rtype: callable
    """
    if _FACTORY is None:
        raise CmorOutputError('setup_and_dataset should be called before get_saver')
    return _FACTORY.getSaver(mip_table_id, variable_name, outputs_per_file)


def close(variable_id=None):
    """
    Call |CMOR| to close down all files.
    """
    _CMOR.close(variable_id)


class _KeywordsFromAttributes(object):
    """
    A base class for classes that need to retrieve attributes from
    objects and perform some translation on the attribute.

    Sub classes need to define sequences _STR_ATTS, _INT_ATTS and
    _CMOR_CONSTANT_ATTS that contain the names of attributes that are
    strings, integers and |CMOR| module constants, respectively.
    """
    def __init__(self, cmor):
        self._cmor = cmor    # anomoly - longer term use _CMOR
        self._ATTS = list(self._STR_ATTS) + list(self._INT_ATTS) + list(self._CMOR_CONSTANT_ATTS)

    def _get_optionals(self, conf):
        """
        Return a dictionary where the keys are the conf attributes
        and the values are the attribute values converted to the
        correct type.
        """
        kwargs = {}
        for attname in self._ATTS:
            if hasattr(conf, attname):
                trans_func = self._translator(attname)
                kwargs[attname] = trans_func(getattr(conf, attname))
        return kwargs

    def _str_to_cmor(self, attval):
        """
        Return the value of the |CMOR| constant for attval.
        """
        return eval('self._cmor.%s' % attval)

    def _translator(self, attname):
        """
        Translate the attribute into form for ``cmor.setup``.
        """
        result = str
        if attname in self._INT_ATTS:
            result = int
        elif attname in self._CMOR_CONSTANT_ATTS:
            result = self._str_to_cmor
        return result


class CmorSetupCall(_KeywordsFromAttributes):
    """
    See the documentation for :func:`setup`.
    """
    _STR_ATTS = ('inpath', 'logfile')
    _INT_ATTS = ('create_subdirectories',)
    _CMOR_CONSTANT_ATTS = ('netcdf_file_action', 'set_verbosity', 'exit_control')

    def __call__(self, setup_conf):
        kwargs = self._get_optionals(setup_conf)
        self._cmor.setup(**kwargs)


class CmorDatasetCall(_KeywordsFromAttributes):
    """
    See the documentation for :func:`dataset`.
    """

    _STR_ATTS = ('model_id',
                 'institute_id',
                 'contact',
                 'references',
                 'comment',
                 'forcing',
                 'parent_experiment_id',
                 'parent_experiment_rip')
    """
    Attributes that are optional in the configuration file and are passed to ``cmor.dataset``.
    """

    _INT_ATTS = ('realization', 'physics_version', 'initialization_method')
    """
    Integer attributes that are optional in the configuration file.
    """

    _CMOR_CONSTANT_ATTS = ()

    _BRANCH_DATE_NOT_APPLICABLE = 'N/A'
    """
    The section option value indicating the fact that ``branch_date`` is not applicable.
    """

    _BRANCH_TIME_NOT_APPLICABLE = 0.
    """
    ``cmor.dataset`` argument indicating a null ``branch_time``.
    """

    def __call__(self, config):
        if hasattr(config, 'write_json'):
            filename = config.write_json()
            kwargs = config.items  # For logging purposes only.
            self._cmor.dataset_json(filename, **kwargs)
        else:
            kwargs = self._optionals(config)
            self._cmor.dataset(config.experiment_id,
                               config.institution,
                               config.source,
                               config.calendar,
                               outpath=config.outpath,
                               history=config.history,
                               **kwargs)

    def _optionals(self, config):
        kwargs = self._get_optionals(config)
        if hasattr(config, 'branch_date'):
            self._branch_date(config, kwargs)
        return kwargs

    def _time_from_option(self, config, option):
        return model_date.strptime(getattr(config, option), config.TIME_FORMAT, config.calendar)

    def _branch_date(self, config, kwargs):
        """
        Deal with branch date if present.
        """
        if config.branch_date == self._BRANCH_DATE_NOT_APPLICABLE or (config.branch_date is None):
            branch_time = self._BRANCH_TIME_NOT_APPLICABLE
        else:
            branch_date = self._time_from_option(config, 'branch_date')
            parent_base_date = self._time_from_option(config, 'parent_base_date')
            branch_time = (branch_date - parent_base_date)
        kwargs['branch_time'] = branch_time
