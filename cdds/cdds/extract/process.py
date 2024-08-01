# (C) British Crown Copyright 2016-2022, Met Office.
# Please see LICENSE.rst for license details.
"""
CDDS class for accessing MASS archive through the moo API
"""

import os
import sys
import getpass
import datetime
import logging

from cdds.common.plugins.plugins import PluginStore
from cdds.extract.common import (
    build_mass_location, process_info, exit_nicely, create_dir,
    check_moo_cmd, run_moo_cmd, get_streamtype
)
from cdds.extract.constants import STREAMDIR_PERMISSIONS
from cdds.extract.filters import FilterFileException


class Process(object):
    """
    Provides CDDS extract methods for accessing the MASS archive through the
    moo API.

    Class supports filtered pp (select) and nc (filter) extractions.
    """

    def __init__(self, lang, args, request, input_data_directory):
        """Initialises extract object

        Parameters
        ----------
        lang: dict
            language strings for log messages etc
        opts: dict
            script options
        request: cdds.common.request.request.Request
            the request object
        input_data_directory: str
            path to the input data directory
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
        self.request = request
        self.input_data_directory = input_data_directory
        self.mass_data_class = self.request.data.mass_data_class
        model_id = self.request.metadata.model_id
        model_params = PluginStore.instance().get_plugin().models_parameters(model_id)
        self.stream_file_info = model_params.stream_file_info()
        # start log
        self.start_log()

    def start_log(self):
        """Starts log object and add some header info.

        """
        if self.args.streams is None:
            streams = ""
        else:
            streams = "--streams" + " " * 12 + ",".join(self.args.streams)
        simulation = "" if self.request.common.simulation is None else "--simulation"
        logger = logging.getLogger(__name__)
        logger.info(
            self.lang["arg_settings"].format(
                self.args.request,
                streams,
                self.request.common.root_proc_dir,
                self.request.common.root_data_dir,
                simulation
            )
        )
        # log process info
        logger.info(self.lang["script_info"].format(
            self.pinfo["pid"], self.pinfo["host"], self.pinfo["user"]))

    def stream_completion_message(self, stream, end_msg, success):
        """Returns a message marking the end of processing of each data stream

        Parameters
        ----------
        stream: dict
            stream attributes
        """
        if success:
            self.stream_summary[stream] = "ok"
            msg = self.lang["stream_end_success"].format(
                stream, end_msg)
        else:
            self.stream_summary[stream] = "fail"
            msg = self.lang["stream_end_fail"].format(
                stream, end_msg)
        return msg

    def request_detail(self):
        """Returns request details for logging.

        Returns
        -------
        : str
            Log message.
        """
        log_msg = self.lang["request_detail"].format(
            self.request.metadata.mip_era, self.request.metadata.mip,
            self.request.metadata.experiment_id, self.request.data.model_workflow_id,
            self.request.metadata.model_id,
            self.input_data_directory
        )
        log_msg += "\n       data streams:\n"
        for stream in self.request.data.streams:
            log_msg += self.lang["data_detail"].format(
                self.request.data.model_workflow_id, stream, get_streamtype(stream),
                self.request.data.start_date, self.request.data.end_date)
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
                data_target, STREAMDIR_PERMISSIONS)
        except OSError as exc:
            msg = ("Problem creating subdirectory {} in directory path {} [{} - [{}:{}]]".format(
                subdirpath, directory, os.strerror(exc.errno), user, group))
            status = "failed"
            success = False
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
            self.request.data.model_workflow_id,
            stream,
            get_streamtype(stream),
            self.request.data.mass_ensemble_member)

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
            mappings.format_filter(get_streamtype(stream), stream))

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

            try:
                status, mass_cmd, error, code = mappings.mass_command(
                    stream, data_source, data_target)
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
        logger = logging.getLogger(__name__)
        if code == 0 and output.strip() == 'true':
            msg = self.lang["stream_exists_ok"].format(request_source)
            exists = True
            logger.info(msg)
        else:
            msg = self.lang["stream_exists_fail"].format(
                request_source, code, output.strip())
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
                                       self.request.common.simulation)

        logger.debug(self.lang["moose_output"].format(
            code, cmd_out))
        return code, cmd_out

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
