# (C) British Crown Copyright 2019-2025, Met Office.
# Please see LICENSE.md for license details.
"""
CDDS class for setting up and running Extract processes.
"""

import getpass
import logging
import os
from cdds.common.request.request import read_request
from cdds.common.constants import INPUT_DATA_DIRECTORY
from cdds.extract.common import (
    check_moo_cmd, configure_mappings, configure_variables, exit_nicely, get_data_target,
    get_zero_sized_files, ValidationResult)
from cdds.extract.filters import Filters
from cdds.extract.process import Process
from cdds.common.plugins.plugins import PluginStore


class ExtractRunner(object):
    """
    Encapsulates configuration setup and triggering of CDDS Extract process.
    """

    def __init__(self, args, language):
        """Initialises runner object

        Parameters
        ----------
        args: :class:`argparse.Namespace` object
            The names of the command line arguments and their validated
            values.
        language: dict
            Dictionary containing message strings.
        """
        self.lang = language
        self.args = args

    def run_extract(self):
        """Main control sequence for extract process"""
        logger = logging.getLogger(__name__)
        # initialise extract_process and add project related configuration
        request = read_request(self.args.request)
        plugin = PluginStore.instance().get_plugin()
        proc_directory = plugin.proc_directory(request)
        input_data_dir = os.path.join(plugin.data_directory(request), INPUT_DATA_DIRECTORY)
        extract_process = Process(self.lang, self.args, request, input_data_dir)

        # log start of processing
        logger.info("EXTRACT PROCESS starting ---- ")
        logger.info(self.lang["user_settings"].format(
            getpass.getuser()))

        # get data streams to be extracted - excludes streams to be skipped
        streams = [stream for stream in request.data.streams if stream in self.args.streams
                   ] if self.args.streams else request.data.streams
        if not streams:
            overall_summary = self.lang["stream_not_selected"]
            overall_result = "failed"
        else:
            # get output variables for request - configure MASS filters
            var_list = configure_variables(os.path.join(proc_directory, 'prepare',
                                                        plugin.requested_variables_list_filename(request)))
            # configure mappings for each variables
            mappings = Filters(
                proc_directory,
                var_list,
                request.common.simulation
            )
            mappings.set_mappings(request)
            mapping_status = configure_mappings(mappings)
            overall_summary = ""
            overall_result = "success"

        stream_validation = ValidationResult()
        stream_count = 0
        stream_success = {}
        for stream in streams:
            stream_success[stream] = True
            # Skip the ancil stream as fixed fields are read from local files
            if stream == "ancil":
                logger.info(self.lang["stream_ancil"])
                continue
            # loop over streams in order requested, omit streams set to 'skip'
            stream_count += 1
            stream_validation.add_validation_result(stream)
            logger.info(
                self.lang["stream_start"].format(
                    stream, request.data.start_date,
                    request.data.end_date))

            # process stream if no missing filters and check option is not skip
            if stream in mapping_status:

                # get data source and target for this stream
                data_source = extract_process.get_data_source(stream)
                data_target = get_data_target(input_data_dir, request.data.model_workflow_id, stream)

                # check data stream exists in MASS
                if extract_process.request_exists(data_source):

                    # create directory for extracted data from this stream
                    extract_process.create_streamdir(data_target)

                    # test for presence of zero-sized files
                    files_to_delete = get_zero_sized_files(data_target)
                    extract_process.delete_files(files_to_delete)

                    # create MOOSE filter filess (if requested)
                    # and mass commands
                    status, mass_cmd, err, stash_codes = (
                        extract_process.configure_commands(
                            mappings, stream, data_source, data_target))

                    # if status is skip OR mass_cmd is empty
                    # then skip this stream
                    if status == "skip" or not mass_cmd:
                        overall_result = "failed"
                        logger.critical(
                            self.lang["stream_skip_data"].format(
                                stream, err
                            )
                        )

                    # submit one moose retrieval request (block)
                    # per period (pp) or substream (nc)
                    else:
                        blocknum = 0
                        for block in mass_cmd:
                            blocknum += 1

                            # log this MASS request
                            logger.info(
                                self.lang["block_start"].format(
                                    stream, blocknum, block["start"],
                                    block["end"]))

                            code, output = extract_process.mass_request(block)
                            status = check_moo_cmd(code, output)
                            if status == "ok":
                                msg = self.lang["block_success"].format(
                                    blocknum)
                            else:
                                stream_success[stream] = False
                                overall_result = "quality"
                                msg = self.lang["block_fail"].format(
                                    blocknum, output)

                            logger.info(msg)

                            if status == "stop":
                                logger.info("{}: {}".format(
                                    self.lang["extract_failed"],
                                    self.lang["moose_fail"].format(
                                        code, output)))
                                exit_nicely(self.lang["script_end"])

                        # ---- end of retrieve block loop ----

                else:
                    overall_result = "failed"
                    stash_codes = {}
                # log stream completion and update progress in CREM
                logger.info(extract_process.stream_completion_message(
                    stream, "[{} of {}]".format(stream_count, len(streams)), stream_success[stream]))
                # do validation check for this stream and write to log
                substreams = list(mappings.filters.keys())
            else:
                end_msg = "skipped [{} of {}]".format(stream_count,
                                                      len(streams))
                if stream not in mapping_status:
                    end_msg += (" WARNING - there are no variables "
                                "requiring this stream")
                else:
                    overall_result = "failed"
                logger.info(extract_process.stream_completion_message(
                    stream, end_msg, stream_success[stream]))
            # ---- end of stream loop ----
        # log end of process
        logger.info("{}: {}".format(
            self.lang["extract_{}".format(overall_result)], overall_summary))
        exit_nicely(
            msg=self.lang["script_end"],
            success=True if overall_result == "success" else False
        )
