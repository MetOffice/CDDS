# (C) British Crown Copyright 2016-2021, Met Office.
# Please see LICENSE.rst for license details.
"""
CDDS class for accessing MASS archive through the moo API
"""

import os
import sys
import getpass
import datetime
import logging
from operator import itemgetter

from cdds_common.cdds_plugins.plugins import PluginStore
from cdds_common.cdds_plugins.streams import StreamAttributes
from hadsdk.config import FullPaths
from hadsdk.constants import REQUIRED_KEYS_FOR_PROC_DIRECTORY
from hadsdk.request import read_request

from extract.common import (
    build_mass_location, process_info, exit_nicely, create_dir,
    check_moo_cmd, run_moo_cmd, file_accessible, file_count,
    validate_stash_fields, get_model_resolution, validate_netcdf
)
from extract.constants import GROUP_FOR_DIRECTORY_CREATION, STREAMDIR_PERMISSIONS
from extract.filters import FilterFileException
from extract.variables import Variables


class Process(object):
    """
    Provides CDDS extract methods for accessing the MASS archive through the
    moo API.

    Class supports filtered pp (select) and nc (filter) extractions.
    """

    def __init__(self, lang, args):
        """Initialises extract object

        Parameters
        ----------
        lang: dict
            language strings for log messages etc
        opts: dict
            script options
        """

        # set parameters for use in class
        self.args = args
        self.pinfo = process_info(sys.argv)

        self.lang = lang
        self.msg = ""
        self.faulty_filepaths = []

        # initialise standard values
        self.stream_summary = {}
        self.processtype = "extract"
        self.package = ""
        self.missing_var = []
        self.request_file = read_request(args.request,
                                         REQUIRED_KEYS_FOR_PROC_DIRECTORY)
        self.full_paths = FullPaths(args, self.request_file)

        self.proc_directory = self.full_paths.proc_directory
        self.data_directory = self.full_paths.data_directory
        self.input_data_directory = self.full_paths.input_data_directory
        self.log_directory = self.full_paths.log_directory("extract")
        self.mass_data_class = self.request_file.mass_data_class
        self.stream_info = PluginStore.instance().get_plugin().stream_info()
        # start log
        self.start_log()

    def start_log(self):
        """Starts log object and add some header info.

        """
        if self.args.streams is None:
            streams = ""
        else:
            streams = "--streams" + " " * 12 + ",".join(self.args.streams)
        simulation = "" if self.args.simulation is None else "--simulation"
        logger = logging.getLogger(__name__)
        logger.info(
            self.lang["arg_settings"].format(
                self.args.request,
                streams,
                self.args.root_proc_dir,
                self.args.root_data_dir,
                simulation
            )
        )
        # log process info
        logger.info(self.lang["script_info"].format(
            self.pinfo["pid"], self.pinfo["host"], self.pinfo["user"]))

    def stream_completion_message(self, stream, end_msg):
        """Returns a message marking the end of processing of each data stream

        Parameters
        ----------
        stream: dict
            stream attributes
        """
        if stream["success"]:
            self.stream_summary[stream["stream"]] = "ok"
            msg = self.lang["stream_end_success"].format(
                stream["stream"], end_msg)
        else:
            self.stream_summary[stream["stream"]] = "fail"
            msg = self.lang["stream_end_fail"].format(
                stream["stream"], end_msg)
        return msg

    def request_detail(self):
        """Returns request details for logging.

        Returns
        -------
        : str
            Log message.
        """
        log_msg = self.lang["request_detail"].format(
            self.request_file.mip_era, self.request_file.mip,
            self.request_file.experiment_id, self.request_file.suite_id,
            self.request_file.model_id,
            self.request_file.request_id,
            self.full_paths.input_data_directory
        )
        log_msg += "\n       data streams:\n"
        for key, item in self.request_file.streaminfo.items():
            log_msg += self.lang["data_detail"].format(
                self.request_file.suite_id, key, item["type"],
                item["start_date"], item["end_date"])
        return log_msg

    def create_streamdir(self, data_target, lcase=False):
        """Adds the specific stream directory paths to the target
        data directory for each data stream extracted.

        Parameters
        ----------
        data_target: str
            target directory for data from this request
        lcase: bool
            if true converts directory path elements to lowercase
        """
        logger = logging.getLogger(__name__)
        if lcase:
            data_target = data_target.lower()
        try:
            success, (status, msg) = create_dir(
                data_target, STREAMDIR_PERMISSIONS, getpass.getuser(),
                GROUP_FOR_DIRECTORY_CREATION)
        except OSError as exc:
            msg = ("Problem creating subdirectory {} in directory path {} [{} - [{}:{}]]".format(
                subdirpath, directory, os.strerror(exc.errno), user, group))
            status = "failed"
        if success and (status == "created" or status == "exists"):
            if status == "created":
                logger.info(
                    self.lang["dir_success"].format("datastream", ""))
            else:
                logger.info(
                    self.lang["dir_exists"].format("datastream"))
            logger.debug(msg)
        else:
            error = self.lang["dir_fail"].format(
                "stream", "", "", data_target, status, msg)
            exit_nicely(error)

    def get_data_source(self, stream):
        """Returns MOOSE source from request record

        Parameters
        ----------
        stream: dict
            stream attributes

        Returns
        -------
        str
            data source string for use in MOOSE commands
        """
        return build_mass_location(
            self.mass_data_class,
            self.request_file.suite_id,
            stream["stream"],
            stream["streamtype"],
            self.request_file.mass_ensemble_member)

    def get_data_target(self, stream):
        """Returns target location for extracted data

        Parameters
        ----------
        stream: dict
            stream attributes

        Returns
        -------
        str
            data target string for use in MOOSE commands
        """
        return os.path.join(
            self.input_data_directory, stream["suiteid"], stream["stream"])

    def get_request_name(self):
        """Returns request name from request record

        Returns
        -------
        str
            request name
        """
        return self.request_file.request_id

    def get_streams(self):
        """Creates list of streams
        Checks that all data streams are of the right type and returns stream
        info removing any streams that the user wishes to be skipped

        Returns
        -------
        list of dict
            attributes for each stream to be processed - dict per stream
        """

        streamlist = []
        for name, info in self.request_file.streaminfo.items():
            if not self.args.streams or name in self.args.streams:
                streamlist.append({
                    "stream": name,
                    "streamtype": info["type"],
                    "success": None,
                    "start_date":  datetime.datetime.strptime(
                        info["start_date"], "%Y-%m-%d-%H-%M-%S"),
                    "end_date": datetime.datetime.strptime(
                        info["end_date"], "%Y-%m-%d-%H-%M-%S"),
                    "suiteid": self.request_file.suite_id
                })
        return streamlist

    def configure_variables(self):
        """Gets required variable information for this request
        Gets configuration file from a json configuration file.
        Reformats the information into the structure required by the
        variable mapping API

        Returns
        -------
        list of dict
            variables in variable mapping API structure - dict per variable
        """
        logger = logging.getLogger(__name__)
        var = Variables(self.processtype)

        var_fn = os.path.join(
            self.full_paths.component_directory("prepare"),
            self.full_paths.requested_variables_list_filename)
        if not file_accessible(var_fn, "r"):
            error = self.lang["variables_file_missing"].format(
                var_fn, "file missing")
            exit_nicely(error)

        logger.info("Reading requested variables file '{}'".format(var_fn))
        # extract variables information from file
        variables = var.get_variables(var_fn)

        if not variables:
            error = self.lang["variables_file_missing"].format(
                var_fn, "file not readable")
            exit_nicely(error)

        # convert variables list to format variable mapping API is expecting
        var_list = var.create_variables_list(variables)

        # log request variables file reference
        logger.info(
            self.lang["variables_file_found"].format(
                os.path.basename(var_fn), variables["data_request_version"],
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
        logger.info("{}:{}\n".format(
            self.lang["variables_to_extract"], var_str))

        # log missing variables for which extraction will not be attempted

        missing = var.missing_variables_list()
        sorted_missing_list = sorted(missing, key=itemgetter("table"))
        table_key = ""
        var_str = ""

        for item in sorted_missing_list:
            if item["table"] != table_key:
                var_str += "\n{}:\n".format(item["table"])
                table_key = item["table"]

            var_str += " {:<25} - {}\n".format(item["name"],
                                               item["reason"])
        logger.debug("{}:\n{}".format(
            self.lang["variables_not_to_extract"], var_str))
        return var_list

    def configure_mappings(self, mappings):
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
        # set mappings
        _ = mappings.set_mappings(
            self.args.mip_table_dir, self.request_file)

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
            logger.info(self.lang["filter_missing"].format(msg))

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
                        var["var"], "[ {} ]".format(mip_table))

        if len(msg) > 0:
            logger.info(self.lang["filter_embargo"].format(msg))

        return stream_mapping

    def configure_commands(self, mappings, stream, data_source,
                           data_target):
        """Creates a set of MOOSE commands to retrieve stream files.
        In most cases there will be a single command - but multiple
        requests may be required if the data set covers more resources
        than a single request can handle

        Parameters
        ----------
        mappings: obj
            variable mapping information (CMIP var to stash/nc variable)
        stream: dict
            data stream attributes
        data_source: str
            MOOSE data source
        data_target: str
            MOOSE data target

        Returns
        -------
        str
            status information on subsequenct action to take [ok|skip|stop]
        list of dict
            MOOSE commands - dict per command
        str
            error messages
        set of str
            a set of short stash codes appearing in filters
        """
        # format filters for this stream
        logger = logging.getLogger(__name__)
        format_status, filter_msg, filter_msg_exc, stash_codes = (
            mappings.format_filter(stream["streamtype"], stream["stream"]))

        status = ""
        mass_cmd = ""
        error = ""
        if format_status:    # known format
            # report filters status
            log_msg = self.lang["filter_list"].format("VALID")
            for rec in filter_msg:
                log_msg += self.lang["filter_ok"].format(
                    rec["name"], rec["table"],
                    "constraint: {} ".format(rec["constraint"]),
                    rec["status"])
            logger.info(log_msg)

            if filter_msg_exc:

                # invalid mappings found - report
                log_msg = self.lang["filter_list"].format("INVALID")
                for rec in filter_msg_exc:
                    log_msg += self.lang["filter_not_ok"].format(
                        rec["name"], rec["table"], rec["reason"])
                logger.info(log_msg)

            resolution = get_model_resolution(
                self.request_file.model_id)[1]  # ocean resolution
            try:
                status, mass_cmd, error, code = mappings.mass_command(
                    stream, data_source, data_target, resolution)
            except FilterFileException as exc:
                errmsg = self.lang["dir_file_access_fail"].format(str(exc))
                exit_nicely(errmsg)

            if mass_cmd:
                log_msg = "MASS requests for this stream:\n"
                for cmd in mass_cmd:
                    log_msg += "  command --  {}\n".format(cmd)
                logger.debug(log_msg)
                if status == "ok" and code == "already_exists":
                    logger.debug(error)

            if status == "stop":
                errmsg = self.lang["stream_size_fail"].format(error)
                exit_nicely(errmsg)

        else:
            errmsg = self.lang["stream_type_invalid"].format(
                stream["streamtype"])
            exit_nicely(errmsg)

        return status, mass_cmd, error, stash_codes

    def request_exists(self, request_source):
        """Checks that requested data collection (stream) exists in MASS.

        Parameters
        ----------
        request_source: str
            MOOSE collection source for request

        Returns
        -------
        bool
            True if collection exists in MASS
        """
        cmd = {"moo_cmd": "test", "param_args": ["-d", request_source]}
        code, output = self.mass_request(cmd)
        status = check_moo_cmd(code, output)
        logger = logging.getLogger(__name__)
        if code == 0:
            msg = self.lang["stream_exists_ok"].format(request_source)
            exists = True
            logger.info(msg)
        else:
            msg = self.lang["stream_exists_fail"].format(
                request_source, code, status["msg"])
            exists = False
            logger.critical(msg)
        return exists

    def mass_request(self, cmd):
        """
        Submits a MOOSE request and returns the MOOSE return code and the
        terminal output.

        Parameters
        ----------
        cmd: dict
            MOOSE command and command parameters

        Returns
        -------
        int
            MOOSE return code
        list
            MOOSE terminal output
        """
        logger = logging.getLogger(__name__)
        logger.debug(self.lang["moose_request"].format(
            cmd["moo_cmd"], cmd["param_args"]))

        code, cmd_out, _ = run_moo_cmd(cmd["moo_cmd"],
                                       cmd["param_args"],
                                       self.args.simulation)

        logger.debug(self.lang["moose_output"].format(
            code, cmd_out))
        return code, cmd_out

    def validate(self, path, stream, stash_codes, substreams, validation_result):
        """Simple validation based on checking correct number of files have
        been extracted, and stash codes comparison in the case of pp streams.

        In the case of ncdf files, it tests if they can be opened at all.

        Parameters
        ----------
        path:str
            directory path containing files to validate
        stream:dict
            stream attributes
        stash_codes : set
            a set of short stash codes appearing in filters
        substreams: list
            list of substreams
        validation_result: hadsdk.common.StreamValidationResult
            An object to hold results from the stream validation
        """

        if stream["success"]:
            self.validate_file_count(path, stream, substreams, validation_result)
            if stream["streamtype"] == "pp":
                self.validate_pp(path, stash_codes, validation_result)
            elif stream["streamtype"] == "nc":
                self.validate_netcdf(path, validation_result)

    def validate_file_count(self, path, stream, substreams, validation_result):
        """
        Checks number of files present at a given location and
        validates it against values expected for a given stream
        and substream.

        Parameters
        ----------
        path: str
            Path to the dataset.
        stream: dict
            Stream description dictionary.
        substreams: list
            List of expected substreams.
        validation_result: hadsdk.common.StreamValidationResult
            An object to hold results from the stream validation
        """
        logger = logging.getLogger(__name__)
        # num files check
        logger.info("Checking file count")
        # count files of specific type in directory
        extension = ".{}".format(stream["streamtype"])
        actual = file_count(path, extension)
        # ocean resolution
        resolution = get_model_resolution(self.request_file.model_id)[1]
        stream_attribute = StreamAttributes(stream["stream"], stream["start_date"], stream["end_date"])
        expected = self.stream_info.calculate_expected_number_of_files(stream_attribute, substreams, resolution == "M")
        validation_result.add_file_counts(expected, actual)

    def validate_pp(self, path, stash_codes, validation_result):
        """
        Checks that PP files at provided location can be read and
        contain |STASH| codes consistent with the reference
        set given as a second argument.
        Returns overall validation status, error message(s),
        and a listof unreadable files (if present).

        Parameters
        ----------
        path: str
            Path pointing to the location of a set of PP files.
        stash_codes: set
            A set of unique |STASH| codes that the set of files will
            be validated against.
        validation_result: hadsdk.common.StreamValidationResult
            An object to hold results from the stream validation
        """
        logger = logging.getLogger(__name__)
        logger.info("Checking STASH fields")
        validate_stash_fields(path, stash_codes, validation_result)

    def validate_netcdf(self, path, validation_result):
        """
        Checks that |netCDF| files at provided location can be read.
        Returns overall validation status, error message(s), and a list
        of unreadable files (if present).

        Parameters
        ----------
        path: str
            Path pointing to the location of |netCDF| dataset.
        validation_result: hadsdk.common.StreamValidationResult
            An object to hold results from the stream validation
        """
        logger = logging.getLogger(__name__)
        logger.info("Checking netCDF files in \"{}\"".format(path))
        for root, _, files in os.walk(path):
            for datafile in sorted(files):
                error = validate_netcdf(os.path.join(root, datafile))
                if error is not None:
                    validation_result.add_file_content_error(error)

    def delete_files(self, files_to_remove):
        """
        Deletes files.

        Parameters
        ----------
        files_to_remove: list
            List of file paths pointing to files that ought to be removed.
        """
        logger = logging.getLogger(__name__)
        for file_path in files_to_remove:
            os.remove(file_path)
            logger.info("Deleted faulty file {}".format(file_path))
