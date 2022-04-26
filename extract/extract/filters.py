# (C) British Crown Copyright 2016-2021, Met Office.
# Please see LICENSE.rst for license details.
"""
Class for creating MOOSE commands for filtered retrievals from MASS
using SELECT and FILTER

"""

import datetime
import json
import logging
import re

from cdds_common.cdds_plugins.plugins import PluginStore
from cdds_common.cdds_plugins.grid import GridType

from hadsdk.common import netCDF_regexp, run_command
from hadsdk.mapping import ModelToMip
from extract.common import (byteify, get_stash, moose_date, run_moo_cmd,
                            check_moo_cmd, get_bounds_variables,
                            calculate_period)
from extract.constants import (MOOSE_LS_PAGESIZE,
                               MOOSE_LS_MAX_PAGES, MOOSE_MAX_NC_FILES,
                               DATESTAMP_PATTERN,
                               MONTHLY_DATESTAMP_PATTERN_APRIL,
                               MONTHLY_DATESTAMP_PATTERN_SEPTEMBER,
                               SUBDAILY_DATESTAMP_PATTERN)


class Filters(object):
    """
    Creates MOOSE commands for filtered retrievals from MASS
    using SELECT (PP files) and FILTER (netcdf files)
    """

    def __init__(self, procdir=None, var_list=None, max_blocks=None,
                 simulation=False):
        """Initialises Filters object

        Parameters
        ----------
        procdir: str
            pathname to extract processing directory
        var_list: list of dict
            list of variables (dicts) to be processed
        max_blocks: int
            maximum number of MOOSE requests to divide a data stream
            retrieval into
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

        self.max_blocks = max_blocks
        self.mass_cmd = []
        self.suite_id = None
        self.ensemble_member_id = None
        self.model_id = None

    def set_mappings(self, mip_table_dir, request):
        """Get the |model to MIP mappings|.

        Parameters
        ----------
        mip_table_dir: str
            pathname to directory holding mip tables for this request
        request: hadsdk.request.Request
            key science parameter values for this request

        Returns
        -------
        bool
            true if all mappings configured, else false
        """
        plugin = PluginStore.instance().get_plugin()
        model_params = plugin.models_parameters(request.model_id)
        # initialise mappings request structure
        mapping_request = {
            "process": {
                "type": "extract_filters", "tabledir": mip_table_dir
            },
            "science": {"mip_era": request.mip_era,
                        "mip": request.mip,
                        "model_id": request.model_id,
                        "model_ver": model_params.model_version,
                        "experiment_id": request.experiment_id,
                        "suite_id": request.suite_id}
        }
        self.model_id = request.model_id
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

    def mass_command(self, stream, source, target, resolution):
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
                stream["start_date"], stream["end_date"], resolution)

        return status, self.mass_cmd, error, code


# ----- PP specialisation methods ---------------------------------------------

    def _format_filter_pp(self, stream):
        """Format mapping information for pp data into MASS filter format.

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

    def _chunk_candidates(self, start_date, end_date):
        """A helper method to calculate chunk sizes candidates.

        Parameters:
        -----------

        start_date: tuple
            A tuple of integer year, month and day.
        end_date: tuple
            A tuple of integer year, month and day.

        Returns:
        --------
        list
            A list of chunk sizes.
        """

        years = end_date[0] - start_date[0] + 1
        # generate chunk sizes
        chunk_sizes = [years]
        while years > 1:
            years = years // 2
            chunk_sizes.append(years)
        # allow for 6 months and 3 months;
        chunk_sizes += [0.5, 0.25]
        return chunk_sizes

    def _test_chunks(self, start_date, chunk_sizes, with_ens_id):
        """Tries requesting data from mass using decreasing chunk
        sizes.


        Parameters:
        -----------
        start_date: tuple
            A tuple of integer year, month and day.
        chunk_sizes: list
            A list of chunk sizes (in simulated years).

        Returns:
        --------
        int
            The largest working chunk size.
        dict
            Moo status dictionary for debugging purposes.
        """
        chunk_size = None
        # test chunk sizes in decreasing order until one works
        for test_size in chunk_sizes:
            test_start = start_date
            if test_size > 1:
                test_end = calculate_period((
                    test_start[0] + test_size,
                    test_start[1],
                    test_start[2]
                ), False)
            else:
                test_end = calculate_period((
                    test_start[0],
                    test_start[1] + int(test_size * 12),
                    test_start[2]
                ), False)
            # create filter file for this block
            file_name = "{}/extract/{}_test.dff".format(
                self.procdir, self.stream)
            try:
                self._create_filterfile_pp(
                    test_start,
                    test_end,
                    file_name,
                    with_ens_id
                )
            except IOError:
                raise FilterFileException(
                    "Could not create a sizing file in {}".format(
                        self.procdir))
                # add single command
            status = self._check_block_size_pp(file_name)
            if status["val"] == "ok":
                # request size ok
                chunk_size = test_size
                break
            elif status["val"] == "skip":
                if status["code"] == "limit_exceeded":
                    continue
                else:
                    return chunk_size, status
        return chunk_size, status

    def generate_chunks(self, start_date, run_end, chunk_size):
        """
        Covers a request period with chunks of suitable sizes.

        Parameters
        ----------
        start_date: tuple
            A tuple of integer year, month and day for a data chunk
            enclosing start date.
        run_end: :class:`datetime.datetime`
            End date for data required.
        chunk_size: int, float
            Chunk size.

        Returns
        -------
        list
            A list of data chunks for a request period.
        """

        chunks = []
        # The Year-Month-Day sequence defines the correct order
        # hence it is possible just to compare strings directly
        # to determine date precedence
        while (DATESTAMP_PATTERN.format(*start_date) <
               DATESTAMP_PATTERN.format(run_end.year, run_end.month,
                                        run_end.day)):
            if chunk_size >= 1:
                end_date_tpl = (
                    start_date[0] + chunk_size,
                    start_date[1],
                    start_date[2])
            else:
                years = start_date[0]
                months = start_date[1] + int(chunk_size * 12)
                if months > 12:
                    years += 1
                    months -= 12
                end_date_tpl = (years, months, start_date[2])

            end_date = calculate_period(end_date_tpl, False)
            chunks.append({
                'start': start_date,
                'end': end_date
            })

            start_date = end_date_tpl
        chunks[-1]['end'] = calculate_period(
            (run_end.year, run_end.month, run_end.day), False)
        return chunks

    def _mass_cmd_pp(self, start, end):
        """Create MASS commands and filter files for pp data streams

        Parameters
        ----------
        start: :class:`datetime.datetime`
            start date for data required
        end: :class:`datetime.datetime`
            end date for data required

        Returns
        -------
        str
            action to be taken with current data stream - [ok|skip|stop]
        list of dict
            list of MOOSE requests to complete the extraction from the data
            stream - dict per request.
        str
            error message
        str
            status code
        """
        self.mass_cmd = []
        error = ""

        start_date = calculate_period((start.year, start.month, start.day))
        end_date = calculate_period((end.year, end.month, end.day), False)
        test_sizes = self._chunk_candidates(start_date, end_date)
        with_ens_id = False
        chunk_size, status = self._test_chunks(start_date, test_sizes, with_ens_id)
        if chunk_size is None and self.ensemble_member_id is not None:
            with_ens_id = True
            chunk_size, status = self._test_chunks(start_date, test_sizes, with_ens_id)
        if chunk_size is None:
            return (
                status["val"], [],
                "Unable to determine chunk length", status["code"])
        chunks = self.generate_chunks(start_date, end, chunk_size)

        for chunk in chunks:
            # create filter file for this block
            start_string = DATESTAMP_PATTERN.format(
                *chunk["start"])
            end_string = DATESTAMP_PATTERN.format(
                *chunk["end"])
            file_name = "{}/extract/{}_{}_{}.dff".format(
                self.procdir, self.stream, start_string, end_string)
            try:
                self._create_filterfile_pp(
                    chunk["start"], chunk["end"], file_name, with_ens_id)
            except IOError:
                raise FilterFileException(
                    "Could not create a sizing file in {}".format(
                        self.procdir))
                # add single command
            moo_options = "-i"
            cmd = {"moo_cmd": "select", "param_args":
                   [moo_options, "-d", file_name, self.source,
                    self.target],
                   "start": chunk["start"], "end": chunk["end"]}
            self.mass_cmd.append(cmd)
        return "ok", self.mass_cmd, error, 1

    def _create_filterfile_pp(self, start, end, file_name, with_ens_id=False):
        """Creates MASS filter file for use when extracting pp data
        streams with SELECT command.

        Parameters
        ----------
        start: tuple
            start date for filter as a (year, month, day) tuple
        end: tuple
            end date for filter as a (year, month, day) tuple
        file_name: str
            name of filter file to create
        """
        if self.ensemble_member_id is not None and with_ens_id:
            suite_prefix = "{}-{}".format(self.suite_id[2:], self.ensemble_member_id)
        else:
            suite_prefix = self.suite_id[2:]

        plugin = PluginStore.instance().get_plugin()
        subdaily_streams = plugin.models_parameters(self.model_id).subdaily_streams()

        if self.stream in subdaily_streams:
            start_filename = SUBDAILY_DATESTAMP_PATTERN.format(
                suite_prefix, self.stream[2], *start)
            end_filename = SUBDAILY_DATESTAMP_PATTERN.format(
                suite_prefix, self.stream[2], *end)
        else:
            # We will try to match all monthly files for a given year.
            # MOO string interpolation uses alphabetic order which is why
            # we start with April and end with September.
            start_filename = MONTHLY_DATESTAMP_PATTERN_APRIL.format(
                suite_prefix, self.stream[2], start[0])
            end_filename = MONTHLY_DATESTAMP_PATTERN_SEPTEMBER.format(
                suite_prefix, self.stream[2], end[0])
        if start_filename != end_filename:
            pp_string = '"{}".."{}"'.format(start_filename, end_filename)
        else:
            pp_string = '"{}"'.format(start_filename)
        with open(file_name, "w") as file_h:
            file_h.write(
                (
                    "begin_global\n"
                    "pp_file=[{}]\n"
                    "end_global\n"
                ).format(pp_string)
            )

            # add stash filters to file
            file_h.write(self.filters[self.stream])
        return pp_string

    def _check_block_size_pp(self, filterfile):
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
        param_args = ["-n", filterfile, self.source, self.target]
        code, cmd_out, command = run_moo_cmd("select", param_args,
                                             self.simulation)
        status = check_moo_cmd(code, cmd_out)
        status['command'] = " ".join(command)
        return status


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

    def _mass_cmd_nc(self, start, end, resolution):
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

        filelist, moo_err = self._fetch_filelist_from_mass(self.source)
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
                                               self.stream, substream,
                                               resolution)
                except IOError:
                    raise FilterFileException(
                        "Could not create a sizing file in {}".format(
                            self.procdir))
                if substream == "default":
                    regexp = netCDF_regexp()
                else:
                    # only nemo and medusa can be sub-streamed
                    regexp = netCDF_regexp("nemo|medusa", substream)
                self._update_mass_cmd(
                    regexp, filelist, start, end, "filter",
                    ["-i", "-d", file_name], MOOSE_MAX_NC_FILES
                )
            if count == 0:
                error = "no matching variables to retrieve"
                status["val"] = "stop"
        return status["val"], self.mass_cmd, error, None

    def _create_filterfile_nc(self, file_name, variables, stream, substream,
                              resolution):
        """Creates MASS filter file for use when extracting nc data streams
         with FILTER command.

        Parameters
        ----------
        file_name: str
            name of filter file
        variables: str
            comma separated string of variables to be selected
        """
        plugin = PluginStore.instance().get_plugin()
        grid_info = plugin.grid_info(self.model_id, GridType.OCEAN)
        with open(file_name, "w") as file_h:
            # add variable filters to file
            file_h.write("-a\n-v {}".format(variables))
            if substream in grid_info.halo_options:
                for ncks_opt in grid_info.halo_options[substream]:
                    file_h.write("\n{}".format(ncks_opt))

    def _fetch_filelist_from_mass(self, mass_dir):
        """Retrieves a list of files stored in a MASS directory

        Parameters
        ----------
        mass_dir: str
            name of a MASS directory

        Returns
        -------
        list
            List of files
        error
            An error output from MOOSE
        """
        # Don't log the file list to avoid cluttering the extract logs
        paging_options = '--page=1-{}:{}'.format(MOOSE_LS_MAX_PAGES,
                                                 MOOSE_LS_PAGESIZE)
        if self.simulation:
            files = []
            error = None
        else:
            try:
                cmd_out = run_command(["moo", "ls", paging_options, mass_dir])
                files = cmd_out.split()
                error = None
            except RuntimeError as e:
                files = []
                error = str(e)
        return files, error

    def _update_mass_cmd(self, regexp, filelist, start, end, moo_cmd,
                         moo_args, max_chunk_size):
        filtered_subset = []
        logger = logging.getLogger(__name__)
        for nc_file in filelist:
            result = re.search(regexp, nc_file)
            if result:
                _, file_start, file_end, _ = result.groups()
                start_dt = datetime.datetime.strptime(file_start, "%Y%m%d")
                end_dt = datetime.datetime.strptime(file_end, "%Y%m%d")
                if start_dt >= start and end_dt <= end:
                    filtered_subset.append(nc_file)
        if not self.simulation:
            logger.info(
                "Using {} to retrieve {} files with chunk size of {}".format(
                    regexp, len(filtered_subset), max_chunk_size
                )
            )

        for offset in range(0, len(filtered_subset), max_chunk_size):
            filtered_chunk = filtered_subset[offset:offset + max_chunk_size]

            cmd = {
                "moo_cmd": moo_cmd,
                "param_args": moo_args + filtered_chunk + [self.target],
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


class FilterFileException(IOError):
    pass
