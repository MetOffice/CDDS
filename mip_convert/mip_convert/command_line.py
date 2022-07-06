# (C) British Crown Copyright 2020-2021, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable=no-member, logging-format-interpolation
"""
Produce the |output netCDF files| for a |MIP| using
|model output files| that cover a single uninterrupted time period and
information provided in the |user configuration file|.
"""
import argparse
import logging
import sys

from cdds.common.plugins.plugin_loader import load_plugin
from hadsdk.common import configure_logger, check_file
from mip_convert import __version__
from mip_convert.constants import LOG_NAME, LOG_LEVEL
from mip_convert.request import convert


def main(args=None):
    """
    Produce the |output netCDF files| for a |MIP| using
    |model output files|.

    If a |MIP requested variable| is unable to be produced, for
    example, if there is:

    * no |model to MIP mapping| corresponding to the
      |MIP requested variable name|
    * no entry in the |MIP table| corresponding to the
      |MIP requested variable name|
    * a problem with loading the relevant data from the
      |model output files|, processing the |input variable| /
      |input variables| or saving the |MIP output variable|

    no exceptions are raised; instead, an appropriate ``CRITICAL``
    message will be written to the log and the exit code will be set
    equal to 2.
    """
    if args is None:
        args = sys.argv[1:]
    parameters = parse_parameters(args)

    # Create the configured logger.
    configure_logger(parameters.log_name, parameters.log_level, parameters.append_log, datestamp=parameters.datestamp)

    # Retrieve the logger.
    logger = logging.getLogger(__name__)

    # Log version.
    logger.info('Using MIP Convert version {}'.format(__version__))

    try:
        exit_code = convert(parameters)
    except BaseException as err:
        logger.exception(err)
        raise

    return exit_code


def parse_parameters(args):
    """
    Return the names of the parameters and their validated values.

    If :func:`parse_parameters` is called from the Python interpreter
    with ``args`` that contains any of the ``--version``, ``-h`` or
    ``--help`` options, the Python interpreter will be terminated.

    The output from the :func:`parse_parameters` function can be used
    as the value of the ``parameters`` parameter in the call to
    :func:`convert`.

    :param args: the parameters to be parsed
    :type args: list of strings
    :return: the names of the parameters and their validated values
    :rtype: :class:`argparse.Namespace` object
    """
    description = __doc__.replace('|', '').replace('``', '')
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('config_file',
                        help=(
                            'The name of the user configuration file (for more information, please see the MIP'
                            'Convert user guide: https://code.metoffice.gov.uk/doc/cdds/mip_convert/user_guide.html).')
                        )
    parser.add_argument('-s',
                        '--stream_identifiers',
                        nargs='*',
                        help=('The stream identifiers to process. If all streams should be processed,'
                              'do not specify this option.')
                        )
    parser.add_argument('-l',
                        '--log_name',
                        default=LOG_NAME,
                        help=(
                            'The name of the log file. The log file will be written to the current working directory '
                            'unless the full path is provided. Set the value to an empty string to only send messages '
                            'to the screen i.e., do not create a log file.')
                        )
    parser.add_argument('-a',
                        '--append_log',
                        action='store_true',
                        help='Append to the log, rather than overwrite.'
                        )
    parser.add_argument('--datestamp',
                        help='Specify the datestamp to use for the log files.',
                        default=None
                        )
    parser.set_defaults(log_level=LOG_LEVEL)

    log_level_group = parser.add_mutually_exclusive_group()
    log_level_group.add_argument('-v',
                                 '--verbose',
                                 action='store_const',
                                 const=logging.DEBUG,
                                 help='Verbose (debug) logging.',
                                 dest='log_level'
                                 )
    log_level_group.add_argument('-q',
                                 '--quiet',
                                 action='store_const',
                                 const=logging.WARNING,
                                 help='Quiet (warning) logging.',
                                 dest='log_level'
                                 )
    parser.add_argument('--version',
                        action='version',
                        version=('%(prog)s {version}'.format(version=__version__))
                        )
    parser.add_argument('--mip_era',
                        default='CMIP6',
                        type=str,
                        help='The MIP era (e.g. CMIP6)')
    parser.add_argument('--external_plugin',
                        default='',
                        type=str,
                        help='Module path to external CDDS plugin')
    parameters = parser.parse_args(args=args)

    load_plugin(parameters.mip_era, parameters.external_plugin)

    # Validate the parameters.
    check_file(parameters.config_file)
    return parameters
