# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
import logging
import re
from io import StringIO
import subprocess
import xml.sax
import xml.sax.handler

COMMAND_ID_NOT_FOUND = 'command-id not found'

""" Classes and methods to wrap moo commands.

Public classes:
    MassError -- raised when a MASS error requiring human intervention occurs
    RetryableMassError -- raised when a temporary MASS error occurs

Public methods:
    run_moo_cmd - runs specified moo command and returns output/errors
    is_mass_available - checks that MASS is available
    is_enabled - checks that the specified command type is being accepted
    parse_xml_output - parses XML output from run_moo_cmd
"""


class MassError(Exception):
    """ Raised when a moo command fails in a way that suggests there's
    an underlying problem that will take manual intervention to solve.
    In our case this is usually a "user error" indicating that, for
    instance, we've tried to fetch a directory that doesn't exist.
    """
    pass


class RetryableMassError(Exception):
    """ Raised when a moo command fails in a way that suggests it
    could work if re-run later (e.g. a "cmd type currently
    unavailable" return code).
    """
    pass


class SiHandler(xml.sax.ContentHandler):
    """ XML handler for parsing moo si -lx output. """

    def __init__(self):
        self._request_status = {}
        cmds = ["GET", "PUT", "SELECT", "MDLS"]
        self._queue_names = {}
        for cmd in cmds:
            queue_name = "%s commands enabled" % cmd
            self._queue_names[queue_name] = cmd.lower()

    @property
    def request_status(self):
        return self._request_status

    def startElement(self, name, attr):
        if name == "attribute":
            attr_name = attr.get("name", None)
            if attr_name in self._queue_names:
                queue_state = attr.get("value", None)
                cmd = self._queue_names[attr_name]
                self._request_status[cmd] = queue_state == "true"
        return


def run_moo_cmd(sub_cmd, args, simulation=False, logger=None):
    """ Runs a moo command.

    MOOSE errors are detected and classified into "can be retried
    later" or "error with the command that requires manual
    intervention to fix". An appropriate exception will be raised for
    either type of error. The exception will be initialised with the
    stdout and stderr from the command.

    Errors will be reported via logging.error calls. Successful
    commands will be reported via logging.info calls.

    Parameters
    ----------
    sub_cmd : str
        The moo command to run (e.g. "put").
    args : list
        Options and arguments to the command.
    simulation : bool, optional
        If true simulate moo command.
    logger : :class:`logging.Logger`, optional.
        Logger to use. If unset a logger will be obtained

    Returns
    -------
    : list of str
        Lines of standard output returned by moo command.

    Raises
    ------
    MassError
        If the command fails and the return code indicates that the
        command is not retryable (e.g. due to syntax error or data not
        being available).
    RetryableMassError
        If the command fails, but the return code indeicates that the
        command is retryable at a later time.
    """
    if logger is None:
        logger = logging.getLogger(__name__)
    cmd_to_run = ["moo", sub_cmd] + [str(i) for i in args]
    cmd_to_log = " ".join(cmd_to_run)
    if simulation:
        logger.info("simulating moo command \"{}\"".format(cmd_to_log))
        cmd_out = b""
    else:
        process = subprocess.Popen(cmd_to_run, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        (cmd_out, cmd_err) = process.communicate()
        command_id_search = re.search(rb"(command-id=\d+)", cmd_out)
        if command_id_search:
            command_id = command_id_search.group(0)
        else:
            command_id = COMMAND_ID_NOT_FOUND
        return_code = process.returncode
        if return_code != 0:
            log_msg = ("Moo command failed ({}):\n"
                       "  stdout: \"{}\"\n"
                       "  stderr: \"{}\"\n"
                       "".format(return_code, cmd_out, cmd_err))
            if _is_retryable(return_code):
                logger.error(log_msg)
                raise RetryableMassError('{}: {}'.format(command_id, cmd_err))
            else:
                logger.critical(log_msg)
                raise MassError('{}: {}'.format(command_id, cmd_err))
        else:
            logger.info("Successfully ran moo cmd \"{}\" (\"{}\")"
                        "".format(cmd_to_log, command_id))
    return cmd_out.decode().rstrip().split("\n")


def parse_xml_output(xml_output, content_handler):
    """ Parses XML output from a MOOSE command using xml.sax. Raises a
    MassError if parsing fails. Does not return any results - you need
    to set attributes in content_handler.

    Arguments:
    xml_output -- output from a moo command in XML format. (list of strs)
    content_handler -- handler for parsing XML (xml.sax.ContentHandler)
    """
    xml_parser = xml.sax.make_parser()
    xml_parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    xml_parser.setContentHandler(content_handler)
    try:
        xml_parser.parse(StringIO("\n".join(xml_output)))
    except xml.sax.SAXParseException as exc:
        raise MassError(
            "XML parser produced error: %s, from line %s, col %s" % (
                exc.getMessage(), exc.getLineNumber(),
                exc.getColumnNumber()))
    return


def _is_retryable(rc):
    # MOOSE return code 3 => system error, such as an outage.
    #                   5 => cmd type temporarily disabled.
    # A retry should be ok in either of these cases.
    return rc in [3, 5]
