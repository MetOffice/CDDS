# (C) British Crown Copyright 2016-2021, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = no-member
"""
Utility functions for extract processing.
"""

import logging
import sys
import pwd
import grp
import os
import subprocess
import re
from collections import defaultdict

from cdds.extract.constants import NUM_PP_HEADER_LINES, TIME_REGEXP
from hadsdk.common import run_command, retry


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


def get_stash_from_pp(filepath):
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

    stash = defaultdict(int)

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


def validate_stash_fields(path, stash_codes, validation_result):
    """Validates if pp files in a given location contain all required
    stash codes, and if the number of codes remains consistent in all files.

    Parameters
    ----------
    path : str
        path to directory of interest
    stash_codes : set
        A set of requried stash codes
    validation_result: hadsdk.common.StreamValidationResult
        An object to hold results from the stream validation
    """
    referencedict = ()
    for _, _, files in os.walk(path):
        if len(files) == 0:
            continue

        for datafile in sorted(files):
            if not datafile.endswith('.pp'):
                continue

            stash = get_stash_from_pp(os.path.join(path, datafile))
            if stash is None:
                validation_result.add_file_content_error(
                    FileContentError(os.path.join(path, datafile), "unreadable file"))
            else:
                if referencedict == ():
                    # populate stash reference dictionary
                    referencedict = (datafile, stash)
                    # test against provided stash_codes
                    # If there are entries in stash_codes (requested data)
                    # that are not in stash (data on disk) then flag up
                    # missing data
                    stash_diff = stash_codes.difference(set(stash.keys()))
                    if stash_diff:
                        error = StashError(os.path.join(path, datafile), "STASH errors")
                        for diff in stash_diff:
                            error.add_stash_error(diff)
                        validation_result.add_file_content_error(error)
                    # If there is additional data on disk that was not asked
                    # for then do nothing.
                # test against a reference dictionary
                elif referencedict[1] != stash:
                    error = StashError(os.path.join(path, datafile), "STASH errors relative to reference values")
                    for key, value in referencedict[1].items():
                        if key not in stash or stash[key] != value:
                            error.add_stash_error(key)
                    for key in stash:
                        if key not in referencedict[1]:
                            error.add_stash_error(key)
                    validation_result.add_file_content_error(error)


def run_moo_cmd(sub_cmd, args, simulate=False):
    """Executes a MOOSE command as a subprocess.

    Parameters
    ----------
    sub_cmd: str
        MOOSE command to be executed
    args : list
        List of arguments to the MOOSE command
    simulate: bool
        If True then moo comands will be simulated
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
    command = ["moo", sub_cmd] + args
    logger.info("moo command: '{}'".format(repr(command)))
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
                logger.info("moo output: '{}'".format(output.strip()))
            command_output += output
        return_code = process.returncode
    return return_code, command_output, command


def check_moo_cmd(code, output):
    """Interprets response from MOOSE command.
    Returns a status dict:

        val   str   subsequent action code - ok, skip, or stop
        code  str   code for status
        msg   str   message for logging purposes

    Parameters
    ----------
    code: int
        return code from MOOSE command
    output:str
        text output from MOOSE command

    Returns
    -------
    dict
        status value, code and user message
    """

    # default status
    status = {"val": "ok", "code": "request_ok", "msg": ""}

    # error config for code 2
    cfg2 = {
        "ERROR_CLIENT_PATH_ALREADY_EXISTS":
            {"val": "ok", "code": "already_exists",
             "msg": "some file(s) already existed"},
        "ERROR_CLIENT_PATH_DOES_NOT_EXIST":
            {"val": "stop", "code": "path_not_exist",
             "msg": "target directory does not exist"},
        "ERROR_CLIENT_INSUFFICIENT_DISK_SPACE":
            {"val": "stop", "code": "disk_space",
             "msg": "insufficient disk space available"},
        "TSSC_EXCEEDS_DATA_VOLUME_LIMIT":
            {"val": "skip", "code": "limit_exceeded", "msg": "volume too big"},
        "TSSC_EXCEEDS_FILE_NUMBER_LIMIT":
            {"val": "skip", "code": "limit_exceeded", "msg": "too many files"},
        "TSSC_SPANS_TOO_MANY_RESOURCES":
            {"val": "skip", "code": "limit_exceeded", "msg": "too many tapes"},
        "TSSC_QUERY_MATCHES_TOO_MANY_RESULTS":
            {"val": "skip", "code": "limit_exceeded",
             "msg": "too many results"},
        "TSSC_QUERY_MATCHES_NO_RESULTS":
            {"val": "skip", "code": "no_matches",
             "msg": "no matching files to retrieve"},
        "SSC_TASK_REJECTION":
            {"val": "skip", "code": "rejected", "msg": (
                "task rejected:\n{}".format(output))},
        "ERROR_TRANSFER":
            {"val": "stop", "code": "rejected", "msg": "data transfer error"}
    }

    # error config for code 3
    cfg3 = {
        "SSC_STORAGE_SYSTEM_UNAVAILABLE":
            {"val": "stop", "code": "system_unavailable",
             "msg": "storage system not available"},
        "ncks: ERROR":
            {"val": "skip", "code": "rejected",
             "msg": "error with ncks filtering "
                    "(possibly requested variable not found)"},
    }

    if code != 0 and code != 17:
        # default output
        status = {"val": "stop", "code": "rejected",
                  "msg": "moo command error (code: {})\noutput: {})".format(
                      code, output)}

        # check for specific code config matches
        if code == 2:
            errors = 0
            for key, value in cfg2.items():
                if key in output:
                    if key == "SSC_TASK_REJECTION" and errors > 0:
                        continue
                    status = value
                    # special case for no match on nc variable
                    if "does not match" in output:
                        status['val'] = "skip"
                        err_str = output.rpartition(
                            " is not in and/or does not match")
                        status['msg'] = \
                            "requested variable not found " \
                            "[{} and maybe others]".format(
                                err_str[0].split()[-1])
                    errors += 1
        elif code == 3:
            for key, value in cfg3.items():
                if key in output:
                    status = value

        else:
            status = {"val": "stop", "code": "other_error",
                      "msg": "unknown system error"}
    elif code == 17:
        status['msg'] = output
        status['code'] = 'already_exists'

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


@retry(exception=OSError, retries=3)
def create_dir(directory, permissions, user, group):
    """Creates directory path (unless it already exists) with requested
    ownership and permissions. Because of the @retry decorator
    the execution of the function will be attempted 3 times.

    Parameters
    ----------
    directory: str
        path for the directory to be created
    permissions: oct
        permissions in standard format (e.g 0775)
    user: str
        user name for file ownership permissions
    group: str
        group name for file ownership permissions

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
        uid = pwd.getpwnam(user).pw_uid
        gid = grp.getgrnam(group).gr_gid

        sep = os.sep
        subdirs = [subdir for subdir in directory.split(sep) if subdir]
        for subdir in subdirs:
            subdirpath = "{}{}{}".format(subdirpath, sep, subdir)
            if not os.path.exists(subdirpath):
                os.mkdir(subdirpath, permissions)
                os.chown(subdirpath, uid, gid)
                os.chmod(subdirpath, permissions)

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


def byteify(data, is_deep=False):
    """Converts a unicode structure to str.
    Used mainly to convert output from json.loads to a useful python
    structure. Requires Python 2.7 or above

    Parameters
    ----------
    data: mixed
        string, list or dict containing unicode structure
    is_deep: bool
        controls depth of dict conversion - currently only supports false

    Returns
    -------
    str
        string converted from unicode structure
    """
    # if this is a unicode string, return its string representation
    if isinstance(data, str):
        return data.encode("utf-8")
    # if this is a list of values, return list of byteified values
    if isinstance(data, list):
        return [byteify(item, True) for item in data]
    # if this is a dictionary, return dictionary of byteified keys and values
    # but only on highest level
    if isinstance(data, dict) and not is_deep:
        return {byteify(key, True): byteify(value, True) for
                key, value in data.items()}
    # if we do not know what it is, return it in its original form
    return data


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


def get_bounds_variables(stream, substream="default"):
    """Returns an array with additional bounds variables for ocean/sea ice fields

    Parameters
    ----------
    stream: str
        Stream name
    substream: str
        Substream name

    Returns
    -------
    list
        A list containing variables
    """
    try:
        return {
            ("onm", "grid-T"): [
                "bounds_lon", "bounds_lat", "time_centered_bounds",
                "deptht_bounds"
            ],
            ("onm", "diad-T"): [
                "bounds_lon", "bounds_lat", "time_centered_bounds",
                "deptht_bounds"
            ],
            ("onm", "ptrc-T"): [
                "bounds_lon", "bounds_lat", "time_centered_bounds",
                "deptht_bounds"
            ],
            ("onm", "ptrd-T"): [
                "bounds_lon", "bounds_lat", "time_centered_bounds",
                "deptht_bounds"
            ],
            ("onm", "grid-U"): [
                "bounds_lon", "bounds_lat", "time_centered_bounds",
                "depthu_bounds"
            ],
            ("onm", "grid-V"): [
                "bounds_lon", "bounds_lat", "time_centered_bounds",
                "depthv_bounds"
            ],
            ("onm", "grid-W"): [
                "bounds_lon", "bounds_lat", "time_centered_bounds",
                "depthw_bounds"
            ],
            ("ond", "grid-T"): [
                "bounds_lon", "bounds_lat", "time_centered_bounds",
            ],
            ("ond", "diad-T"): [
                "bounds_lon", "bounds_lat", "time_centered_bounds",
            ],
            ("ond", "ptrc-T"): [
                "bounds_lon", "bounds_lat", "time_centered_bounds",
            ],
            ("ond", "ptrd-T"): [
                "bounds_lon", "bounds_lat", "time_centered_bounds",
            ],
            ("ond", "scalar"): [
                "bounds_lon", "bounds_lat", "time_centered_bounds",
            ],
            ("inm", "default"): [
                "lont_bounds", "latt_bounds", "lonu_bounds", "latu_bounds"
            ],
            ("ind", "default"): [
                "lont_bounds", "latt_bounds", "lonu_bounds", "latu_bounds"
            ],
        }[stream, substream]
    except KeyError:
        return []


def get_model_resolution(model_name):
    """Returns a tuple with letter codes corresponding to atmos and ocean
    resolution

    Parameters
    ----------
    model_name: str
        Model name

    Returns
    -------
    tuple
        A tuple containing one-character codes, e.g. ('L','L')
    """
    return (model_name.split("-")[2][0], model_name.split("-")[2][1])


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


def calculate_period(date, start=True, file_size_in_days=10):
    """Accepts a tuple containing integer year, month and day, and returns
    a similar tuple which matches the datetime stamp of the file
    that starts or ends in that period.

    Parameters
    ----------
    date: tuple
        Date as (year, month, day)
    start: bool
        If True, will calculate a starting period, ending otherwise.
    file_size_in_days: int
        Temporal size of the file in days. Default value is 10 for N96,
        but it might be different for other configurations.
    Returns
    -------
    tuple
        A tuple containing (year, month, day) of the resulting date
    """
    year, month, day = date

    if not start and day == 1 and month == 1:
        year = year - 1
        month = 12
        day = 30 - file_size_in_days + 1
    else:
        day = ((day - 1) // file_size_in_days) * file_size_in_days + 1
    return year, month, day


class FileContentError(object):
    """
    Class representing a problematic file (usually an unreadable one).
    """
    def __init__(self, filepath, error_message):
        """
        Parameters
        ----------
        filepath: str
            Where the faulty file is stored.
        error_message: str
            What's wrong with the file.
        """
        self.filepath = filepath
        self.error_message = error_message


class StashError(FileContentError):
    """
    Class representing a problematic pp file with STASH errors.
    """
    def __init__(self, filepath, error_message):
        """
        Parameters
        ----------
        filepath: str
            Where the faulty file is stored.
        error_message: str
            What's wrong with the file.
        """
        super(StashError, self).__init__(filepath, error_message)
        self.stash_errors = []

    def add_stash_error(self, stash):
        """
        Adds a faulty stash code.

        Parameters
        ----------
        stash: str
            Faulty stash code.
        """
        self.stash_errors.append(stash)


class StreamValidationResult(object):
    """
    Encapsulates results from validation of a single stream.
    """
    def __init__(self, stream):
        """
        Constructor

        Parameters
        ----------
        stream: str
            Stream name
        """
        self.stream = stream
        self.file_count_expected = None
        self.file_count_actual = None
        self.file_errors = {}

    def add_file_counts(self, expected, actual):
        """
        Stores expected and actual file counts for a given stream.

        Parameters
        ----------
        expected: int
            Expected number of files in this stream

        actual: int
            Actual number of files in this stream
        """
        self.file_count_expected = expected
        self.file_count_actual = actual

    def add_file_content_error(self, file_content_error):
        """
        Adds a file content error to the results

        Parameters
        ----------
        file_content_error : cdds.extract.common.FileContentError
            Error to be added to the stream validation results.
        """
        self.file_errors[file_content_error.filepath] = file_content_error

    def log_results(self, log_directory):
        """
        Creates a log of issues for this stream (assuming there are any).

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
            logger.critical("Validation for stream {} has failed, please consult {} for details".format(
                self.stream, validation_report_filepath))
            with open(validation_report_filepath, "w") as fn:
                fn.write("Expected number of files: {}\n".format(self.file_count_expected))
                fn.write("Actual number of files: {}\n".format(self.file_count_actual))
                if self.file_errors:
                    fn.write("Problems detected with the following files:\n")
                    for _, file_error in self.file_errors.items():
                        fn.write("{}: {}\n".format(file_error.filepath, file_error.error_message))
                        if isinstance(file_error, StashError):
                            fn.write("\t\tSuspected STASH codes: {}\n".format(", ".join(file_error.stash_errors)))

    @property
    def valid(self):
        """
        Is this stream valid?

        Returns
        -------
        : bool
        """
        return self.file_count_actual == self.file_count_expected and not self.file_errors


class ValidationResult(object):
    """
    Encapsulates results from validation of pp and netcdf streams in Extract.
    """
    def __init__(self):
        """
        Constructor
        """
        self.validated_streams = {}

    def add_validation_result(self, stream):
        """
        Add validation result from a single stream

        Parameters
        ----------
        stream: str
            Stream name
        """
        self.validated_streams[stream] = StreamValidationResult(stream)

    def validation_result(self, stream):
        """
        Returns validation result for a single stream

        Parameters
        ----------
        stream: str
            Stream name

        Returns
        -------
        : cdds.extract.common.StreamValidationResult
        """
        return self.validated_streams[stream]


def stream_file_template(stream, suite_id):
    """
    Returns glob template for data files from particular stream.

    Parameters
    ----------
    stream: str
        Stream name
    suite_id: str
        Suite id (e.g. 'u-as744')

    Returns
    -------
    : list of str
        Glob templates.
    """
    if stream.startswith('ap'):
        filename_templates = ['{}a.p{}*'.format(suite_id.split('-')[1], stream[2]), ]
    elif stream.startswith('o'):
        filename_templates = ['nemo_{}o_1{}_*'.format(suite_id.split('-')[1], stream[2]),
                              'medusa_{}o_1{}_*'.format(suite_id.split('-')[1], stream[2])]
    elif stream.startswith('i'):
        filename_templates = ['cice_{}i_1{}_*'.format(suite_id.split('-')[1], stream[2])]
    else:
        raise InputError('Unknown stream type')
    return filename_templates


def build_mass_location(mass_data_class: str, suite_id: str, stream: str, streamtype: str,
                        mass_ensemble_member: str = None) -> str:
    """
    Returns root of the location of the dataset in MASS.

    Parameters
    ----------
        mass_root: str
            The root of the MASS location of a given dataset type
        suite_id: str
            Full suite id (e.g. u-as777)
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
        suiteid = "{}/{}".format(suite_id, mass_ensemble_member)
    else:
        suiteid = suite_id.split("/")[0]
    data_source = "moose:/{}/{}/{}.{}".format(mass_data_class, suiteid, stream, streamtype)
    if streamtype == "nc":
        data_source += ".file"
    return data_source
