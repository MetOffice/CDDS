# (C) British Crown Copyright 2016-2023, Met Office.
# Please see LICENSE.rst for license details.
"""
Class for creating MOOSE commands for filtered retrievals from MASS
using SELECT and FILTER

"""

import datetime
import logging
import re
from collections import defaultdict
from operator import itemgetter
from typing import Dict, List, Tuple

from cdds.common import netCDF_regexp, generate_datestamps_pp
from cdds.common.mappings.mapping import ModelToMip
from cdds.common.mass import mass_list_dir
from cdds.common.plugins.grid import GridType
from cdds.common.plugins.plugins import PluginStore
from cdds.extract.common import (check_moo_cmd, chunk_by_files_and_tapes, fetch_filelist_from_mass,
                                 get_bounds_variables, get_stash, get_tape_limit, run_moo_cmd)
from cdds.extract.constants import GRID_LOOKUPS, MOOSE_MAX_NC_FILES


class Filters(object):
    """
    Creates MOOSE commands for filtered retrievals from MASS
    using SELECT (PP files) and FILTER (netcdf files)
    """

    def __init__(self, procdir=None, var_list=None,
                 simulation=False):
        """Initialises Filters object

        Parameters
        ----------
        procdir: str
            pathname to extract processing directory
        var_list: list of dict
            list of variables (dicts) to be processed
        simulation: bool
            If true MASS commands will be simulated

        """
        self.source = ""
        self.target = ""
        self.procdir = procdir
        self.stream = ""

        self.var_status = ""
        self.var_list = {"variables": var_list}
        self.mappings = {}
        self.mappings_missing = {}
        self.mappings_embargoed = {}
        self.simulation = simulation
        self.filters = {}
        self.mass_cmd = []
        self.suite_id = None
        self.ensemble_member_id = None
        self.model_id = None

        self.plugin = None
        self.model_parameters = None

    def set_mappings(self, mip_table_dir, request):
        """Get the |model to MIP mappings|.

        Parameters
        ----------
        mip_table_dir: str
            pathname to directory holding mip tables for this request
        request: cdds.common.request.Request
            key science parameter values for this request

        Returns
        -------
        bool
            true if all mappings configured, else false
        """
        self.model_id = request.model_id
        self.plugin = PluginStore.instance().get_plugin()
        self.model_parameters = self.plugin.models_parameters(self.model_id)
        # initialise mappings request structure
        mapping_request = {
            "process": {
                "type": "extract_filters", "tabledir": mip_table_dir
            },
            "science": {"mip_era": request.mip_era,
                        "mip": request.mip,
                        "model_id": request.model_id,
                        "model_ver": self.model_parameters.model_version,
                        "experiment_id": request.experiment_id,
                        "suite_id": request.suite_id}
        }
        self.suite_id = request.suite_id
        self.ensemble_member_id = request.mass_ensemble_member
        # add list of requested variables to request structure
        mapping_request.update(self.var_list)

        # encode request structure as json string
        json_in = mapping_request

        # get configured filters
        mapping = ModelToMip(json_in)
        json_out = mapping.mass_filters()

        # remove variables that have unknown mappings and/or streams
        status = True
        for key, value in json_out.items():
            self.mappings_missing[key] = []
            # if unknown stream - all mappings are missing
            if key == "unknown":
                for var in value:
                    status = False
                    self.mappings_missing[key].append(
                        {"var": var["name"], "reason": "stream not known"})

            # known stream - include all mappings that are ok or embargoed
            # [avoids having to rerun extract if mappings are released]
            else:    # known stream - check for unknown mappings
                self.mappings[key] = []
                self.mappings_embargoed[key] = []
                for var in value:
                    if var["status"] != "ok" and var["status"] != "embargoed":
                        status = False
                        self.mappings_missing[key].append(
                            {"table": var["table"], "var": var["name"],
                             "reason": "stash mapping not known"})
                    else:
                        self.mappings[key].append(var)
                        if var["status"] == "embargoed":
                            self.mappings_embargoed[key].append(
                                {
                                    "table": var["table"],
                                    "var": var["name"]
                                }
                            )

        return status

    def get_mappings(self):
        """Returns mappings for the data request.

        Returns
        -------
        dict
            mappings - dict per mapping
        """
        return self.mappings

    def get_missing_mappings(self):
        """Returns missing mappings for the data request.

        Returns
        -------
        dict
            missing mappings - dict per mapping
        """
        return self.mappings_missing

    def get_embargoed_mappings(self):
        """Returns embargoed mappings for the data request

        Returns
        -------
        dict
            embargoed mappings - dict per mapping
        """
        return self.mappings_embargoed

    def format_filter(self, streamtype, stream):
        """Manages the formatting of variable mappings into MOOSE filters for the
        various types of data stream.

        Parameters
        ----------
        streamtype: str
            code for stream data type(e.g. pp)
        stream: str
            code name for stream (e.g. apm)

        Returns
        -------
        bool
            true if stream data type is supported
        list of dict
            details of variable mappings for reporting - dict per variable
        list of dict
            details of missing variable mappings for reporting
            - dict per variable
        set of str
            a set of short stash codes appearing in pp filters
        """
        status = False
        filter_msg = []
        filter_msg_exc = []
        stash_codes = None
        if streamtype == "pp":
            filter_msg, filter_msg_exc, stash_codes = (
                self._format_filter_pp(stream)
            )
            status = True

        elif streamtype == "nc":
            filter_msg, filter_msg_exc = (
                self._format_filter_nc(stream)
            )
            status = True

        return status, filter_msg, filter_msg_exc, stash_codes

    def mass_command(self, stream, source, target):
        """Manages the creation of MASS commands and associated filter files
        for the various types of data stream supported by CDDS.

        Parameters
        ----------
        stream: dict
            code name for stream (e.g. onm)
        source: str
            MASS source location (incl wildcards if appropriate)
        target: str
            pathname for directory to hold extracted data

        Returns
        -------
        bool
            true if MASS extraction commands created
        list of dict
            list of MOOSE requests for extraction of data stream - dict
            per request.
        str
            error message
        str
            status code
        """

        status = False
        error = ""
        self.source = source
        self.target = target
        self.stream = stream["stream"]
        code = None
        if stream["streamtype"] == "pp":
            status, self.mass_cmd, error, code = self._mass_cmd_pp(
                stream["start_date"], stream["end_date"])
        elif stream["streamtype"] == "nc":
            status, self.mass_cmd, error, code = self._mass_cmd_nc(
                stream["start_date"], stream["end_date"])

        return status, self.mass_cmd, error, code

# ----- PP specialisation methods ---------------------------------------------
    def _format_filter_pp(self, stream):
        """
        Format mapping information for pp data into MASS filter format.

        Parameters
        ----------
        stream: str
            code name for stream (e.g. apm)

        Returns
        -------
        list of dict
            list of configured MOOSE filters - dict per filter
        list of dict
            list of missing filters for requested variables - dict
            per missing filter
        set of str
            a set of short stash codes appearing in filters
        """
        filter_msg = []
        filter_msg_exc = []
        stash_codes = set()
        self.filters = {stream: ""}

        # check if variables/mappings are defined for this data stream
        if self.mappings.get(stream):
            # loop over variables/mappings for this stream
            # include embargoed mappings

            for var in self.mappings.get(stream):
                if var.get("constraint") is None:
                    filter_msg_exc.append(
                        {"name": var["name"], "table": var["table"],
                         "reason": "no mapping details specified"})
                elif var.get("status") is None:
                    filter_msg_exc.append(
                        {"name": var["name"], "table": var["table"],
                         "reason": "filter status not specified"})
                elif self._detect_nc_in_pp(var):
                    filter_msg_exc.append(
                        {"name": var["name"], "table": var["table"],
                         "reason": "netCDF mapping"})
                elif var["status"] in ["ok", "embargoed"]:
                    filter_msg.append(var)

                    # create filter block from constraint
                    for constraint in var["constraint"]:
                        filter_block = "begin\n"
                        for k, val in constraint.items():
                            if k == "stash":
                                filter_block += " {}={}\n".format(
                                    k, get_stash(val))
                                stash_codes.add(get_stash(val).lstrip("0"))
                            else:
                                if isinstance(val, list):
                                    val = tuple(val)
                                filter_block += " {}={}\n".format(
                                    k, val)

                        filter_block += "end\n"
                        self.filters[stream] += filter_block
                else:
                    filter_msg_exc.append(
                        {"name": var["name"], "table": var["table"],
                         "reason": "filter status invalid"})

        # sort variables in filter missing filter lists
        filter_msg = sorted(filter_msg, key=lambda y: y["name"])
        filter_msg_exc = sorted(filter_msg_exc, key=lambda y: y["name"])
        return filter_msg, filter_msg_exc, stash_codes

    def _detect_nc_in_pp(self, var):
        """Checks if a stream mapping contains a ncdf variable

        Parameters
        ----------
        var: dict
            Variable mapping entry from ModelToMip, e.g.
            {"name": "tas", "status": "ok", "table": "Amon", "constraint": []}

        Returns
        -------
        bool
            True if doesn't contain stash mapping
        """
        try:
            return not bool(
                [constr for constr in var["constraint"] if "stash" in constr]
            )
        except IndexError:
            return False

    def _chunk_pp_filelist(self, pp_filelist: List[Dict]) -> List[List[Dict]]:
        """Recursively split a pp_filelist into chunks that will not exceed moose
        resource limits.

        :param pp_filelist: A pp_filelist
        :type pp_filelist: List[Dict]
        :raises: RecursionError If too many calls made.
        :return: A list of pp_filelist chunks
        :rtype: List[List[Dict]]
        """
        self.call_counter = 0
        self.call_limit = 20

        def generate_chunks(chunk):
            self.call_counter += 1
            if self.call_counter > self.call_limit:
                raise RecursionError

            test_file = self._create_filterfile_pp(chunk, test_mode=True)
            valid, _ = self._check_block_size_pp(test_file, override_simulate=True)
            if valid["val"] == "ok":
                return [chunk]

            mid_point = len(chunk) // 2
            sub_chunk_1, sub_chunk_2 = chunk[:mid_point], chunk[mid_point:]

            return generate_chunks(sub_chunk_1) + generate_chunks(sub_chunk_2)

        return generate_chunks(pp_filelist)

    def _generate_filenames_pp(self, datestamps: List[str]) -> List[str]:
        """Generate .pp filenames. Accounts for cases where ensemble id is
        used in the filename by running a `moo ls` on the source directory
        and checking the returned filenames.

        :param datestamps: List of datestamps
        :type datestamps: List[str]
        :return: List of .pp filenames
        :rtype: Tuple[List[str], List[str]]
        """
        suite = self.suite_id.split("-")[1]
        stream_id = self.stream[-1]

        if self.ensemble_member_id:
            suite = "{}-{}".format(suite, self.ensemble_member_id)

            command_output = mass_list_dir(self.source, False)
            if suite not in command_output[0]:
                suite = self.suite_id.split("-")[1]

        filenames = [f"{suite}a.p{stream_id}{date}.pp"for date in datestamps]

        return filenames

    def _pp_file_string(self, pp_filelist: List[dict], file_frequency: str) -> str:
        """Given a pp_file list, construct the appropriate pp_file value for a select
        filter file, accounting for any partial years in the case of monthly or seasonal
        files.

        :param pp_filelist: A pp_filelist
        :type pp_filelist: List[dict]
        :param file_frequency: The time range overed by the pp files
        :type file_frequency: str
        :return: A pp_file string for use in a filterfile
        :rtype: str
        """

        pp_filelist = sorted(pp_filelist, key=itemgetter("timepoint"))

        # Lexicographic sort works on these files frequencies without intervention i.e.
        # partial years do not need to be treated as a special case.
        if file_frequency in ["10 day", "daily"]:
            return f'["{pp_filelist[0]["filename"]}".."{pp_filelist[-1]["filename"]}"]'

        if file_frequency == "monthly":
            start, end = 1, 12
        elif file_frequency == "season":
            start, end = 3, 12

        start_date, end_date = pp_filelist[0]["timepoint"], pp_filelist[-1]["timepoint"]

        leading_trailing_files = []

        if start_date.month_of_year != start:
            leading_trailing_files += [file["filename"]
                                       for file in pp_filelist
                                       if file["timepoint"].year == start_date.year]
            pp_filelist = [file for file in pp_filelist if file["timepoint"].year != start_date.year]
        if end_date.month_of_year != end:
            leading_trailing_files += [file["filename"]
                                       for file in pp_filelist
                                       if file["timepoint"].year == end_date.year]
            pp_filelist = [file for file in pp_filelist if file["timepoint"].year != end_date.year]

        pp_filelist_string, individual_files_string = "", ""

        if pp_filelist:
            pp_filelist = sorted(pp_filelist, key=itemgetter("filename"))
            pp_filelist_string = f'["{pp_filelist[0]["filename"]}".."{pp_filelist[-1]["filename"]}"]'

        if leading_trailing_files:
            leading_trailing_files = [f'"{file}"' for file in leading_trailing_files]
            individual_files_string = ', '.join(leading_trailing_files)

        if pp_filelist_string and individual_files_string:
            pp_file = f"({pp_filelist_string}, {individual_files_string})"
        elif pp_filelist_string:
            pp_file = pp_filelist_string
        elif individual_files_string:
            if len(leading_trailing_files) > 1:
                pp_file = f"({individual_files_string})"
            else:
                pp_file = f"{individual_files_string}"

        return pp_file

    def _create_pp_filelist(self, start: str, end: str) -> List[Dict]:
        """Create a list of expected .pp files where each file is represented
        as a dictionary with two values, TimePoint and filename.

        :param start: Start run bound
        :type start: str
        :param end: End run bound
        :type end: str
        :return: A pp_filelist
        :rtype: List[Dict]
        """
        file_frequency = self.model_parameters._stream_file_info.file_frequencies[self.stream].frequency
        datestamps, timepoints = generate_datestamps_pp(start, end, file_frequency)
        filenames = self._generate_filenames_pp(datestamps)

        pp_filelist = []

        for timepoint, filename in zip(timepoints, filenames):
            pp_filelist.append({"timepoint": timepoint,
                                "filename": filename})

        return pp_filelist

    def _mass_cmd_pp(self, start: datetime, end: datetime) -> Tuple[str, List[Dict], str, int]:
        """Create the list of mass commands and respective filter files needed for a given
        stream.

        :param start: Start date run bound.
        :type start: datetime
        :param end: End date run bound.
        :type end: datetime
        :raises FilterFileException:
        :return: A list of mass cmds represented as dictionaries.
        :rtype: Tuple[str, List[Dict], str, int]
        """
        self.mass_cmd = []
        start, end = start.strftime("%Y%m%d"), end.strftime("%Y%m%d")
        pp_filelist = self._create_pp_filelist(start, end)
        chunks = self._chunk_pp_filelist(pp_filelist)

        for chunk in chunks:
            start, end = chunk[0]["timepoint"], chunk[-1]["timepoint"]
            start_tup = start.year, start.month_of_year, start.day_of_month
            end_tup = end.year, end.month_of_year, end.day_of_month
            try:
                filterfile = self._create_filterfile_pp(chunk, False)
            except IOError:
                raise FilterFileException(
                    "Could not create a sizing file in {}".format(self.procdir))
            # add a single command
            cmd = {"moo_cmd": "select",
                   "param_args": ["-i", "-d", filterfile, self.source, self.target],
                   "start": start_tup,
                   "end": end_tup}
            self.mass_cmd.append(cmd)

        return "ok", self.mass_cmd, "", 1

    def _create_filterfile_pp(self, chunk: List[Dict], test_mode: bool) -> str:
        """_summary_

        :param chunk: _description_
        :type chunk: List[Dict]
        :param test_mode: _description_
        :type test_mode: bool
        :return: _description_
        :rtype: str
        """
        file_frequency = self.model_parameters._stream_file_info.file_frequencies[self.stream].frequency

        pp_file = self._pp_file_string(chunk, file_frequency)

        start_string = str(chunk[0]["timepoint"])
        end_string = str(chunk[-1]["timepoint"])

        if test_mode:
            file_name = "{}/extract/{}_test.dff".format(self.procdir, self.stream)
        else:
            file_name = "{}/extract/{}_{}_{}.dff".format(self.procdir, self.stream, start_string, end_string)

        with open(file_name, "w") as file_h:
            file_h.write(
                (
                    "begin_global\n"
                    "pp_file={}\n"
                    "end_global\n"
                ).format(pp_file)
            )
            # add stash filters to file
            file_h.write(self.filters[self.stream])

        return file_name

    def _check_block_size_pp(self, filterfile, override_simulate=False):
        """Runs a dry-run MOOSE SELECT with supplied filter file.

        Returned status information includes:
            val   str   subsequent action code - ok, skip, or stop
            code  str   code for status
            msg   str   message for logging purpose

        Parameters
        ----------
        filterfile: str
            name of temporary filter file used for checking request size

        Returns
        -------
        dict
            status information
        """
        if override_simulate:
            simulate = False
        else:
            simulate = self.simulation

        param_args = ["-n", filterfile, self.source, self.target]
        code, cmd_out, command = run_moo_cmd("select", param_args, simulate)
        status = check_moo_cmd(code, cmd_out)
        status['command'] = " ".join(command)
        return status, cmd_out

# ----- NC specialisation methods ---------------------------------------------
    def _format_filter_nc(self, stream):
        """Format mapping information for nc data into MASS filter format.

        Parameters
        ----------
        stream: str
            code for stream (e.g. onm)

        Returns
        -------
        list of dict
            list of configured MOOSE netcdf filters
        list of dict
            list of missing filters
        """
        filter_msg = []
        filter_msg_exc = []
        self.filters = {}

        # check if variables/mappings are defined for this data stream
        if self.mappings.get(stream):

            # loop over variables/mappings for this stream
            # include embargoed mappings
            for var in self.mappings.get(stream):

                if ((var["status"] == "ok" or var["status"] == "embargoed")
                        and var.get("constraint")):
                    filter_msg.append(var)
                    # TODO: replace loops with ",".join()
                    # create filter block from constraint
                    for constraint in var["constraint"]:
                        # check if substream defined for this constraint
                        if "substream" in constraint:
                            substream = constraint["substream"]
                        else:
                            substream = "default"

                        # check if substream exists - if not initialise it
                        if substream not in self.filters:
                            self.filters[substream] = ""
                        # add in coordinate bounds if necessary
                        for coord_bound in get_bounds_variables(
                                stream, substream):
                            self.filters[substream] += "{},".format(
                                coord_bound)

                        # concatenate variable to relevant substream str
                        self.filters[substream] += "{},".format(
                            constraint["variable_name"])

                elif var.get("status") is None:
                    filter_msg_exc.append(
                        {"name": var["name"],
                         "table": var["table"],
                         "reason": "filter status not specified"})

                elif var.get("constraint") is None:
                    filter_msg_exc.append(
                        {"name": var["name"],
                         "table": var["table"],
                         "reason": "no mapping details specified"})

                else:
                    filter_msg_exc.append(
                        {"name": var["name"],
                         "table": var["table"],
                         "reason": "filter status invalid"})

            # trim trailing comma from strings and remove duplicates
            for k in self.filters:
                filter_str = self.filters[k][:-1]
                var_list = filter_str.split(",")
                self.filters[k] = \
                    ",".join(sorted(set(var_list), key=var_list.index))

            filter_msg = sorted(filter_msg, key=lambda y: y["name"])
            filter_msg_exc = sorted(filter_msg_exc, key=lambda y: y["name"])

        return filter_msg, filter_msg_exc

    def _mass_cmd_nc(self, start, end):
        """Create MASS commands and filter files for nc data stream.
        [Note filtering on date is not yet implemented - waiting for
        functionality to be included in MOOSE]

        Parameters
        ----------
        start: :class:`datetime.datetime`
            start date for data required
        end: :class:`datetime.datetime`
            end date for data required

        Returns
        -------
        str
            action status - ok|skip|stop
        list of dict
            MOOSE requests required to extract data from current stream
             - dict per request
        str
            message detailing nature of error
        str
            Status code (for consistency with _mass_cmd_pp)
        """

        self.mass_cmd = []

        error = ""
        status = {"val": "ok"}        # dummy value for consistency with pp

        filelist, moo_err = fetch_filelist_from_mass(self.source, self.simulation)
        logger = logging.getLogger(__name__)
        logger.info("MOO LS command returned {} files".format(len(filelist)))
        if moo_err:
            logger.info(
                "MOO LS command returned error message {}".format(moo_err))
        if not filelist and not self.simulation:
            error = "no matching files found" if moo_err is None else moo_err
            status["val"] = "stop"
        else:
            # loop through substreams for this netcdf stream (e.g. grid-T)
            count = 0

            for substream, filter_str in self.filters.items():
                count += 1
                file_name = "{}/extract/{}_{}s.dff".format(
                    self.procdir, self.stream, substream)
                try:
                    self._create_filterfile_nc(file_name, filter_str,
                                               self.stream, substream)
                except IOError:
                    raise FilterFileException(
                        "Could not create a sizing file in {}".format(
                            self.procdir))
                if substream == "default":
                    regexp = netCDF_regexp()
                else:
                    # only nemo and medusa can be sub-streamed
                    regexp = netCDF_regexp("nemo|medusa", substream)
                if not self._update_mass_cmd(
                    regexp, filelist, start, end, "filter",
                    ["-i", "-d", file_name], MOOSE_MAX_NC_FILES
                ) and self.ensemble_member_id is not None:
                    if substream == "default":
                        regexp = netCDF_regexp(None, None, self.ensemble_member_id)
                    else:
                        # only nemo and medusa can be sub-streamed
                        regexp = netCDF_regexp("nemo|medusa", substream, self.ensemble_member_id)
                    self._update_mass_cmd(
                        regexp, filelist, start, end, "filter",
                        ["-i", "-d", file_name], MOOSE_MAX_NC_FILES
                    )

            if count == 0:
                error = "no matching variables to retrieve"
                status["val"] = "stop"
        return status["val"], self.mass_cmd, error, None

    def _generate_filenames_nc(self, datestamps: List[str], sub_stream: str) -> List[str]:
        """Generate .nc filenames. Accounts for cases where ensemble id is
        used in the filename by running a `moo ls` on the source directory
        and checking the returned filenames.

        :param datestamps: List of datestamps
        :type datestamps: List[str]
        :return: List of .pp filenames
        :rtype: Tuple[List[str], List[str]]
        """

        if self.stream[0] == "o":
            model_realm = GRID_LOOKUPS[sub_stream]
            grid = f"_{sub_stream}"
        elif self.stream[0] == "i":
            model_realm = "cice"
            grid = ""

        suite = self.suite_id.split("-")[1]
        freq = "1" + self.stream[-1]

        if self.ensemble_member_id:
            suite = "{}-{}{}".format(suite, self.ensemble_member_id, self.stream[0])
            command_output = mass_list_dir(self.source, False)
            if suite not in command_output[0]:
                suite = self.suite_id.split("-")[1] + self.stream[0]
        else:
            suite = suite + self.stream[0]
        filenames = [f"{model_realm}_{suite}_{freq}_{date}{grid}.nc" for date in datestamps]

        return filenames

    def _create_filterfile_nc(self, file_name, variables, stream, substream):
        """Creates MASS filter file for use when extracting nc data streams
         with FILTER command.

        Parameters
        ----------
        file_name: str
            name of filter file
        variables: str
            comma separated string of variables to be selected
        """
        grid_info = self.plugin.grid_info(self.model_id, GridType.OCEAN)
        with open(file_name, "w") as file_h:
            # add variable filters to file
            file_h.write("-a\n-v {}".format(variables))
            if substream in grid_info.halo_options:
                for ncks_opt in grid_info.halo_options[substream]:
                    file_h.write("\n{}".format(ncks_opt))

    def _update_mass_cmd(self, regexp, filelist, start, end, moo_cmd,
                         moo_args, max_chunk_size):
        files_on_tapes = defaultdict(list)
        files_found = 0
        logger = logging.getLogger(__name__)
        for (tape, nc_file) in filelist:
            result = re.search(regexp, nc_file)
            if result:
                files_found += 1
                _, file_start, file_end, _ = result.groups()
                start_dt = datetime.datetime.strptime(file_start, "%Y%m%d")
                end_dt = datetime.datetime.strptime(file_end, "%Y%m%d")
                if start_dt >= start and end_dt <= end:
                    files_on_tapes[tape].append(nc_file)
        if not files_found:
            return False
        if not self.simulation:
            logger.info(
                "Using {} to retrieve {} files with chunk size of {}".format(
                    regexp, files_found, max_chunk_size
                )
            )
        tape_limit, error = get_tape_limit(simulation=self.simulation)
        if error:
            logger.info(error)
            return False
        chunks = chunk_by_files_and_tapes(files_on_tapes, tape_limit, MOOSE_MAX_NC_FILES)
        for chunk in chunks:
            cmd = {
                "moo_cmd": moo_cmd,
                "param_args": moo_args + chunk + [self.target],
                "start": start,
                "end": end,
            }
            self.mass_cmd.append(cmd)
        if self.simulation:
            self.mass_cmd.append({
                "moo_cmd": "SIMULATED",
                "param_args": moo_args + [self.target],
                "start": start,
                "end": end,
            })
        return True


class FilterFileException(IOError):
    pass
