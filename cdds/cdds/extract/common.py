# (C) British Crown Copyright 2016-2026, Met Office.
# Please see LICENSE.md for license details.
# pylint: disable = no-member
"""Utility functions for extract processing."""

import json
import logging
import os
import pwd
import re
import subprocess
import sys
from collections import defaultdict
from operator import itemgetter

from cdds.common import retry, run_command
from cdds.extract.constants import (
    MAX_MOOSE_LOG_MESSAGE,
    MOOSE_TAPE_PATTERN,
    NUM_PP_HEADER_LINES,
    STREAMTYPE_NC,
    STREAMTYPE_PP,
    TIME_REGEXP,
)
from cdds.extract.variables import Variables


def moose_date(when, mode):
    """Converts database or iso format date to MOOSE format dates.
    Converts database (1859-12-01 00:00:00) or iso (1859-12-01T00:00:00)
    format to a MOOSE format date(1859/12/01 00:00)

    Parameters
    ----------
    when: str
        input date (database or iso format)
    mode: str
        "datetime" if date includes time
    Returns
    -------
    str
        reformatted date
    """
    if mode == "datetime":
        when = when[:16]
    else:
        when = when[:10]
    return when.replace("-", "/").replace("T", " ")


def get_stash_from_pp(filepath) -> dict[str, int] | None:
    """Executes a ppfp command as a subprocess and parses the output
    to extract stash codes

    Parameters
    ----------
    filepath : str
        path to the pp file

    Returns
    -------
    set|None
        A set of stash codes from the file or None if the command fails
    """
    stash: dict = defaultdict(int)

    command = ["ppfp", "-stash", filepath]
    process = subprocess.Popen(command, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, universal_newlines=True)
    cmd_out = process.communicate()[0]
    if process.returncode > 0:
        return None
    else:
        for lines in cmd_out.split("\n")[NUM_PP_HEADER_LINES:]:
            try:
                int(lines)
                stash[lines.strip().lstrip("0")] += 1
            except ValueError:
                continue
        return stash


def run_moo_cmd(sub_cmd, args, simulate=False, verbose=True):
    """Executes a MOOSE command as a subprocess.

    Parameters
    ----------
    sub_cmd: str
        MOOSE command to be executed
    args : list
        List of arguments to the MOOSE command
    simulate: bool
        If True then moo comands will be simulated
    verbose: bool
        If True will dump moose commands as info instead of debug messages
    Returns
    -------
    int
        return code from subprocess invocation
    str
        text output from subprocess
    str
        command submitted
    """
    logger = logging.getLogger(__name__)
    if verbose:
        logger_cmd = logger.info
    else:
        logger_cmd = logger.debug
    command = ["moo", sub_cmd] + args
    to_log = repr(command)
    to_log = to_log[0:MAX_MOOSE_LOG_MESSAGE] + '...' if len(to_log) > MAX_MOOSE_LOG_MESSAGE else to_log
    logger_cmd("moo command: '{}'".format(to_log))
    if simulate:
        return_code = 0
        command_output = "SIMULATED"
    else:
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        command_output = ""
        while process.poll() is None:
            output = process.stdout.readline()
            if len(output) > 0:
                logger_cmd("moo output: '{}'".format(output.strip()))
            command_output += output
        return_code = process.returncode
    return return_code, command_output, command


def check_moo_cmd(code, output):
    """Interprets response from MOOSE command.
    Returns a status that specified an action - ok, skip or stop.

    Parameters
    ----------
    code: int
        return code from MOOSE command
    output:str
        text output from MOOSE command

    Returns
    -------
    str
        status value
    """

    # default status
    STOP_ERRORS = [
        'PATH_DOES_NOT_EXIST', 'INSUFFICIENT_DISK_SPACE', 'COLLECTION_DOES_NOT_EXIST', 'ERROR_TRANSFER',
        'STORAGE_SYSTEM_UNAVAILABLE', 'SINGLE_COPY_UNAVAILABLE', 'QUERY_MATCHES_NO_RESULTS'
    ]
    SKIP_ERRORS = [
        'EXCEEDS_DATA_VOLUME_LIMIT', 'EXCEEDS_FILE_NUMBER_LIMIT', 'SPANS_TOO_MANY_RESOURCES',
        'QUERY_MATCHES_TOO_MANY_RESULTS', 'does not match',
        'ncks: ERROR'
    ]
    OK_ERRORS = ['PATH_ALREADY_EXISTS']
    logger = logging.getLogger(__name__)
    if code == 0:
        status = 'ok'
    elif code == 2:
        if any(s in output for s in STOP_ERRORS):
            status = 'stop'
        elif any(s in output for s in SKIP_ERRORS):
            status = 'skip'
        elif any(s in output for s in OK_ERRORS):
            status = 'ok'
        else:
            # note that once new MOOSE User Guide is available it would be better to map all
            # codes and expected Extract behaviour explicitly
            status = 'stop'
    elif code == 3:
        if any(s in output for s in STOP_ERRORS):
            status = 'stop'
        elif any(s in output for s in SKIP_ERRORS):
            status = 'skip'
        else:
            logger.warning('An unknown error occurred. Stop application.')
            status = 'stop'
    elif code == 17:
        # already exists
        status = 'ok'
    else:
        status = 'stop'
    return status


def makefacetstring(facetmap, param, delimiter="/"):
    """Creates directory path from information facets.
    For example a facetmap of 'project|experiment|realisation'
    would be rendered to a facet string like 'ScenarioMIP/ssp_24/r1i1p1f1'

    Parameters
    ----------
    facetmap: str
        facet names separated with |
    param: dict
        parameters used to map facet name to value
    delimiter: str
        required delimiter character in the output string

    Returns
    -------
    str
        rendered facet string
    """
    facets = facetmap.split("|")
    facetvalues = []
    for value in facets:
        facetvalues.append(param[value])

    facet_str = delimiter.join(facetvalues)

    return facet_str


def exit_nicely(msg, success=False):
    """Common function for exiting from process.
    Includes appropriate logging.

    Parameters
    ----------
    msg: str
        message for user on exit
    success: bool
        whether process failed or not
    """
    logger = logging.getLogger(__name__)
    if not success:
        logger.critical("-- EXTRACT process exit: \n{} ".format(msg))
        sys.exit(1)
    else:
        logger.info("-- EXTRACT process exit: \n{} ".format(msg))


@retry(exception=OSError, retries=3)  # type: ignore
def create_dir(directory, permissions):
    """Creates directory path (unless it already exists) with requested
    ownership and permissions. Because of the @retry decorator
    the execution of the function will be attempted 3 times.

    Parameters
    ----------
    directory: str
        path for the directory to be created
    permissions: oct
        permissions in standard format (e.g 0775)

    Returns
    -------
    bool
        True if hasn't reached maximum number of retries
    tuple
        (status, message)
    """
    if os.path.exists(directory):
        msg = "Directory exists: {}".format(directory)
        status = "exists"
    else:
        subdirpath = ''

        sep = os.sep
        subdirs = [subdir for subdir in directory.split(sep) if subdir]
        for subdir in subdirs:
            subdirpath = "{}{}{}".format(subdirpath, sep, subdir)
            if not os.path.exists(subdirpath):
                os.mkdir(subdirpath, permissions)

        msg = "Directory created : {}".format(directory)
        status = "created"

    return status, msg


def conv_test_name(name):
    """Remove test suffix from name if necessary.

    Parameters
    ----------
    name: str
        name of entity

    Returns
    -------
    clean_name
        name with test suffix removed
    """
    pos = name.upper().rfind("-TEST")
    if pos > 0:
        clean_name = name[:pos]
    else:
        clean_name = name

    return clean_name


def file_accessible(filepath, mode):
    """Check if a file exists and is accessible.

    Parameters
    ----------
    filepath: str
        path for file of interest
    mode: str
        required access mode (e.g. 'r', 'w' etc.)

    Returns
    -------
    bool
        true if file exists and has requested access rights
    """
    try:
        fhandle = open(filepath, mode)
        fhandle.close()
    # except IOError as err:
    except IOError:
        return False

    return True


def file_count(path, extension):
    """Counts files in directory with specified extension.

    Parameters
    ----------
    path: str
        path to directory of interest
    extension: str
        extension of files to be included (e.g '.pp')

    Returns
    -------
    int
        no. of files in directory ending with specified extension
    """
    count = 0
    for _, _, files in os.walk(path):
        for datafile in files:
            if datafile.endswith(extension):
                count += 1
    return count


def merge_dicts(dict1, dict2):
    """Merges two python dictionaries.

    Parameters
    ----------
    dict1: dict
        first dictionary
    dict2: dict
        second dictionary

    Returns
    -------
    dict
        merged dictionary
    """
    merged_dict = dict1.copy()

    for key, val in dict2.items():
        if key not in dict1:
            merged_dict[key] = val
        else:
            for key2, val2 in val.items():
                if key2 not in dict1[key]:
                    merged_dict[key][key2] = val2
                else:
                    merged_dict[key][key2] += val2

    return merged_dict


def get_stash(fullstash):
    """Converts full UM stash definition to basic stash code.
    e.g. converts m01s15i226 to 15226

    Parameters
    ----------
    fullstash: str
        full stash definition
    Returns
    -------
    str
        short stash code
    """
    stash = fullstash[4:6].lstrip("0") + fullstash[7:10]
    return stash


def process_info(args):
    """Gets process information for current script.
    Process information returned includes script name, script path, user,
    pid, uid, and system details (name, host, release, version and
    architecture)

    Parameters
    ----------
    args: dict
        standard Python script args

    Returns
    -------
    dict
        process information
    """
    pinfo = {}

    pwdlist = pwd.getpwuid(os.geteuid())
    pinfo["script"] = os.path.basename(args[0])
    pinfo["scriptdir"] = os.path.dirname(args[0])
    pinfo["user"] = pwdlist[0]
    pinfo["uid"] = str(pwdlist[2])
    pinfo["pid"] = str(os.getpid())

    (pinfo["system"], pinfo["host"], pinfo["release"], pinfo["version"],
     pinfo["architecture"]) = os.uname()

    return pinfo


def validate_netcdf(filepath):
    """"Attempts to open a netCDF file, validates it, and returns
    a success/fail status

    Parameters
    ----------
    filepath: str
        File location

    Returns
    -------
    bool
        True if the file appears to be valid, false if not
    str
        Error message
    """
    error = None
    command = ['ncdump', '-h', filepath]
    try:
        output = run_command(command, exception=IOError)
        if not check_dimensions(output):
            error = FileContentError(filepath, "File has zero time length")
    except IOError:
        error = FileContentError(filepath, "File cannot be opened")
    return error


def check_dimensions(netcdf_headers):
    """Parses the |netCDF| metadata header and checks if `time` or
    `time_counter` variable has length greater than 0.

    Parameters
    ----------
    netcdf_headers: str
        |netCDF| file headers.

    Returns
    -------
    bool
        True if the file has a correct number of time steps
    """
    valid = False
    match = re.search(TIME_REGEXP, netcdf_headers)
    if match:
        try:
            if int(match.group(2)) > 0:
                valid = True
        except IndexError:
            pass
    return valid


def calculate_period(date, start=True):
    """Accepts a tuple containing integer year, month and day, and returns
    a similar tuple which matches the datetime stamp of the file
    that starts or ends in that period.

    Parameters
    ----------
    date: tuple
        Date as (year, month, day)
    start: bool
        If True, will calculate a starting period, ending otherwise.

    Returns
    -------
    tuple
        A tuple containing (year, month, day) of the resulting date
    """
    year, month, day = date

    if not start and day == 1 and month == 1:
        year = year - 1
        month = 12
        day = 30 + 1
    return year, month, day


class FileContentError(object):
    """Class representing a problematic file (usually an unreadable one)."""
    def __init__(self, filepath, error_message):
        """Parameters
        ----------
        filepath: str
            Where the faulty file is stored.
        error_message: str
            What's wrong with the file.
        """
        self.filepath = filepath
        self.error_message = error_message


class StashError(FileContentError):
    """Class representing a problematic pp file with STASH errors."""
    def __init__(self, filepath, error_message):
        """Parameters
        ----------
        filepath: str
            Where the faulty file is stored.
        error_message: str
            What's wrong with the file.
        """
        super(StashError, self).__init__(filepath, error_message)
        self.stash_errors = []

    def add_stash_error(self, stash):
        """Adds a faulty stash code.

        Parameters
        ----------
        stash: str
            Faulty stash code.
        """
        self.stash_errors.append(stash)


class StreamValidationResult(object):
    """Encapsulates results from validation of a single stream."""
    def __init__(self, stream):
        """Constructor

        Parameters
        ----------
        stream: str
            Stream name
        """
        self.stream = stream
        self.file_names_expected = None
        self.file_names_actual = None
        self.file_errors = {}
        self.mappings = None

    def add_mappings(self, mappings):
        """Adds mappings for this stream.

        Parameters
        ----------
        mappings: dict
            Mappings for this stream.
        """
        self.mappings = mappings

    def add_file_names(self, expected_files, actual_files):
        """Stores expected and actual files for a given stream.

        Parameters
        ----------
        expected: set
            Expected files in this stream

        actual: set
            Actual files in this stream
        """
        self.file_names_expected = expected_files
        self.file_names_actual = actual_files

    def add_file_content_error(self, file_content_error):
        """Adds a file content error to the results

        Parameters
        ----------
        file_content_error : cdds.extract.common.FileContentError
            Error to be added to the stream validation results.
        """
        self.file_errors[file_content_error.filepath] = file_content_error

    def log_results(self, log_directory):
        """Creates a log of issues for this stream (assuming there are any).

        Parameters
        ----------
        log_directory: str
            Path to the directory where the log file should be stored.
        """
        logger = logging.getLogger(__name__)
        validation_report_filepath = os.path.join(log_directory, "{}_validation.txt".format(self.stream))
        try:
            os.remove(validation_report_filepath)
            logger.info("Removed old validation report {}".format(validation_report_filepath))
        except OSError:
            pass
        if not self.valid:
            logger.critical("Validation for stream {} has failed, copy of the log saved in {}".format(
                self.stream, validation_report_filepath))
            with open(validation_report_filepath, "w") as fn:
                msg = ""
                missing_files = sorted(list(self.file_names_expected.difference(self.file_names_actual)))
                if missing_files:
                    msg += "{} Missing file(s):\n".format(len(missing_files))
                    for file in missing_files:
                        msg += f"{file}\n"

                additional_files = sorted(list(self.file_names_actual.difference(self.file_names_expected)))
                if additional_files:
                    msg += "{} Unexpected file(s):\n".format(len(additional_files))
                    for file in additional_files:
                        msg += f"{file}\n"

                if self.file_errors:
                    msg += "Problems detected with the following files:\n"
                    # Collect problematic STASH codes while reporting file errors
                    problematic_stash_codes = set()
                    for _, file_error in self.file_errors.items():
                        # breakpoint()
                        msg += "{}: {}\n".format(file_error.filepath, file_error.error_message)
                        if isinstance(file_error, StashError):
                            msg += "\t\tMissing STASH codes: {}\n".format(", ".join(file_error.stash_errors))
                            problematic_stash_codes.update(file_error.stash_errors)

                    # Cross-reference missing STASH with requested variables
                    affected_variables = self._get_affected_variables(problematic_stash_codes)
                    if affected_variables:
                        msg += "\nAs a result, these variables cannot be produced:\n"
                        for table in sorted(affected_variables.keys()):
                            var_list = ", ".join(sorted(affected_variables[table]))
                            msg += "\t{}: {}\n".format(table, var_list)

                fn.write(msg)
                logger.critical(msg)

    def _get_affected_variables(self, problematic_stash_codes):
        """Determines which variables cannot be produced due to file errors by cross-referencing
        the problematic STASH codes with the variable mappings for this stream. Requires that
        mappings have been set via add_mappings() before calling this method.

        Parameters
        ----------
        problematic_stash_codes : set
            Set of STASH codes that are missing or problematic in the data files

        Returns
        -------
        dict
            Dictionary mapping MIP table names to sets of affected variable names. Returns
            an empty dict if mappings are not set or the stream has no mappings.

        Raises
        ------
        RuntimeError
            If mappings have not been set for this stream validation result
        """
        affected_vars = defaultdict(set)

        # Ensure mappings have been set
        if self.mappings is None:
            logger = logging.getLogger(__name__)
            msg = logger.critical("Mappings not found for stream {}".format(self.stream))
            logger.critical(msg)
            raise RuntimeError(msg)

        # Get the mappings for this stream
        stream_mappings = self.mappings.get_mappings()
        if self.stream not in stream_mappings:
            return affected_vars

        # Check each variable's constraints against problematic STASH codes
        for var_dict in stream_mappings[self.stream]:
            if "constraint" not in var_dict:
                continue
            for constraint in var_dict["constraint"]:
                if "stash" in constraint:
                    # breakpoint()
                    stash = get_stash(constraint["stash"]).lstrip("0")
                    if stash in problematic_stash_codes:
                        var_name = var_dict.get("name")
                        mip_table = var_dict.get("table")
                        # Group by MIP table
                        affected_vars[mip_table].add(var_name)
                        break

        return affected_vars

    @property
    def valid(self):
        """Is this stream valid?

        Returns
        -------
        bool
        """
        return self.file_names_expected == self.file_names_actual and not self.file_errors


class ValidationResult(object):
    """Encapsulates results from validation of pp and netcdf streams in Extract."""
    def __init__(self):
        """Constructor"""
        self.validated_streams = {}

    def add_validation_result(self, stream):
        """Add validation result from a single stream

        Parameters
        ----------
        stream: str
            Stream name
        """
        self.validated_streams[stream] = StreamValidationResult(stream)

    def validation_result(self, stream):
        """Returns validation result for a single stream

        Parameters
        ----------
        stream: str
            Stream name

        Returns
        -------
        cdds.extract.common.StreamValidationResult
        """
        return self.validated_streams[stream]


def stream_file_template(stream, model_workflow_id):
    """Returns glob template for data files from particular stream.

    Parameters
    ----------
    stream: str
        Stream name
    model_worflow_id: str
        Workflow id (e.g. 'u-as744')

    Returns
    -------
    list of str
        Glob templates.
    """
    if stream.startswith('ap'):
        filename_templates = ['{}a.p{}*'.format(model_workflow_id.split('-')[1], stream[2]), ]
    elif stream.startswith('o'):
        filename_templates = ['nemo_{}o_1{}_*'.format(model_workflow_id.split('-')[1], stream[2]),
                              'medusa_{}o_1{}_*'.format(model_workflow_id.split('-')[1], stream[2])]
    elif stream.startswith('i'):
        filename_templates = ['cice_{}i_1{}_*'.format(model_workflow_id.split('-')[1], stream[2])]
    else:
        raise RuntimeError('Unknown stream type')
    return filename_templates


def build_mass_location(mass_data_class: str, model_workflow_id: str, stream: str, streamtype: str,
                        mass_ensemble_member: str = None) -> str:
    """Returns root of the location of the dataset in MASS.

    Parameters
    ----------
        mass_root: str
            The root of the MASS location of a given dataset type
        model_workflow_id: str
            Full model workflow id (e.g. u-as777)
        stream: str
            Stream name (e.g. ap4)
        streamtype: str
            Stream type, either pp or nc
        mass_ensemble_member: str
            Optional identifier of the ensemble member for PPE simulations

    Returns
    -------
        str: Location of the dataset
    """
    assert mass_data_class in ["crum", "ens"], "MASS data class must have a value of 'crum' or 'ens'"
    if mass_ensemble_member:
        workflowid = "{}/{}".format(model_workflow_id, mass_ensemble_member)
    else:
        workflowid = model_workflow_id.split("/")[0]
    data_source = "moose:/{}/{}/{}.{}".format(mass_data_class, workflowid, stream, streamtype)
    if streamtype == "nc":
        data_source += ".file"

    return data_source


def configure_variables(variable_file):
    """Gets required variable information for this request
    Gets configuration file from a json configuration file.
    Reformats the information into the structure required by the
    variable mapping API

    Parameters
    ----------
    variable_file: str
        Path to requested variables list.

    Returns
    -------
    list of dict
        variables in variable mapping API structure - dict per variable
    """
    logger = logging.getLogger(__name__)
    var = Variables("extract")

    if not file_accessible(variable_file, "r"):
        error = "CRITICAL: variables file [{}] not found]".format(variable_file)
        exit_nicely(error)

    logger.info("Reading requested variables file '{}'".format(variable_file))
    # extract variables information from file
    variables = var.get_variables(variable_file)

    if not variables:
        error = "CRITICAL: variables file [{}] not readable]".format(variable_file)
        exit_nicely(error)

    # convert variables list to format variable mapping API is expecting
    var_list = var.create_variables_list(variables)

    # log request variables file reference
    logger.info("""
    variables file specification
    - file:       {}
    - mip:        {}
    - experiment: {}""".format(
        os.path.basename(variable_file),
        variables["mip"], variables["experiment_id"]))

    # log requested variables for which extraction will be attempted
    sorted_var_list = sorted(var_list, key=itemgetter("table"))
    table_key = ""
    var_str = ""
    for item in sorted_var_list:
        if item["table"] != table_key:
            var_str += "\n\n{:<12}:  ".format(item["table"])
            table_key = item["table"]
        var_str += item["name"] + " "
    logger.info("Variables requested for processing - by stream:{}\n".format(var_str))

    # log missing variables for which extraction will not be attempted
    missing = var.missing_variables_list()
    sorted_missing_list = sorted(missing, key=itemgetter("table"))
    table_key = ""
    var_str = ""
    for item in sorted_missing_list:
        if item["table"] != table_key:
            var_str += "\n{}:\n".format(item["table"])
            table_key = item["table"]
        var_str += " {:<25} - {}\n".format(item["name"], item["reason"])
    logger.debug("Variables NOT requested for processing (with reason):\n{}".format(var_str))
    return var_list


def configure_mappings(mappings):
    """Get mappings for variables.
    Reports missing mappings to the log file.

    Parameters
    ----------
    mappings: obj
        variable mapping information (CMIP var to stash/nc variable)

    Returns
    -------
    dict
        contains bool element for each stream - if false there are
        mappings missing for the stream
    """
    logger = logging.getLogger(__name__)
    # log missing mappings and set return dict
    stream_mapping = {}
    msg = ""
    missing = mappings.get_missing_mappings()
    for stream in missing:
        if len(missing.get(stream)) > 0:
            stream_mapping[stream] = False
            msg += "STREAM: {}\n".format(stream)
            for var in missing.get(stream):
                if "table" in var:
                    mip_table = var["table"]
                else:
                    mip_table = " - "
                msg += " {:<15} {:<15} : {}\n".format(
                    var["var"], "[ {} ]".format(mip_table), var["reason"])
        else:
            stream_mapping[stream] = True

    if len(msg) > 0:
        logger.info("\n ----- Missing Variable Mappings -----\n{} \n".format(msg))

    msg = ""
    embargoed = mappings.get_embargoed_mappings()
    for stream in embargoed:
        if len(embargoed.get(stream)) > 0:
            msg += "STREAM: {}\n".format(stream)
            for var in embargoed.get(stream):
                if "table" in var:
                    mip_table = var["table"]
                else:
                    mip_table = " - "
                msg += " {:<15} {:<15}\n".format(
                    var["var"], "[ {},@{} ]".format(mip_table, var["frequency"]))

    if len(msg) > 0:
        logger.info("\n ----- Embargoed Variable Mappings -----\n{} \n".format(msg))

    return stream_mapping


def get_data_target(input_data_directory, model_workflow_id, stream):
    """Returns target location for extracted data

    Parameters
    ----------
    input_data_directory: str
        directory with model input data
    model_workflow_id: str
        model workflow id
    stream: str
        stream name

    Returns
    -------
    str
        data target string for use in MOOSE commands
    """
    return os.path.join(input_data_directory, model_workflow_id, stream)


def fetch_filelist_from_mass(mass_dir, simulation=False):
    """Retrieves a list of files stored in a MASS directory along with the tape number

    Parameters
    ----------
    mass_dir: str
        name of a MASS directory

    Returns
    -------
    list
        List of tuples (tape, filename)
    error
        An error output from MOOSE
    """
    files = []
    error = None
    if not simulation:
        try:
            cmd_out = run_command(["moo", "ls", "-m", mass_dir])
            filelines = cmd_out.split('\n')[0:-1]
            for fileline in filelines:
                try:
                    _, tape, _, _, _, filepath = fileline.split()
                    files.append((tape, filepath))
                except ValueError:
                    # skip files which hasn't been completely written to the tape system yet
                    pass
        except RuntimeError as e:
            files = []
            error = str(e)
    return files, error


def get_tape_limit(tape_msg_pattern=MOOSE_TAPE_PATTERN, simulation=False):
    """Retrieves a current tape limit from MASS

    Parameters
    ----------
    tape_msg_pattern: str
        regular expression matching message containing information about the MASS system
    simulation: bool
        if True no real interaction with MASS will happen

    Returns
    -------
    int
        Tape limit
    error
        An error output from MOOSE
    """

    limit = None
    if simulation:
        limit = 50
        error = None
    else:
        try:
            cmd_out = run_command(["moo", "si", "-v"])
            search = re.search(tape_msg_pattern, cmd_out)
            if not search:
                error = 'Could not determine tape limit'
            else:
                limit = int(search.group(1))
                error = None
        except RuntimeError as e:
            limit = None
            error = str(e)
    return limit, error


def chunk_by_files_and_tapes(fileset: dict, tape_limit: int, file_limit: int) -> list:
    """Divides the filelist dictionary into chunks ensuring that each chunk doesn't exceed the file number limit and
    the number of tapes accessed in each chunk doesn't exceed the tape limit.

    Parameters
    ----------
    fileset: dict
        A dictionary of filenames lists indexed by their tape identifier
    tape_limit: int
        Maximum number of tapes that can be accessed in a single moo filter request
    file_limit: int
        Maximum number of files that can be fetched in a single moo filter request

    Returns
    -------
    list
        List of chunked lists of filenames
    """
    tapes: set = set()
    current_chunk: list[str] = []
    chunks = []
    for tape_id, files in fileset.items():
        for file in files:
            # If adding another file will exceed tape threshold or we've hit the file limit save the chunk
            if len(tapes | set([tape_id])) > tape_limit or len(current_chunk) == file_limit:
                chunks.append(current_chunk)
                tapes = set()
                current_chunk = []
            tapes.add(tape_id)
            current_chunk.append(file)
    # Add the final chunk
    if current_chunk:
        chunks.append(current_chunk)
    return chunks


def get_zero_sized_files(dirpath: str) -> list:
    """Checks if a given directory contain files of zero size and returns them.

    Parameters
    ----------
    dirpath : str
        Directory to be checked

    Returns
    -------
    list
        List of files to be deleted
    """
    files_to_remove = []
    for _, _, files in os.walk(dirpath):
        for datafile in files:
            filepath = os.path.join(dirpath, datafile)
            if os.path.getsize(filepath) == 0:
                files_to_remove.append(filepath)
        break
    return files_to_remove


def get_streamtype(stream: str) -> str:
    """A helper function to determine stream type based on its name.

    Parameters
    ----------
    stream : str
        Stream name

    Returns
    -------
    str
        'pp' or 'nc'
    """
    if 'ap' in stream:
        return STREAMTYPE_PP
    else:
        return STREAMTYPE_NC


def condense_constraints(variable_constraints) -> dict:
    """Processes a list of dictionaries containing constraints and condenses them by
    grouping instances where multiple stash codes correspond to the same constraint
    attributes.

    Parameters
    ----------
    variable_constraints : list
        A list of dictionaries, where each dictionary contains a 'constraint' key
        with a list of constraint specifications.

    Returns
    -------
    condensed_constraints : collections.defaultdict[set]
        A defaultdict where the keys are hashed representations of constraints and the
        values are sets of 'stash' values corresponding to those constraints.
    """
    logger = logging.getLogger(__name__)
    condensed_constraints = defaultdict(set)

    for variable in variable_constraints:
        for constraint in variable["constraint"]:
            if "stash" not in constraint:
                logger.critical("Constraint without stash found: {}".format(constraint))
                continue
            stash = constraint["stash"]
            # Create a copy and remove stash for grouping whilst avoiding mutating the
            # original (needed to ensure stash codes appear in logs).
            constraint_without_stash = constraint.copy()
            constraint_without_stash.pop("stash")
            hashed_constraint = json.dumps(constraint_without_stash, sort_keys=True)
            condensed_constraints[hashed_constraint].add(stash)

    return condensed_constraints
