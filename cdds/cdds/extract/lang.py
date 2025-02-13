# (C) British Crown Copyright 2016-2021, Met Office.
# Please see LICENSE.md for license details.
"""
Function to provide all text strings used in logging and user interaction
for extract.
"""


def set_language():
    """cdds_extract language strings

    Returns
    -------
    dict of str
        language strings used in cdds_extract
    """

    lang = {
        # script
        "script_end": "-- script end --",
        "script_suspend": "{} process suspended",
        "script_suspend_email":
            """
            The {} process for request {} has been killed.
            The status for this process in CREM has been set to 'suspended'.
            """,
        "script_sigint": "SIGINT detected - {} process suspended [{}:{}]",
        "script_info": "Process: |pid: {}|host: {}|user: {}|",

        # configuration setup
        "config_fail": "CRITICAL: CDDS configuration file could not be "
                       "accessed",
        "config_project_fail": "CRITICAL: project-SPECIFIC cfg file could "
                               "not be accessed [{}] ...",
        "config_project_success": "project-SPECIFIC cfg file used to "
                                  "modify configuration [{}] ...",
        "config_dir": "configuration directory used: {}",
        "config_json_err": "CRITICAL: unable to read json configuration "
                           "file {}: {}",

        # database
        "dbase_unknown": "CRITICAL: database [{}] not configured for CDDS",
        "dbase_connect_fail": "CRITICAL: failed to connect to CREM database",
        "dbase_content_error": "CRITICAL: database content for the {} is "
                               "missing (id = {})",

        # files / directories
        "dir_success": "Created {} directory {}",
        "dir_exists": "Directory {} already exists",
        "dir_fail": """CRITICAL: failed to create {} directory
            root:   {}
            map:    {}
            name:   {}
            status: {}
            error:  {}
        """,
        "dir_log_fail": "ERROR failed to create {} log directory",
        "dir_file_access_fail": "CRITICAL: failed to write to a directory {}",

        # logger
        "tmplog_close": "logger switching to process specific log in "
                        "proc directory...",

        # filters
        "filter_incomplete_stop": "MOOSE filters for requested variables are "
                                  "not complete - extract check option "
                                  "forces stop",
        "filter_list": "{} filter details:  --------------------\n",
        "filter_ok": " + {:<15} : {:<15} {}  - {}\n",
        "filter_not_ok": " + {:<15} : {:<15} {}\n",
        "filter_missing": "\n ----- Missing Variable Mappings -----\n{} \n",
        "filter_embargo": "\n ----- Embargoed Variable Mappings -----\n{} \n",

        # request
        "request_detail":
            """REQUEST details for this extract process:
            mip_era                {}
            activity_id            {}
            experiment_id          {}
            suite_id               {}
            model_id               {}
            target                 {}
            """,

        "data_detail": """
       suite:  {},  stream: {},  type: {},  start: {},  end: {}""",


        "request_init_error": "CRITICAL: Neither CREM or JSON initialisation "
                              "of request parameters was defined",
        "request_json_missing": "CRITICAL: JSON request context file not"
                                "  found or not readable [error: {}]",
        "request_json_invalid": "CRITICAL: JSON request not parsed correctly "
                                "[error: {}]",
        "request_already_running": "this request has an {} process already"
                                   " running or suspended",

        "extract_success": "complete / success",
        "extract_quality": "complete / quality issues",
        "extract_failed":    "failed",
        "extract_suspend": "suspended",
        "extract_unknown": "failed / unrecognised status [{}]",

        # streams (data items)
        "stream_ancil": "\"ancil\" stream not retrieved from MASS",
        "stream_size_fail": "CRITICAL: could not establish number of MASS"
                            " requests required [error: {} ]",
        "stream_exists_ok": "archive data exists for dataset {}",
        "stream_exists_fail": "CRITICAL: archive data exists check FAILED"
                              " for dataset {} (error_code: {})\n{}",
        "stream_start":
            """Stream Start:  {}  ---------------- start: {}  end: {} """,
        "stream_skip": "stream {} skipped on user request",
        "stream_skip_data": "stream {} skipped: [ {} ]\n",
        "stream_not_selected": "CRITICAL: no stream could be selected for "
                               "processing",
        "stream_type_invalid": "CRITICAL: stream {} has invalid filetype "
                               "[{}]",
        "stream_end_success":
            """Stream {} completed  ---------------- {}\n\n""",
        "stream_end_fail":
            """CRITICAL: Stream {} failed ---------------- {}\n\n""",

        # blocks
        "block_start": "stream {} request: {}  [{} to {}]  ----------------",
        "block_fail": "CRITICAL: block {}: extraction FAILED - {}",
        "block_success": "block {}: extraction SUCCESS",

        # moose
        "moose_request": "MOOSE request: {} [{}]",
        "moose_output": "MOOSE request response: {} [{}]",
        "moose_fail": "MOOSE request failed: {} [err: {}]",

        # command line interface
        "cli_desc":
            "CDDS extraction script for scripted retrievals from MASS"
            " to obtain the input data for a CDDS data dissemination "
            "request.  Includes filtering of PP and netcdf files.",
        "cli_epilog":
            "More information on this script is available at "
            "<FIXME url to be added here in lang['cli_epilog']>",
        "cli_project":
            "short project/programme code e.g. CMIP6",
        "cli_database":
            "database name e.g crem2live (required if using CREM database)",
        "cli_jsondb":
            "json file path (required if NOT using CREM database)",
        "cli_requestid":
            "if using DATABASE option the id for the request record in CREM "
            "(integer) - required if using CREM)",
        "cli_user":
            "if using DATABASE option the CREM user name "
            "- required if using CREM",
        "cli_email":
            "user email address if notifications required",
        "cli_check":
            "action to be taken on stream error: "
            "none - get data for mappings we have; "
            "skip - if missing mappings skip this stream; "
            "stop - if missing mappings stop process ",
        "cli_logverbose":
            "include verbose output in log files",
        "cli_filter":
            "apply filters to select only required data",
        "cli_overwrite":
            "replace existing files",
        "cli_stream":
            "process only specified stream",
        "cli_dberror": "-r and -u are required when -d is set",

        "arg_settings":
            """
            Script Options
               request              {}
               {}
               --root_proc_dir      {}
               --root_data_dir      {}
               {}
            """,
        "user_settings":
            """
            Username {}
            """,

        # user emails
        "start_email_subject": "extract process started",
        "start_email_msg":
            """
            The extract process for request [{}] has started.

               The process details are:
                  - server:  {}
                  - user:    {}
                  - process: {}
            """,

        "end_email_subject": "extract process completed",
        "end_email_msg":
            """
            The extract process for request [{}] has completed.

               - the completion status is {} - more information may be
                 available from the history tab in CREM

               - the log file for the process is available at:
                  {}

               - the extracted data can be found at:
                  {}
            """,

        # validation
        "val_title": "VALIDATION for stream {}:\n",
        "val_file_count": "files count: correct number of files ( {} )\n",
        "val_file_count_error":
            "CRITICAL: mismatch on number of files "
            "(expected: {} ; actual: {} )\n",
        "val_stash_codes_error":
            "CRITICAL: mismatch on stash codes in {} pp file(s): {}\n",
        "val_nc_file_error": "CRITICAL: problems with netcdf output: {}\n",
        "val_type_unknown":
            "stream type is not recognised - no validation performed\n",
        "val_none": "CRITICAL extract failure: no validation performed\n",
        "val_stash_start": "  {}: starting STASH codes validation\n",
        "val_stash_end": "  {}: completed STASH codes validation\n",
        "val_stash_ok": "  no problems found with stash codes in pp files\n",
        "val_stash_reference": "  --- STASH reference dictionary "
                               "generated from file {}: {}\n",
        "val_ok": "VALIDATION completed, no problems found\n",
        # variables
        "variables_file_missing":
            "CRITICAL: variables file [{}] not found or not readable "
            "[error: {}]",
        "variables_file_found": """
        variables file specification
          - file:       {}
          - request:    {}
          - mip:        {}
          - experiment: {}
          """,
        "variables_bad_status": """
        variables file does not have valid status
          - file:   {}
          - status: {}
          - detail: {}
          """,
        "variables_to_extract":
            "Variables requested for processing - by stream: ",
        "variables_not_to_extract":
            "Variables NOT requested for processing (with reason): ",
    }

    return lang
