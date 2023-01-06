# (C) British Crown Copyright 2019-2021, Met Office.
# Please see LICENSE.rst for license details.
"""
CDDS class for setting up and running Extract processes.
"""

import getpass
import logging
from cdds.extract.common import check_moo_cmd, exit_nicely, ValidationResult
from cdds.extract.constants import (GROUP_FOR_DIRECTORY_CREATION, MAX_EXTRACT_BLOCKS)
from cdds.extract.filters import Filters
from cdds.extract.process import Process


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
        extract_process = Process(self.lang, self.args)
        self.lang["requestname"] = extract_process.get_request_name()

        # log start of processing
        logger.info("EXTRACT PROCESS starting ---- ")
        logger.info(self.lang["user_settings"].format(
            getpass.getuser(), GROUP_FOR_DIRECTORY_CREATION))
        logger.info(extract_process.request_detail())

        # get data streams to be extracted - excludes streams to be skipped
        streams = extract_process.get_streams()

        num_streams = len(streams)
        if num_streams == 0:
            overall_summary = self.lang["stream_not_selected"]
            overall_result = "failed"
        else:
            # get output variables for request - configure MASS filters
            var_list = extract_process.configure_variables()

            # configure mappings for each variables
            mappings = Filters(
                extract_process.proc_directory,
                var_list,
                MAX_EXTRACT_BLOCKS,
                self.args.simulation
            )
            mapping_status = extract_process.configure_mappings(mappings)
            overall_summary = ""
            overall_result = "success"

        stream_validation = ValidationResult()
        stream_count = 0
        # the following loop will be ignored if num_streams == 0 (see above)
        for _, stream in enumerate(streams):
            # Skip the ancil stream as fixed fields are read from local files
            if stream == "ancil":
                logger.info(self.lang["stream_ancil"])
                continue
            # loop over streams in order requested, omit streams set to 'skip'
            stream["success"] = True
            stream_count += 1
            stream_validation.add_validation_result(stream["stream"])
            logger.info(
                self.lang["stream_start"].format(
                    stream["stream"], stream["start_date"],
                    stream["end_date"]))

            # process stream if no missing filters and check option is not skip
            if stream["stream"] in mapping_status:

                # get data source and target for this stream
                data_source = extract_process.get_data_source(stream)
                data_target = extract_process.get_data_target(stream)

                # check data stream exists in MASS
                if extract_process.request_exists(data_source):

                    # create directory for extracted data from this stream
                    extract_process.create_streamdir(data_target)

                    # create MOOSE filter filess (if requested)
                    # and mass commands
                    status, mass_cmd, err, stash_codes = (
                        extract_process.configure_commands(
                            mappings, stream, data_source, data_target))

                    # if status is skip OR mass_cmd is empty
                    # then skip this stream
                    if status == "skip" or not mass_cmd:
                        stream["success"] = False
                        overall_result = "failed"
                        logger.critical(
                            self.lang["stream_skip_data"].format(
                                stream["stream"], err
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
                                    stream["stream"], blocknum, block["start"],
                                    block["end"]))

                            code, output = extract_process.mass_request(block)
                            status = check_moo_cmd(code, output)
                            if status["val"] == "ok":
                                msg = self.lang["block_success"].format(
                                    blocknum, status["msg"])
                            else:
                                stream["success"] = False
                                overall_result = "quality"
                                msg = self.lang["block_fail"].format(
                                    blocknum, status["msg"])

                            logger.info(msg)

                            if status["val"] == "stop":
                                logger.info("{}: {}".format(
                                    self.lang["extract_failed"],
                                    self.lang["moose_fail"].format(
                                        status["code"], status["msg"])))
                                exit_nicely(self.lang["script_end"])

                        # ---- end of retrieve block loop ----

                else:
                    stream["success"] = False
                    overall_result = "failed"
                    stash_codes = {}
                # log stream completion and update progress in CREM
                logger.info(extract_process.stream_completion_message(
                    stream, "[{} of {}]".format(stream_count, num_streams)))
                # do validation check for this stream and write to log
                substreams = list(mappings.filters.keys())
                if not self.args.skip_extract_validation:
                    extract_process.validate(
                        data_target, stream, stash_codes, substreams,
                        stream_validation.validation_result(stream["stream"])
                    )
                    if not stream_validation.validation_result(stream["stream"]).valid:
                        overall_result = "quality"
            else:
                end_msg = "skipped [{} of {}]".format(stream_count,
                                                      num_streams)
                if stream["stream"] not in mapping_status:
                    end_msg += (" WARNING - there are no variables "
                                "requiring this stream")
                else:
                    stream["success"] = False
                    overall_result = "failed"
                logger.info(extract_process.stream_completion_message(
                    stream, end_msg))
            # ---- end of stream loop ----
        # log end of process
        logger.info("{}: {}".format(
            self.lang["extract_{}".format(overall_result)], overall_summary))
        if not self.args.skip_extract_validation:
            for stream_name, validation_result in stream_validation.validated_streams.items():
                validation_result.log_results(extract_process.log_directory)
        exit_nicely(
            msg=self.lang["script_end"],
            success=True if overall_result == "success" else False
        )
