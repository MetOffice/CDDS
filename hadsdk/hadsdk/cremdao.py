# (C) British Crown Copyright 2016-2021, Met Office.
# Please see LICENSE.rst for license details.
"""
Data access class to interface with CREM
"""
from datetime import datetime
import json
import time

from hadsdk.dbsql import SqlDb
from hadsdk.cremdao_exception import (CremInvalidInputException,
                                      CremZeroRecordsException)


class CremDao(SqlDb):
    """
    Class for interfacing CREM database with python post processing scripts.
    Uses mysql database interface class SqlDb.

    Methods:
      CONFIGURATION
      get_cfg_param           - retrieves config parameter

      CODES
      get_codes               - retrieves code values for selected code
      check_code              - checks if value is valid for selected code
      set_code                - Adds a new code to the ct_codelist table

      PROCESS
      set_process             - sets process information rt_process
      get_process             - retrieves process information from rt_process
      del_process             - deletes process information from rt_process

      HISTORY
      get_history             - retrieves status history for a request
      set_history             - set status history record for a request
      upd_history             - updates a status history record for a request
      del_history             - deletes a status history record for a request

      LOCATIONS [DISK]
      get_location            - retrieves disk locations for a request

      REQUESTS
      get_request             - retrieves data set request record
      find_request            - searches for request(s)
      set_request             - creates a new request record
      set_request_data        - adds data items to an existing request
      upd_request             - updates a request record
      del_request             - deletes a request record
      get_request_status      - gets latest status for all request processes
      set_request_status      - sets request status for a request process
      get_request_data        - gets input data stream info for this request
      get_extract_filter      - gets MOOSE filter information

      PERSON
      get_person_by_id        - retrieves individual record by record id
      get_responsible_party   - gets contacts for specified entity

      INSTITUTE
      get_institute_by_id     - retrieves institute record by record id

      PROJECT [MIP]
      set_project             - inserts or updates a project record
      del_project             - deletes a project record
      get_project_by_id       - retrieves project record by record id
      get_project_by_name     - retrieves project record by project name
      list_projects_by_programme_id
                              - retrieves all projects by programme id

      EXPERIMENT
      get_experiment_by_id    - retrieves experiment record
      get_experiment_by_name  - retrieves experiment(s) by canonical name
      set_experiment          - inserts or updates an experiment record
      del_experiment          - deletes an experiment record
      list_experiments_by_project_id
                              - retrieves all experiments associated
                                with a project id

      REQUIREMENT
      get_requirement_by_id   - retrieves requirement record by id
      get_requirement_by_name - retrieves requirement record by name
      set_requirement         - inserts or updates a requirement record
      del_requirement         - deletes a requirement
      list_requirements_by_parent_id
                              - fetches requirements associated with
                                parent (experiment) record
      set_reqt_attribute      - insert or update requirement attribute
      del_reqt_attribute      - delete a requirements attribute
      list_reqt_attributes_by_requirement_id
                              - retrieves all attributes for a requirement

      SIMULATION
      get_simulation_by_id    - retrieves simulation record

      MODEL RUN
      get_modelrun_by_id      - retrieves model run record

      MODEL
      get_model_by_id         - retrieves model record
      get_grid_by_id          - retrieves grid record
      list_couplings_by_modelid
                              - get associated submodels for a coupled model
      get_submodel_by_id      - gets component model details by id

      DOMAIN [REALM]
      get_domain_by_id        - gets domain record by id
      list_domains_by_submodelid
                              - gets domains associated with a submodel

      TOPICS
      list_topics_by_parent   - gets topics associated with a topic owner
      list_properties_by_topicid
                              - gets model properties associated with topic
      list_enums_by_property  - gets enum options for specified property

      REFERENCES
      get_references          - gets references for specified entity

      MANIFEST [FILE TRANSFERS]
      get_file_manifest_by_id - gets file manifest entry by record id
      get_file_manifest_by_request
                              - gets files file manifest entries for request
      set_file_manifest       - inserts a record in the rt_filemanifest table
      del_file_manifest       - deletes file manifest records by id or request

      MISC
      validate_mandatory_keys - crude input validation
      get_user_by_name        - gets CREM user details (not password)

      AUDIT
      log_change             - logs database operations

    """

    def __init__(self, connect_env):
        """Initialises cremdao object

        Parameters
        ----------
        connect_env : dict
            Host and database name for connection
        """
        super(CremDao, self).__init__(connect_env)
        self.connect_env = connect_env

    def get_cfg_param(self, project, parameter):
        """Retrieves project specific configuration parameter
        from ct_config table in CREM.

        Parameters
        ----------
        project : str
            project code (e.g. cmip5)
        parameter: str
            parameter name

        Returns
        -------
        str
            parameter configuration value (empty if not found)
        """
        if project is None:
            raise CremInvalidInputException(
                "get_cfg_param: project name not specified")

        if parameter is None:
            raise CremInvalidInputException(
                "get_cfg_param: parameter name not specified")

        query = ("SELECT `value` FROM ct_config "
                 "WHERE `project`=%s AND `parameter`=%s")
        query_param = (project, parameter, )
        result = self.single_row_select(query, query_param)

        if not result:
            result["value"] = None

        return result["value"]

    def get_codes(self, codetype, project=None):
        """Gets all code values defined for a specific code type.
        If project is specified then project specific codes
        will be returned.

        Information provided for each code value is;
           codetype  str  code type
           label     str  code label for user presentation
           value     str  code data value in database
           default   int  1 if default value
           rank      int  order in which to present codes to user

        Parameters
        ----------
        codetype: str
            code type as defined in ct_codes (e.g. ensembletype)
        project: str
            (optional) string with project constraint (e.g. cmip5)

        Returns
        -------
        int
            number of code values found
        list
            list of dicts with code value information
        """
        if codetype is None:
            raise CremInvalidInputException(
                "get_codes: Code type not specified")

        query = ("SELECT a.codetype, `label`, `value`, `default`, `rank` "
                 "FROM ct_codes as a "
                 "JOIN ct_codelist as b ON a.codetype=b.codetype "
                 "WHERE a.codetype=%s ")
        query_param = (codetype, )

        # add project specific constraints if required
        if project is not None:
            query += " AND project LIKE %%s% "
            query_param = query_param + (project, )

        query += " ORDER BY b.rank ASC"
        result = self.multi_row_select(query, query_param)
        return len(result), result

    def check_code(self, codetype, codevalue, project=None):
        """Checks if supplied code is a valid value.
        If project is specified then project specific codes are checked.

        Parameters
        ----------
        codetype: str
            code type as defined in ct_codes (e.g. ensembletype)
        codevalue: str
            value to be checked (e.g. initialisation)
        project: str
            (optional) string with project constraint (e.g. cmip5)

        Returns
        -------
        bool
            true if value is valid for this code
        """
        if codetype is None or codevalue is None:
            raise CremInvalidInputException(
                "check_code: Code type not specified")

        if codevalue is None:
            raise CremInvalidInputException(
                "check_code: Code value not specified")

        query = ("SELECT b.id "
                 "FROM ct_codes as a "
                 "JOIN ct_codelist as b ON a.codetype=b.codetype "
                 "WHERE b.codetype =%s AND b.value =%s ")
        query_param = (codetype, codevalue,)

        # add project specific constraints if required
        if project is not None:
            query += " AND project LIKE %%s% "
            query_param = query_param + (project, )

        query += " ORDER BY b.rank ASC"
        result = self.multi_row_select(query, query_param)

        if len(result) > 0:
            valid = True
        else:
            valid = False

        return valid

    def set_code(self, codeinfo):
        """Adds a new code to the ct_codelist table

        Returned dict contains:
            codetype  str  valid code type from the ct_codes table
            value     str  code value
            label     str  code label
            upd_by    str  username that performed the operation

        Parameters
        ----------
        codeinfo: dict
            code details to be updated/inserted

        Returns
        -------
        int
            number of records inserted (1 is success)
        int
            ct_codelist record id for the inserted record
        """
        mandatory_keys = ["codetype", "value", "label", "upd_by"]
        self.validate_mandatory_keys(mandatory_keys, codeinfo, "set_code")

        # check if code type exists
        query = ("SELECT `id` "
                 "FROM ct_codes "
                 "WHERE `codetype` =%s")
        query_param = (codeinfo["codetype"], )
        result = self.multi_row_select(query, query_param)
        num = len(result)
        if num == 0:                             # record does not exist
            raise Exception("Codetype {} does not exist"
                            .format(codeinfo["codetype"]))

        num, lastrowid = self.insert("ct_codelist", codeinfo)
        self.log_change("ct_codelist", lastrowid, "insert",
                        codeinfo["upd_by"], codeinfo)
        return num, lastrowid

    def set_process(self, processinfo):
        """Adds a process to the rt_process table

        Returned dict contains:
            requestid    int  requestid associated with process
            process_type str  valid process type  (e.g. extract)
            host         str  host name
            user         str  user name
            uid          int  user id
            pid          int  process id

        Parameters
        ----------
        processinfo: dict
            process information

        Returns
        -------
        int
            number of records inserted (1 is success)
        int
            rt_process record id for the inserted record
        """
        mandatory_keys = ["requestid", "process_type", "host", "user", "uid",
                          "pid"]
        self.validate_mandatory_keys(mandatory_keys, processinfo,
                                     "set_process")

        # check if record exists
        query = ("SELECT `id` "
                 "FROM rt_process "
                 "WHERE `requestid` =%s AND `process_type` =%s "
                 "ORDER BY `upd_date` DESC")
        query_param = (processinfo["requestid"], processinfo["process_type"],)
        result = self.multi_row_select(query, query_param)
        num = len(result)

        # record(s) exists - delete record(s)
        if num >= 1:
            _ = self.del_process(processinfo["requestid"],
                                 processinfo["process_type"])

        # now insert new or updated record [no log for temporary record]
        num, lastrowid = self.insert("rt_process", processinfo)
        return num, lastrowid

    def get_process(self, requestid, process_type):
        """Retrieves current process details for a request.
        Returned dict contains:
            host      str  host name
            user      str  user name
            uid       int  user id
            pid       int  process id
            upd_date  str  date/time process record created

        Parameters
        ----------
        requestid: int
            id for request that process is associated with
        process_type: str
            valid process type  (e.g. extract)

        Returns
        -------
        dict
            process information
        """
        if requestid is None:
            raise CremInvalidInputException(
                "get_process: request identifier must be specified")

        if process_type is None:
            raise CremInvalidInputException(
                "get_process: process type must be specified")

        query = ("SELECT `process_type`,`host`,`user`,`uid`,`pid`,`upd_date` "
                 "FROM rt_process "
                 "WHERE `requestid`=%s AND `process_type`=%s")
        query_param = (requestid, process_type,)
        return self.single_row_select(query, query_param)

    def del_process(self, requestid, process_type):
        """Deletes process record

        Parameters
        ----------
        requestid: int
            id for request that process is associated with
        process_type: str
            valid process type  (e.g. extract)

        Returns
        -------
        int
            number of records deleted
        """
        if requestid is None:
            raise CremInvalidInputException(
                "del_process: request identifier must be specified "
                "and an integer")

        if process_type is None:
            raise CremInvalidInputException(
                "del_process: process type must be specified")

        query_param = {"requestid": requestid, "process_type": process_type}
        return self.delete("rt_process", query_param)

    def get_history(self, requestid, process_type=None):
        """Gets history for a request and optionally for a specific process.
        Status information is presented in datetime order - earliest first.
        Returns list of dicts each containing:
            id               int  id for history record
            process_type     str  process type
            host             str  host name
            user             str  user name
            uid              int  user id
            pid              int  process id
            status_value     str  status code
            notes            str  process log
            processs_status  str  process update
            upd_by           str  user/process for last updated
            upd_date         str  date/time process created

        Parameters
        ----------
        requestid: int
            id for request that process is associated with
        process_type: str
            valid process type  (e.g. extract)

        Returns
        -------
        int
            number of history records retrieved
        list of dict
            history records - one dict per record
        """
        if requestid is None:
            raise CremInvalidInputException(
                "get_history: request identifier must be specified")

        if process_type is None:
            raise CremInvalidInputException(
                "get_history: process type must be specified")

        query = ("SELECT `id`, `requestid`, `process_type`, `host`, `user`, "
                 "`uid`, `pid`, `status_value`, `notes`, `process_status`, "
                 " `upd_by`, `upd_date` "
                 "FROM rt_history WHERE `requestid`=%s ")
        query_param = (requestid, )

        if process_type is not None:
            query += " AND `process_type`=%s"
            query_param = query_param + (process_type,)

        query += " ORDER BY `upd_by`"
        result = self.multi_row_select(query, query_param)
        return len(result), result

    def set_history(self, historyinfo):
        """Add a history record for a request.
        History records are used to record when process status changes and
        when progress needs to be logged in CREM.

        History information provided in dict containing:
            requestid       int  id for associated request
            process_type    str  process type (e.g. extract)
            host            str  (optional) host name
            user            str  (optional) user name
            uid             int  (optional) user id
            pid             int  (optional) process id
            status_value    str  status code associated with record
            notes           str  (optional) process log
            process_status  str  (optional) process update
            upd_by          str  user/process who last updated record

        Parameters
        ----------
        historyinfo: dict
            information to be used to create record

        Returns
        -------
        int
            number of records created
        int
            id of last record created
        """
        mandatory_keys = ["requestid", "process_type", "status_value",
                          "upd_by"]
        self.validate_mandatory_keys(mandatory_keys, historyinfo,
                                     "set_history")

        num, lastrowid = self.insert("rt_history", historyinfo)
        self.log_change("rt_history", lastrowid, "insert",
                        historyinfo["upd_by"], historyinfo)
        return num, lastrowid

    def upd_history(self, historyinfo):
        """Update the most recent history record for a request without
        changing the current overall status.
        Used to indicate progress e.g. number of files processed.
        If the ``notes`` field is updated the new information is
        appended to the existing notes field.  If the ``process_status``
        field is updated it will overwrite the previous value.

        Parameters
        ----------
        historyinfo: dict
            information to be used to update record

        Returns
        -------
        int
            number of records updated
        """
        mandatory_keys = ["requestid", "process_type", "updprocess"]
        self.validate_mandatory_keys(mandatory_keys, historyinfo,
                                     "upd_history")

        if historyinfo["process_status"] is None \
                and historyinfo["notes"] is None:
            raise CremInvalidInputException(
                "upd_history: no new information in update")

        # find the latest record that matches requestid and processtype
        query = ("SELECT `id`, `process_status`, `notes` "
                 "FROM rt_history "
                 "WHERE `requestid`=%s AND `process_type`=%s "
                 "ORDER BY upd_date DESC LIMIT 1")

        query_param = (historyinfo["requestid"], historyinfo["process_type"],)
        result = self.single_row_select(query, query_param)

        if result:
            updateinfo = {"upd_by": historyinfo["updprocess"]}

            # append notes content
            if historyinfo["notes"] is not None:
                updateinfo["notes"] = "{} | {}".format(
                    result["notes"], self.clean_string(historyinfo["notes"]))

            # if not changing process status - leave it as it is
            if historyinfo["process_status"] is not None:
                updateinfo["process_status"] = self.clean_string(
                    historyinfo["process_status"])

            update_param = {"id": result["id"]}
            num = self.update("rt_history", updateinfo, update_param)
            self.log_change("rt_history", result["id"], "update",
                            updateinfo["upd_by"], updateinfo)

        else:
            num = 0     # no record to update

        return num

    def del_history(self, requestid, process_type):
        """Clears history for a request process.

        Parameters
        ----------
        requestid: int
            id for request that history is associated with
        process_type: str
            valid process type  (e.g. extract)

        Returns
        -------
        int
            number of records deleted
        """
        if requestid is None:
            raise CremInvalidInputException(
                "del_history: request identifier must be specified")

        if process_type is None:
            raise CremInvalidInputException(
                "del_history: process type must be specified")

        constraint = {"requestid": requestid, "process_type": process_type}
        return self.delete("rt_history", constraint)

    def get_location(self, locationid, purpose):
        """Gets information on a disk location associated with a request.

        Returns a dict for the location with the following content.
            id        int  id for location in rt_locations
            loctype   str  purpose for location (source|process)
            basepath  str  CDDS basepath to location - not
                           including request related directories
            host      int  host id for preferred compute engine
                           for this location
            valid     bool true if this location is valid for
                           specified use

        Note: If a location is not in database a dictionary will be returned
        with the requestid and valid set to false.

        Parameters
        ----------
        locationid: int
            id for location (from request record)
        purpose: str
            intended purpose for location (source|process)

        Returns
        -------
        dict
            location information
        """
        if locationid is None:
            raise CremInvalidInputException(
                "get_location: location identifier must be specified")

        if purpose not in ["source", "process"]:
            raise CremInvalidInputException(
                "get_location: location purpose is not source or process ")

        # get details for this location
        query = ("SELECT `id`,`name`,`location`,`source`,`process`,"
                 "`processhost`"
                 " FROM ut_locations "
                 "WHERE id = %s")
        query_param = (locationid, )
        result = self.single_row_select(query, query_param)

        valid = False
        if result is None:
            location = {
                "id": locationid, "loctype": purpose, "basepath": "",
                "host": "", "valid": valid}

        else:
            if result[purpose]:   # confirm if location is ok for intended use
                valid = True

            location = {
                "id": result["id"], "name": result["name"],
                "loctype": purpose, "basepath": result["location"],
                "host": result["processhost"], "valid": valid}

        return location

    def get_request(self, requestid):
        """Retrieves request attributes by record id.
        Returns a dict for the request if it is marked as active with the
        following content:
            id              int  id for request (primary key)
            name            str  name (fixed - model_experiment_variant)
            info            str  text description
            projectid       int  id for associated project
            experimentid    int  id for associated experiment
            simulationid    int  id for associated simulation
            package         str  name modifier to identifier partial request
            request_date    str  date request created (HHHH-MM-YY)
            input_format    str  code for input data format
            output_format   str  code for output data format
            delivery_method str  code for product delivery method
            source_loc      str  id for source data location
            process_loc     str  id for processing tasks location
            owner_institute int  id for institute that owns the data
            upd_by          str name of user responsible for last update
            upd_date        date of last update

        Parameters
        ----------
        requestid: int
            request record identifier (primary key)

        Returns
        -------
        dict
            request information
        """
        if requestid is None:
            raise CremInvalidInputException(
                "get_request: request identifier must be specified")

        query = ("SELECT id, name, info, projectid, experimentid, "
                 "simulationid, package, request_date, input_format, "
                 "output_format, delivery_method, source_loc, process_loc, "
                 "owner_institute, upd_by, upd_date "
                 "FROM rt_request "
                 "WHERE `id`= %s and active= 1")
        query_param = (requestid, )
        return self.single_row_select(query, query_param)

    def get_request_primary_key(self, model_id, experiment_id,
                                sub_experiment_id, mip, variant_label,
                                package):
        """
        Return the request primary key from CREM.

        Parameters
        ----------
        model_id : str
            Model identifier (also known as source_id in the CVs), e.g.
            `HadGEM3-GC31-LL`.
        experiment_id : str
            The |experiment identifer|.
        sub_experiment_id : str
            The sub |experiment identifier|.
        mip : str
            The |MIP|.
        variant_label : str
            The |variant label|.
        package : str
            The |package|.

        Returns
        -------
        : int
            The request primary key from CREM.

        Raises
        ------
        CremZeroRecordsException
            If no requests are found.
        RuntimeError
            If more than one request is found.
        """
        # Construct the SQL query
        query = ("SELECT r.id "
                 "FROM rt_request AS r "
                 "INNER JOIN pt_simulation AS s ON r.simulationid = s.id "
                 "INNER JOIN pt_experiment AS e on r.experimentid = e.id "
                 "INNER JOIN pt_project AS p on r.projectid = p.id "
                 "INNER JOIN mt_coupledmodel as m on s.modelid = m.id "
                 "WHERE e.sname = %s AND e.subname = %s AND p.sname = %s "
                 "AND s.realisation = %s AND r.package = %s AND m.sname = %s")
        # CREMdb has blank rather than "none" for sub_experiment_id.
        sub_experiment_id_to_use = ("" if sub_experiment_id == "none"
                                    else sub_experiment_id)
        # Parameters to interpolate
        query_param = (experiment_id, sub_experiment_id_to_use, mip,
                       variant_label, package, model_id)
        # Retrieve results from CREM
        results = self.multi_row_select(query, query_param)
        # Raise errors if we don't have a single record.
        common_msg = ("  model_id = \"{}\",\n"
                      "  experiment_id = \"{}\",\n"
                      "  sub_experiment_id = \"{}\",\n"
                      "  mip = \"{}\",\n"
                      "  variant_label = \"{}\",\n"
                      "  package = \"{}\"")
        if len(results) == 0:
            msg = ("No records found corresponding to:\n" +
                   common_msg.format(model_id, experiment_id,
                                     sub_experiment_id, mip, variant_label,
                                     package))
            raise CremZeroRecordsException(msg)
        if len(results) > 1:
            msg = ("Found multiple requests corresponding to:\n" +
                   common_msg.format(experiment_id, sub_experiment_id,
                                     mip, variant_label, package) +
                   "request ids received: \"{}\"".format(repr(results)))
            raise RuntimeError(msg)
        # Otherwise return our one result!
        return int(results[0]['id'])

    def find_request(self, constraint):
        """Finds active request records that match search constraint.
        Returns a list of dicts for each matching request.
        Contents for each dict are as defined for get_request.

        Parameters
        ----------
        constraint: dict
            search criteria (field: value pairs)

        Returns
        -------
        int
            number of records found
        list of dicts
            dict for each request record
        """
        query = ("SELECT id, name, info, projectid, experimentid, "
                 "simulationid, package, request_date, input_format, "
                 "output_format, delivery_method, source_loc, process_loc, "
                 "upd_by, upd_date "
                 "FROM rt_request "
                 "WHERE active=1 ")
        # add where constraints
        query_param = ()
        for field, value in constraint.items():
            query += " AND `{}`= %s ".format(field)
            query_param = query_param + (value,)

        query += " ORDER BY projectid, experimentid, name "

        request = self.multi_row_select(query, query_param)
        return len(request), request

    def set_request(self, fields, updby):
        """Creates new active request record.
        Request information provided in dict as defined for get_request
        - mandatory fields are:
            name          str  name for request (unique within project)
            projectid     int  id for associated project
            experimentid  int  id for associated experiment
            input_format  str  code for input data format
            source_loc    str  code for location of source database

        Parameters
        ----------
        fields: dict
            field values for request (field: value pairs)
        updby: str
            process name or user responsible for creating request

        Returns
        -------
        int
            number of records inserted (should be 1)
        int
            id for record inserted
        """
        mandatory_keys = ["name", "projectid", "experimentid", "input_format"]
        self.validate_mandatory_keys(mandatory_keys, fields, "set_request")

        if updby is None:
            raise CremInvalidInputException(
                "set_request: creator not specified when creating "
                "new data request")

        if "request_date" not in fields:
            now = datetime.now()
            fields["request_date"] = now.strftime("%Y-%m-%d")

        # add creator to request attributes
        fields["upd_by"] = updby

        # check that request is not a duplicate for this projectid
        constraint = {"projectid": fields["projectid"], "name": fields["name"]}
        num, _ = self.find_request(constraint)
        if num != 0:
            raise CremInvalidInputException(
                "set_request: data request with that name already exists "
                "for this project")

        num, lastrowid = self.insert("rt_request", fields)
        self.log_change("rt_request", lastrowid, "insert", updby, fields)
        return num, lastrowid

    def set_request_data(self, requestid, dataitems, updby):
        """Adds data items to existing request.
        Each data item must include the following information:
            simulationid  int  record id for simulation
            runid         int  record id for model run
            stream        str  stream name (e.g. apa)
            streamtype    str  stream format (e.g. pp, nc)
            streaminit    int  file reinitialisation period in hours
            start_date    str  start date for this request (optional)
            end_date      str  end date for this request (optionsl
            extract_order int  extract order (optional)

        Note: If start_date and/or end_date are not provided then
        the simulation start/end dates in the pt_modelrun table
        are assumed.

        Parameters
        ----------
        requestid: int
            id for request record
        dataitems: list of dict
            data item information - dict per data item

        Returns
        -------
        int
            number of records inserted
        """
        # check arguments
        if requestid is None:
            raise CremInvalidInputException(
                "set_request_data: request identifier must be specified")

        if dataitems is None:
            raise CremInvalidInputException(
                "set_request_data: must provide information for associated "
                "data items")

        for item in dataitems:
            mandatory_keys = ["runid", "stream", "streamtype"]
            self.validate_mandatory_keys(mandatory_keys, item,
                                         "set_request_data")

        # check request exists
        request = self.get_request(requestid)
        if request is None:
            raise CremZeroRecordsException(
                "set_request_data: no request found matching specified "
                "request id")

        # add a record for each data item
        count = 0
        for item in dataitems:
            item["requestid"] = requestid
            item["upd_by"] = updby
            num, lastrowid = self.insert("rt_requestdata", item)
            if num == 1:
                self.log_change("rt_requestdata", lastrowid, "insert", updby,
                                item)
                count += 1

        return count

    def upd_request(self, requestid, fields):
        """Updates information in existing request.
        Can change any field in the request table with the EXCEPTION
        of the following fields:
            name           name for request (unique within project)
            projectid      id for associated project
            experimentid   id for associated experiment
            input_format   code for input data format

        Parameters
        ----------
        requestid: int
            id for request to be updated
        fields: dict
            field values to be updated (field: value pairs)

        Returns
        -------
        int
            number of records updated (should be 1)
        """
        # check that changes do NOT include id, name, projectid or experimentid
        if "requestid" in fields:
            raise CremInvalidInputException(
                "upd_request: cannot change request identifier")
        if "name" in fields:
            raise CremInvalidInputException(
                "upd_request: cannot change request name")
        if "projectid" in fields:
            raise CremInvalidInputException(
                "upd_request: cannot change associated project identifier")
        if "experimentid" in fields:
            raise CremInvalidInputException(
                "upd_request: cannot change associated experiment identifier")

        if self.get_request(requestid):       # check if request exists
            fields["o_type"] = "REQUEST"
            num = self.update("rt_request", fields, {"id": requestid})
        else:
            raise CremInvalidInputException(
                "upd_request: request does not exist - unable to update")

        return num

    def del_request(self, requestid):
        """Deletes request record and associated data items,
        status information and history information.

        Parameters
        ----------
        requestid: int
            id for request to be deleted

        Returns
        -------
        int
            number of request records deleted (should be 1)
        """
        if requestid is None:
            raise CremInvalidInputException(
                "del_request: request identifier must be specified")

        # delete associated details records then request record
        constraint = {"requestid": requestid}
        _ = self.delete("rt_requestdata", constraint)    # data items
        _ = self.delete("rt_history", constraint)        # history
        _ = self.delete("rt_status", constraint)         # status
        return self.delete("rt_request", {"id": requestid})

    def get_request_status(self, requestid, process=None):
        """Retrieves status information for the specified request.

        Returned dict contains following keys:
           status_type   str  status type code (e.g. extract)
           status_value  str  status value code
                              (e.g. IP - extract in progress)
           status_info   str  additional information
           upd_by        str  user/process who last added status
           upd_date      str  date status last updated

        Parameters
        ----------
        requestid: int
            id for request
        process: str
            process type (e.g. extract) - optional

        Returns
        -------
        int
            number of status records retrieved
        list of dict
            status records - dict per record
        """
        if requestid is None:
            raise CremInvalidInputException(
                "get_request_status: request identifier must be specified")

        if process is None:
            query = ("SELECT process_type, status_value, status_info, "
                     "upd_by, upd_date "
                     "FROM rt_status "
                     "WHERE `requestid`=%s ORDER BY upd_date ASC")
            query_param = (requestid, )
            status_rs = self.multi_row_select(query, query_param)
        else:
            query = ("SELECT process_type, status_value, status_info, "
                     "upd_by, upd_date "
                     "FROM rt_status "
                     "WHERE `requestid`=%s AND `process_type`=%s "
                     "ORDER BY upd_date ASC")
            query_param = (requestid, process,)
            status_rs = self.single_row_select(query, query_param)

        num = len(status_rs)
        if num <= 0:       # no status information matching requestid/process
            status_rs = None

        return num, status_rs

    def set_request_status(self, status):
        """Sets or updates the status value for a specified process associated
        with a specified request.

        Status information supplied must include:
            requestid     int  id for request
            process_type  str  process type (e.g extract)
            status_value  str  status value to be applied (e.g IP)
            upd_by        str  user or process responsible for status change

        Parameters
        ----------
        status: dict
            status information to be created/updated

        Returns
        -------
        bool
            True if status record has been created or updated
        """
        mandatory_keys = ["requestid", "process_type", "status_value",
                          "upd_by"]
        self.validate_mandatory_keys(mandatory_keys, status,
                                     "set_request_status")

        # check if supplied process code value is valid
        if not self.check_code("process_type", status["process_type"]):
            raise CremInvalidInputException(
                "set_request_status: process type [{}] does not "
                "have valid value".format(status["process_type"]))

        # check if supplied status code value is valid for this process
        if not self.check_code("process_status", status["status_value"]):
            raise CremInvalidInputException(
                "set_request_status: status type [{}] does not "
                "have valid value".format(status["status_value"]))

        # delete any existing status record for this process
        query_param = {"requestid": status["requestid"],
                       "process_type": status["process_type"]}
        _ = self.delete("rt_status", query_param)

        # insert new status record
        rows, _ = self.insert("rt_status", status)
        if rows == 1:
            status_rs = True
        else:
            status_rs = False

        return status_rs

    def get_request_data(self, requestid, stream=""):
        """Gets information data items for specified request.
        The data item retrieval can be constrained by optional data
        stream argument.

        Information for each data item (dict) contains
            runid          int  id for model run record
            suiteid        str  simulation configuration for run
                                (suite id, e.g. ajhog)
            simulationid   int  id for simulation record
            stream         str  data stream name (e.g. apa)
            streamtype     str  data stream type (e.g. pp)
            streaminit     int  data stream reinitialisation interval
                                (hours e.g. 240)
            start_date     str  start date for data required (YYYY-MM-DD)
            end_date       str  end date for data required (YYYY-MM-DD)
            extract_order  int  order in which to extract data streams
            skip           int  if set ignore this data item

        Parameters
        ----------
        requestid: int
            record id for the request
        stream: str
            data stream name e.g. apa (optional

        Returns
        -------
        int
            number of request data item records retrieved
        list of dict
            data item information - dict per data item
        """
        if requestid is None:
            raise CremInvalidInputException(
                "get_request_data: request identifier must be specified")

        query = ("SELECT runid, suiteid, stream, streamtype, streaminit, "
                 "a.start_date as start_date, a.end_date as end_date, "
                 "sim_start_date, sim_end_date, extract_order, skip "
                 "FROM rt_requestdata as a "
                 "LEFT JOIN pt_modelrun as b ON a.runid=b.id "
                 "WHERE `requestid`= %s ")
        query_param = (requestid, )

        if stream:
            query += " AND `stream`= %s "
            query_param = query_param + (stream, )

        query += " ORDER BY extract_order"
        dataitem = self.multi_row_select(query, query_param)

        # resolve start and end dates
        for row in dataitem:
            if row["start_date"] is None:
                row["start_date"] = row["sim_start_date"]
            if row["end_date"] is None:
                row["end_date"] = row["sim_end_date"]

        return len(dataitem), dataitem

    def get_extract_filter(self, requestid, datastream, experiment="all"):
        """Returns filter records for MOOSE extraction process

        The optional experiment argument is used to retrieve additional
        stash codes that are not part of the standard stash set.

        The returned json string contains the following for each variable
               name         variable short name
               table        MIP table name
               status       status value for filter
               constraint   mapping expression

        Parameters
        ----------
        requestid: int
            record id for request
        datastream: str
            datastream name (e.g. apa)
        experiment: str
            experiment short name e.g. rcp45 (optional)

        Returns
        -------
        str
            json encoded string with filter information
        """
        if requestid is None:
            raise CremInvalidInputException(
                "get_extract_filter: request identifier must be specified")

        if datastream is None:
            raise CremInvalidInputException(
                "get_extract_filter: data stream must be specified")

        # find model id
        request = self.get_request(requestid)
        project = self.get_project_by_id(request["projectid"])
        simulation = self.get_simulation_by_id(int(request["simulationid"]))
        model = self.get_model_by_id(simulation["modelid"])

        query = ("SELECT variable, miptable, model, stream, filters, "
                 "projects, experiments "
                 "FROM rt_filter "
                 "WHERE `projects` LIKE %s AND `model` = %s "
                 "AND `stream`= %s ")
        query_param = ("%" + project["sname"] + "%", model["sname"],
                       datastream, )

        if experiment != "all":
            query += " AND `experiments` LIKE %s"
            query_param = query_param + ("%" + experiment + "%", )

        query += " ORDER BY `variable`"
        result = self.multi_row_select(query, query_param)

        if len(result) != 0:
            # construct data structure to be output in json
            json_arr = {datastream: []}
            for row in result:
                var = {"name": row["variable"], "table": row["miptable"],
                       "status": "ok", "constraint": []}
                stash_list = row["filters"].split(";")
                for constraint in stash_list:
                    constraint_d = {}
                    constraint_list = constraint.split(",")
                    for item in constraint_list:
                        item.replace(" ", "")
                        elem = item.split("=", 1)
                        constraint_d[elem[0]] = elem[1]
                    var["constraint"] = constraint_d
                json_arr[datastream].append(var)

            json_str = json.dumps(json_arr)    # encode json string
        else:
            json_str = None

        return json_str

    def get_person_by_id(self, personid):
        """Retrieves contact and institute information for a person.
        Returns dict with the following content:
            title       str  person title
            firstname   str  person first name
            familyname  str  person family name
            position    str  position/role
            email       str  email address
            weblink     str  URL to web page
            inst_code   str  institute short name/code
            inst_name   str  institute full name
            inst_link   str  institute web site URL

        Parameters
        ----------
        personid: int
            record id for person

        Returns
        -------
        dict
            person information (field:value pairs)
        """
        if personid is None:
            raise CremInvalidInputException(
                "get_person_by_id; person identifier must be specified")

        query = ("SELECT title, firstname, familyname, position, email, "
                 "a.weblink as weblink, b.sname as inst_code, "
                 "b.name as inst_name, b.weblink as inst_link "
                 "FROM ut_person as a "
                 "JOIN ut_institute as b ON a.institute=b.id "
                 "WHERE a.id= %s ")
        query_param = (personid, )
        return self.single_row_select(query, query_param)

    def get_responsible_party(self, entity, entityid, role=""):
        """Gets responsible party information.
        Responsible parties (persons or institutes) are associated with
        a specific entity in CREM (e.g. a project).  The search can
        also be constrained by an optional role (e.g. project lead).

        The information returned for each party can be an institute,
        a person or both.

        Dictionary keys for person related attributes are prefixed
        with "p_" and for institute related attributes are
        prefixed with "i_".

          o_type          str  entity type (e.g experiment)
          o_id            int  entity record id
          role            str  responsible party role

          p_id            int  id for person record
          p_title         str  person title
          p_firstname     str  person first name
          p_familyname    str  person family name
          p_position      str  position in institute
          p_address       str  address
          p_city          str  city
          p_adminarea     str  county/state
          p_postcode      str  postcode
          p_country       str  country
          p_phone         str  telephone
          p_email         str  email
          p_weblink       str  person web page
          p_permanent_id  str  personal id
          p_cim_id        str  esdoc CIM record id for person

          i_id            int  id for institute record
          i_sname         str  institute acronym/short name
          i_name          str  institute full name
          i_address       str  address
          i_city          str  city
          i_adminarea     str  county/state
          i_postcode      str  postcode
          i_country       str  country
          i_weblink       str  institute web page
          i_cim_id        str  esdoc CIM record id for institute

        Parameters
        ----------
        entity: str
            type of entity (e.g. experiment)
        entityid: int
            record id for entity
        role: str
            role constraint e.g. contact, project manager etc. (optional)

        Returns
        -------
        int
            number of responsible parties returned
        list of dict
            responsible party information - dict per party
        """
        if entity is None:
            raise CremInvalidInputException(
                "get_responsible_party: entity type must be specified "
                "(e.g. experiment)")
        if entityid is None:
            raise CremInvalidInputException(
                "get_responsible_party: entity record id "
                "must be specified")

        # entity_valid = self.check_code("entity_type", entity)
        # if not entity_valid:
        #     raise CremInvalidInputException(
        #         "get_responsible_party: entity type [%s]is not recognised"
        #         % entity)

        if role:
            role_valid = self.check_code("party_role", role)
            if not role_valid:
                raise CremInvalidInputException(
                    "get_responsible_party: specified role [{}] "
                    "is not recognised".format(role))

        # query has to deal with the problem of a responsible party being
        # either a person, a person associated with an institute, or just an
        # institute.  In each case the institute information has to be
        # obtained with different joins
        query = ("SELECT o_type, o_id, role,  "
                 "b.id as p_id,b.title as p_title,b.firstname as p_firstname, "
                 "b.familyname as p_familyname, b.position as p_position, "
                 "b.address as p_address, b.city as p_city, "
                 "b.adminarea as p_adminarea, b.postcode as p_postcode, "
                 "b.country as p_country, b.phone as p_phone, "
                 "b.email as p_email, b.weblink as p_weblink, "
                 "b.permanent_id as p_permanent_id, b.cim_id as p_cim_id, "
                 "c.id as c_id, c.sname as c_sname, c.name as c_name, "
                 "c.address as c_address, c.city as c_city, "
                 "c.adminarea as c_adminarea, c.postcode as c_postcode, "
                 "c.country as c_country, c.weblink as c_weblink, "
                 "c.cim_id as c_cim_id, "
                 "d.id as d_id, d.sname as d_sname, d.name as d_name, "
                 "d.address as d_address, d.city as d_city, "
                 "d.adminarea as d_adminarea, d.postcode as d_postcode, "
                 "d.country as d_country, d.weblink as d_weblink, "
                 "d.cim_id as d_cim_id "
                 "FROM ut_contactrole as a "
                 "LEFT JOIN ut_person as b ON a.personid = b.id AND "
                 "a.personid IS NOT NULL "
                 "LEFT JOIN ut_institute as c ON b.institute = c.id "
                 "LEFT JOIN ut_institute as d ON a.instituteid = d.id AND "
                 "a.instituteid IS NOT NULL "
                 "WHERE `o_type` = %s AND `o_id` = %s ")
        query_param = (entity, entityid)

        if role:
            query += " AND `role`= %s "
            query_param = query_param + (role, )

        party = self.multi_row_select(query, query_param)

        # remove unused institute fields and rename institute fields
        remove_c = {"i_id": "c_id", "i_sname": "c_sname", "i_name": "c_name",
                    "i_address": "c_address", "i_city": "c_city",
                    "i_adminarea": "c_adminarea", "i_postcode": "c_postcode",
                    "i_country": "c_country", "i_weblink": "c_weblink",
                    "i_cim_id": "c_cim_id"}
        remove_d = {"i_id": "d_id", "i_sname": "d_sname", "i_name": "d_name",
                    "i_address": "d_address", "i_city": "d_city",
                    "i_adminarea": "d_adminarea", "i_postcode": "d_postcode",
                    "i_country": "d_country", "i_weblink": "d_weblink",
                    "i_cim_id": "d_cim_id"}

        for _, row in enumerate(party):
            if row["c_id"] is None or row["c_id"] == "":
                for key in remove_c:
                    row.pop(key, None)
                for key, val in remove_d.items():
                    row[key] = row.pop(val)
            else:
                for key in remove_d:
                    row.pop(key, None)
                for key, val in remove_c.items():
                    row[key] = row.pop(val)

        return len(party), party

    def get_institute_by_id(self, instituteid):
        """Retrieves information for an institute.

        Returned dict contains:
            sname      str  short name/code for institute
            name       str  full name for institute
            address    str  street address for institute
            city       str  city for institute
            adminarea  str  state/county
            postcode   str  post code
            country    str  country
            weblink    str  URL for institute

        Parameters
        ----------
        instituteid: int
            record id for institute

        Returns
        -------
        dict
            institute information (field:value pairs)
        """
        if instituteid is None:
            raise CremInvalidInputException(
                "get_institute_by_id; institute identifier must be specified")

        query = ("SELECT sname, name, address, city, adminarea, postcode, "
                 "country, weblink "
                 "FROM ut_institute "
                 "WHERE id= %s ")
        query_param = (instituteid, )
        return self.single_row_select(query, query_param)

    def set_project(self, projectinfo):
        """Adds a new record to pt_project or updates an existing one

        Project dict should contain:
            id          int  (optional) id of record to be updated,
                             None for insert
            programmeid int  Foreign key for programme this project
                             belongs too
            name        str  Project full name
            sname       str  Project canonical name
            info        str  Project description
            weblink     str  URL to project website
            dataowner   int  Foreign key for institute owning data
            datalicense int  id for data license in ut_commontxt
            datause     str  id for data use restrictions in ut_commontxt
            upd_by      str  username of a user responsible for the last
                             update
        Parameters
        ----------
        projectinfo: dict
            project information (field:value pairs)

        Returns
        -------
        int
            number of rows inserted (0 if update)
        int
            id for record inserted/updated
        """
        if "id" in projectinfo:
            # update - check if record exists
            row = self.get_project_by_id(projectinfo["id"])
            if row:
                try:
                    timestamp = time.time()
                    projectinfo["upd_date"] = datetime.fromtimestamp(
                        timestamp).strftime("%Y-%m-%d %H:%M:%S")
                    pkey = projectinfo.pop("id")
                    _ = self.update("pt_project", projectinfo, {"id": pkey})
                    self.log_change("pt_project", pkey, "update",
                                    projectinfo["upd_by"], projectinfo)
                    return 0, pkey
                except Exception as exp:
                    raise exp
            else:
                raise CremZeroRecordsException(
                    "Could not find a project with id {0}"
                    .format(projectinfo["id"]))
        else:
            # insert
            mandatory_keys = ["name", "sname", "programmeid", "dataowner",
                              "upd_by"]
            self.validate_mandatory_keys(mandatory_keys, projectinfo,
                                         "set_project")
            try:
                num, lastrowid = self.insert("pt_project", projectinfo)
                self.log_change("pt_project", lastrowid, "insert",
                                projectinfo["upd_by"], projectinfo)
            except Exception as exp:
                raise exp

            return num, lastrowid

    def del_project(self, projectid, user="NA"):
        """Deletes a single project.

        Parameters
        ----------
        projectid: int
            id for project record to be deleted
        user: str
            user or process deleting the project

        Returnsmax length of method name
        -------
        int
            number of records deleted (1 is success)
        """
        num = self.delete("pt_project", {"id": projectid})
        self.log_change("pt_project", projectid, "delete", user)
        return num

    def get_project_by_id(self, projectid):
        """Retrieves project information by project record id.

        Will exclude projects marked as not visible

        Returns dict with following information:
            sname         str   shortname for project (e.g. cmip5)
            name          str   full name for project
            info          str   short description of project
            weblink       str   URL for project website
            datalicense   str   text with data license constraints
            datause       str   text with data access constraints
            dataowner     str   institute that owns the data
                                (for data processed by MOHC
                                on behalf of another organisation)
            pname         str   programme name from pt_programme
            visible       str   visibility flag for the project
            configdefault str   default setting for cdds config version
                                for this project
            upd_by        str   user/process responsible for last update
            upd_date      str   date for last update (YYYY-MM-DD)
            esdoc_id      str   id from esdoc specialisation
            esdoc_hash    str   hash from esdoc specialisation

        Parameters
        ----------
        projectid: int
            id for project record

        Returns
        -------
        dict
            project information
        """
        if projectid is None:
            raise CremInvalidInputException(
                "get_project_by_id; project identifier must be specified")

        query = ("SELECT a.sname, a.name, a.info, a.weblink, a.datalicense, "
                 "a.datause, a.configdefault, a.upd_by, a.upd_date, "
                 "a.visible, a.esdoc_id, a.esdoc_hash, b.sname as pname, "
                 "c.sname as dataowner "
                 "FROM pt_project as a "
                 "LEFT JOIN ut_institute as c ON a.dataowner=c.id "
                 "JOIN pt_programme as b ON a.programmeid=b.id "
                 "WHERE a.id= %s AND a.visible!='FF' ")
        query_param = (projectid, )
        return self.single_row_select(query, query_param)

    def get_project_by_name(self, name, programmeid=None,
                            check_visibility=False):
        """Retrieves project information by project name
        The search may be constrained to only retrieve projects that
        are marked as visible, and/or associated with a particular
        programme.

        The dict returned for each project will be the same as defined
        for get_project_by_id with the addition of:
            id  int   project record identifier

        Parameters
        ----------
        name: str
            project name
        programmeid: int
            id for programme to constrain project search (optional)
        check_visibility: bool
            if True will only retrieve projects marked as visible (optional)

        Returns
        -------
        int
            number of projects retrieved
        list of dict
            project information - dict per project
        """
        if name is None:
            raise CremInvalidInputException(
                "get_project_by_name: project name must be specified ")

        query = ("SELECT a.id, a.sname, a.name, a.info, a.weblink, "
                 "a.datalicense, a.datause, a.configdefault, a.upd_by, "
                 "a.upd_date, a.visible, a.esdoc_id, a.esdoc_hash, "
                 "b.sname as pname, c.sname as dataowner "
                 "FROM pt_project as a  "
                 "JOIN pt_programme as b ON a.programmeid=b.id "
                 "LEFT JOIN ut_institute as c ON a.dataowner=c.id "
                 "WHERE a.sname= %s")
        if check_visibility:
            query += " AND a.visible != 'FF'"

        if programmeid is not None:
            query += " AND a.programmeid = %s"
            query_param = (name, programmeid, )
        else:
            query_param = (name, )

        project = self.multi_row_select(query, query_param)
        return len(project), project

    def list_projects_by_programme_id(self, programme_id,
                                      check_visibility=True):
        """Retrieves all projects associated with a given programme.

        Returned list of dicts contains for each project:
            id          str     id of the project
            sname       str     canonical name of the project
            name        str     long name of the project
            visible     str     visibility flag for the project
            esdoc_id    str     id from esdoc specialisation
            esdoc_hash  str     hash from esdoc specialisation

        Parameters
        ----------
        programme_id: int
            id for programme record in pt_programme
        check_visibility: bool
            if True will only retrieve projects marked as visible (optional)

        Returns
        -------
        int
            number of projects retrieved
        list of dict
            project information - dict per project
        """
        query = ("SELECT a.id, a.sname, a.name, a.visible, a.esdoc_id, "
                 "a.esdoc_hash "
                 "FROM pt_project a "
                 "JOIN pt_programme as b ON a.programmeid=b.id "
                 "WHERE b.id= %s ")

        if check_visibility:
            query += " AND a.visible != 'FF'"

        query_param = (programme_id, )
        projects = self.multi_row_select(query, query_param)
        return len(projects), projects

    def get_experiment_by_id(self, experimentid):
        """
        Retrieves experiment information by experiment record id:
            sname          str     shortname for experiment
            subname        str     sub-experiment name
            name           str     full name for experiment
            info           str     short description of experiment
            weblink        str     URL for experiment website
            projectid      int     id for project
            areatype       str     code for global or regional experiment
            areacode       str     project specific code for experiment area
            ensemblesize   int     no. of elements in ensemble
            ensembletype   str     code for ensemble type
            upd_by         str     user/process responsible for last update
            upd_date       str     date for last update (YYYY-MM-DD)
            esdoc_id       str     id from esdoc specialisation
            esdoc_hash     str     hash from esdoc specialisation

        Parameters
        ----------
        experimentid: int
            id for experiment record of interest

        Returns
        -------
        dict
            experiment information (field:value pairs)
        """
        if experimentid is None:
            raise CremInvalidInputException(
                "get_experiment_by_id: experiment identifier "
                "must be specified")

        query = ("SELECT sname, subname, name, info, weblink, projectid, "
                 "areatype, areacode, ensemblesize, ensembletype, upd_date, "
                 "upd_by, esdoc_id, esdoc_hash "
                 "FROM pt_experiment "
                 "WHERE `id`= %s ")
        query_param = (experimentid, )
        return self.single_row_select(query, query_param)

    def get_experiment_by_name(self, name, projectid=None):
        """Fetches one or more experiments matching a given name.

        Returned dict contains following information for each
        experiment:
            id             int     id of experiment record
            sname          str     shortname for experiment (e.g. cmip5)
            subname        str     subexperiment name
            name           str     full name for experiment
            info           str     short description of experiment
            weblink        str     URL for experiment website
            projectid      int     id for project
            areatype       str     code for global or regional experiment
            areacode       str     project specific code for experiment area
            ensemblesize   int     no. of elements in ensemble
            ensembletype   str     code for ensemble type
            upd_by         str     user/process responsible for last update
            upd_date       str     date for last update (YYYY-MM-DD)
            esdoc_id       str     id from esdoc specialisation
            esdoc_hash     str     hash from esdoc specialisation
            project_name   str     project name

        Parameters
        ----------
        name: str
            canonical name of the experiment to search
        projectid: int
            id of project (optional constraint)

        Returns
        -------
        int
            number of experiment records returned
        list of dict
            experiment information - dict per experiment
        """
        if name is None:
            raise CremInvalidInputException(
                "get_experiment_by_name: experiment name must be specified")

        query = ("SELECT a.id, a.sname, a.subname, a.name, a.info, "
                 "a.weblink, a.projectid, a.areatype, a.areacode, "
                 "a.ensemblesize, a.ensembletype, a.upd_date, a.upd_by, "
                 "a.esdoc_id, a.esdoc_hash, "
                 "b.sname as project_name "
                 "FROM pt_experiment a "
                 "JOIN pt_project b ON b.id = a.projectid "
                 "WHERE a.sname= %s ")

        if projectid is not None:
            query += " AND a.projectid = %s"
            query_param = (name, projectid, )
        else:
            query_param = (name, )

        experiment = self.multi_row_select(query, query_param)
        return len(experiment), experiment

    def set_experiment(self, expinfo):
        """Adds a new record to experiment or updates an existing one

        Experiment information dict may contain:
            id           primary key of the experiment
            projectid    id of the governing project
            sname        canonical experimentname
            subname      experiment subname
            name         full experiment name
            info         experiment description
            weblink      URL to further information on experiment
            areatype     global or regional
            areacode     reference to domain from the pt_domain table
            ensemblesize total number of elements in ensemble
            ensembletype coded rip value indicating how ensemble is
                         constructed
            upd_by       username of a user that updated the record
            esdoc_id     id from esdoc specialisation
            esdoc_hash   hash from esdoc specialisation

        Parameters
        ----------
        expinfo: dict
            experiment information

        Returns
        -------
        int
            number of rows inserted/updated (1 is success)
        int
            id for record inserted/updated
        """
        if "id" in expinfo:
            # update - check if record exists
            row = self.get_experiment_by_id(expinfo["id"])
            if row:
                try:
                    timestamp = time.time()
                    expinfo["upd_date"] = datetime.fromtimestamp(
                        timestamp).strftime("%Y-%m-%d %H:%M:%S")
                    pkey = expinfo.pop("id")

                    _ = self.update("pt_experiment", expinfo, {"id": pkey})
                    self.log_change("pt_experiment", pkey, "update",
                                    expinfo["upd_by"], expinfo)
                    return 0, pkey
                except Exception as exp:
                    # just in case we want to implement transaction management
                    raise exp
            else:
                raise CremZeroRecordsException(
                    "Could not find an experiment with id {0}".
                    format(expinfo["id"]))
        else:
            # insert
            mandatory_keys = ["projectid", "sname", "name", "ensembletype",
                              "upd_by"]
            self.validate_mandatory_keys(mandatory_keys, expinfo,
                                         "set_experiment")
            try:
                num, lastrowid = self.insert("pt_experiment", expinfo)
                self.log_change("pt_experiment", lastrowid, "insert",
                                expinfo["upd_by"], expinfo)
            except Exception as exp:
                raise exp

            return num, lastrowid

    def del_experiment(self, experimentid):
        """Deletes experiment record

        Parameters
        ----------
        experimentid: int
            id of the experiment record to be deleted

        Returns
        -------
        int
            number of records deleted (1 is success)
        """
        query_param = {"id": experimentid}
        return self.delete("pt_experiment", query_param)

    def list_experiments_by_project_id(self, project_id):
        """Retrieves all experiments associated with a given project.

        Returned list of dicts contain:
            id          str  id of the experiment
            sname       str  canonical name of the experiment
            subname     str  subname of the experiment
            name        str  long name of the experiment
            esdoc_id    str  id from esdoc specialisation
            esdoc_hash  str  hash from esdoc specialisation

        Parameters
        ----------
        project_id: int
            id for project of interest

        Returns
        -------
        int
            number of experiment records
        list of dict
            experiment information - dict per experiment
        """
        query = ("SELECT a.id, a.sname, a.subname, a.name, a.esdoc_id, "
                 "a.esdoc_hash "
                 "FROM pt_experiment a "
                 "JOIN pt_project as b ON a.projectid=b.id "
                 "WHERE b.id = %s ")
        query_param = (project_id, )
        experiments = self.multi_row_select(query, query_param)
        return len(experiments), experiments

    def get_requirement_by_id(self, requirement_id):
        """
        Retrieves requirement by its identifier

        Returned dict contains:
            parent_id      str  id of a parent
            parent_type    str  experiment/requirement
            s_name         str  canonical name
            s_label        str  CIM label
            s_info         str  CIM description
            s_required     str  conformance requirement flag
            s_reqt_type    str  coded value for CIM requirement type
            s_keywords     str  keywords related to requirement
            s_scope        str  requirement scope
            s_ordinal      str  requirement delivery order
            conform_status str  conformance status
            conform_method str  conformance method
            conform_info   str  additional conformance description
            upd_date       str  date of last update
            upd_by         str  person responsible for last update
            esdoc_id       str  id from esdoc specialisation
            esdoc_hash     str  hash from esdoc specialisation

        Parameters
        ----------
        requirement_id: int
            id for requirement of interest

        Returns
        -------
        dict
            requirement information (field: value pairs)
        """
        if requirement_id is None:
            raise CremInvalidInputException(
                "get_requirement_by_id: requirement identifier "
                "must be specified")

        query = ("SELECT parent_id, parent_type, s_name, s_label, s_info, "
                 "s_required, s_reqt_type, s_keywords, s_scope, s_ordinal, "
                 "conform_status, conform_method, conform_info, upd_date, "
                 "upd_by, esdoc_id, esdoc_hash "
                 "FROM pt_requirement "
                 "WHERE `id`= %s ")
        query_param = (requirement_id, )
        return self.single_row_select(query, query_param)

    def get_requirement_by_name(self, name, parent_id=None,
                                parent_type="EXPERIMENT"):
        """Retrieves one or more requirement matching given name,
        parent_id, and parent_type.
        Returned list of dicts as defined for get_requirement_by_id.

        Parameters
        ----------
        name: str
            canonical name of requirement to search for
        parent_id: int
            parent id (optional)
        parent_type: str
            parent type - 'EXPERIMENT' and 'REQUIREMENT' (optional)

        Returns
        -------
        int
            number of requirements found
        list of dict
            requirements information - dict per requirement
        """
        if name is None:
            raise CremInvalidInputException(
                "get_requirement_by_name: requirement name "
                "must be specified")

        query = ("SELECT id, parent_id, parent_type, s_name, s_label, "
                 "s_info, s_required, s_reqt_type, s_keywords, s_scope, "
                 "s_ordinal, conform_status, conform_method, conform_info, "
                 "upd_date, upd_by, esdoc_id, esdoc_hash "
                 "FROM pt_requirement "
                 "WHERE s_name= %s ")

        if parent_type is not None or parent_id is not None:
            if parent_type not in ["EXPERIMENT", "REQUIREMENT"]:
                raise CremInvalidInputException("wrong parent type " +
                                                parent_type)
            query += " AND parent_id = %s AND parent_type= %s"
            query_param = (name, parent_id, parent_type, )
        else:
            query_param = (name, )

        requirement = self.multi_row_select(query, query_param)
        return len(requirement), requirement

    def set_requirement(self, reqinfo):
        """Adds a new requirement or updates an existing one.

            id             int  id of a requirement
            parent_id      int  id of a parent
            parent_type    str  experiment or requirement
            s_name         str  canonical name
            s_label        str  CIM label
            s_info         str  CIM description
            s_required     str  conformance requirement flag
            s_reqt_type    str  coded value for CIM requirement type
            s_keywords     str  keywords related to requirement
            s_scope        str  requirement scope
            s_ordinal      str  requirement delivery order
            conform_status str conformance status
            conform_method str conformance method
            conform_info   str additional conformance description
            upd_date       str  date of last update (YYYY-MM-DD)
            upd_by         str  user responsible for last update

        Parameters
        ----------
        reqinfo: dict

        Returns
        -------
        int
            number of rows inserted
        int
            id of inserted/updated requirement record
        """
        if "id" in reqinfo:
            # update - check if record exists
            row = self.get_requirement_by_id(reqinfo["id"])
            if row:
                try:
                    timestamp = time.time()
                    reqinfo["upd_date"] = datetime.fromtimestamp(
                        timestamp).strftime("%Y-%m-%d %H:%M:%S")
                    pkey = reqinfo.pop("id")

                    _ = self.update("pt_requirement", reqinfo, {"id": pkey})
                    self.log_change("pt_requirement", pkey, "update",
                                    reqinfo["upd_by"], reqinfo)
                    return 0, pkey
                except Exception as exp:
                    raise exp
            else:
                raise CremZeroRecordsException(
                    "Could not find a requirement with id {0}".format(
                        reqinfo["id"]))
        else:
            # insert
            mandatory_keys = ["parent_id", "parent_type", "s_name",
                              "s_required", "s_reqt_type", "upd_by"]
            self.validate_mandatory_keys(mandatory_keys, reqinfo,
                                         "set_requirement")
            try:
                num, lastrowid = self.insert("pt_requirement", reqinfo)
                self.log_change("pt_requirement", lastrowid, "insert",
                                reqinfo["upd_by"], reqinfo)
            except Exception as exp:
                raise exp

            return num, lastrowid

    def del_requirement(self, requirementid, cascade=True):
        """Deletes requirement record

        Parameters
        ----------
        requirementid: int
            id of the requirement to be deleted
        cascade: bool
            true if delete sub-requirements and attributes

        Returns
        -------
        int
            number of records deleted
        """
        if cascade:
            # delete sub requirements
            _, rows = self.list_requirements_by_parent_id(requirementid,
                                                          "REQUIREMENT")
            for row in rows:
                self.del_requirement(row["id"], False)

            # delete attributes
            _, rows = self.list_attributes_by_requirement_id(
                requirementid)
            for row in rows:
                self.del_reqt_attribute(row["id"])

        query_param = {"id": requirementid}
        return self.delete("pt_requirement", query_param)

    def list_requirements_by_parent_id(self, parent_id,
                                       parent_type="EXPERIMENT"):
        """Fetches all requirements associated with a parent record
        (which might be an experiment or another requirement)

        Returned requirements dict contains information as defined for
        get_requirement_by_id.

        Parameters
        ----------
        parent_id: int
            id of parent (experiment or requirement) record
        parent_type: str
            'EXPERIMENT' or 'REQUIREMENT'

        Returns
        -------
        int
            number of requirements retrieved
        list of dict
            requirements information - dict per requirement
        """
        query = ("SELECT id, parent_id, parent_type, s_name, s_label, "
                 "s_info, s_required, s_reqt_type, s_keywords, s_scope, "
                 "s_ordinal, conform_status, conform_method, conform_info "
                 "upd_date, upd_by, esdoc_id, esdoc_hash "
                 "FROM pt_requirement "
                 "WHERE parent_id = %s AND parent_type = %s ")
        query_param = (parent_id, parent_type, )
        requirements = self.multi_row_select(query, query_param)
        return len(requirements), requirements

    def set_reqt_attribute(self, reqattinfo):
        """Inserts new requirement attribute.

        reqattinfo dict should contain the following information:
            requirementid  int  id of the requirement the attribute is
                                associated with
            meta_type      str  attribute type
            meta_value     str  attribute value
            upd_by         str  user performing the insert operation

        Parameters
        ----------
        reqattinfo: dict
            requirement attribute information

        Returns
        -------
        int
            number of rows inserted (1 if success)
        int
            record id of inserted requirement attribute
        """
        mandatory_keys = ["requirementid", "meta_type", "meta_value", "upd_by"]
        self.validate_mandatory_keys(mandatory_keys, reqattinfo,
                                     "set_reqt_attribute")

        try:
            num, lastrowid = self.insert("pt_reqt_attribute", reqattinfo)
            self.log_change("pt_reqt_attribute", lastrowid, "insert",
                            reqattinfo["upd_by"], reqattinfo)
        except Exception as exp:
            raise exp

        return num, lastrowid

    def del_reqt_attribute(self, reqt_attribute_id):
        """Deletes requirement attribute record

        Parameters
        ----------
        reqt_attribute_id: int
            id for requirement attribute of interest

        Returns
        -------
        int
            number of records deleted (1 is success)
        """
        query_param = {"id": reqt_attribute_id}
        return self.delete("pt_reqt_attribute", query_param)

    def list_attributes_by_requirement_id(self, requirement_id):
        """Retrieves all attributes associated with a requirement.
        Returns list of dicts each containing:
            id          int  attribute id
            meta_type   str  attribute type
            meta_value  str  attribute value
            upd_by      str  user responsible for last update
            upd_date    str  time of last update

        Parameters
        ----------
        requirement_id: int
            id for requirement of interest
        Returns
        -------
        int
            number of attributes retrieved
        list of dict
            requirement attribute information - dict per attribute
        """
        query = ("SELECT id, meta_type, meta_value, upd_by, upd_date "
                 "FROM pt_reqt_attribute "
                 "WHERE requirementid = %s ")
        query_param = (requirement_id, )
        req_attributes = self.multi_row_select(query, query_param)
        return len(req_attributes), req_attributes

    def get_simulation_by_id(self, simulationid):
        """Retrieves simulation information by simulation record id.
        Returned information in dict:
            sname               str  shortname for experiment
            name                str  full name for experiment
            info                str  short description of experiment
            weblink             str  URL for experiment website
            projectid           int  id for project
            experimentid        int  id for experiment
            modelid             int  id for configured model
            model_type          str  model type information
            suiteid             str  suite id for simulation
            configversion       str  cdds config version used for this
                                     simulation processing
            modelversion        str  model version code
            timestep            str  model timestep
            calendar            str  calendar type
            start_date          str  start date (YYYY-MM-DD)
            end_date            str  end date (YYYY-MM-DD)
            realisation         str  realisation (rip) code
            parent_relation     str  code to define relation between parent
                                     and this simulation
            parent_project      int  id for project of parent simulation
            parent_model        int  id for model used for parent simulation
            parent_experiment   str  name of parent experiment
            parent_realisation  str  parent realisation code

            parent_basedate     str  basedate in parent ((YYYY-MM-DD)
            parent_branch       str  date of branch in parent (YYYY-MM-DD)
            child_basedate      str  basedate in child ((YYYY-MM-DD)
            child_branch        str  date of branch in child (YYYY-MM-DD)

            bound_project       str  (regional) - boundary project code
            bound_model         str  (regional) - boundary model name
            bound_simulation    str  (regional) - boundary simulation name
            upd_by              str  user/process responsible for last update
            upd_date            str  date of last update (YYYY-MM-DD)

        Parameters
        ----------
        simulationid: int
            id for simulation record of interest

        Returns
        -------
        dict
            simulation information (field: value pairs)
        """
        if simulationid is None:
            raise CremInvalidInputException(
                "get_simulation_by_id: simulation identifier "
                "must be specified")

        query = ("SELECT sname, name, info, weblink, projectid, experimentid, "
                 "modelid, suiteid, configversion, modelversion, "
                 "timestep, calendar, start_date, end_date, realisation, "
                 "model_config as model_type, "
                 "pnt_type as parent_relation, "
                 "pnt_project as parent_project, "
                 "pnt_model as parent_model, "
                 "pnt_experiment as parent_experiment, "
                 "pnt_realisation as parent_realisation, "
                 "pnt_basedate_parent as parent_basedate, "
                 "pnt_branch_parent as parent_branch, "
                 "pnt_basedate_child as child_basedate, "
                 "pnt_branch_child as child_branch, "
                 "bnd_project as boundary_project, "
                 "bnd_model as boundary_model, "
                 "bnd_experiment as boundary_experiment, "
                 "bnd_realisation as boundary_realisation, upd_date, upd_by  "
                 "FROM pt_simulation "
                 "WHERE `id`= %s ")
        query_param = (simulationid, )
        return self.single_row_select(query, query_param)

    def get_modelrun_by_id(self, modelrunid):
        """Retrieves model run information by model run record id.
        Returned information in dict:
            suiteid         str  UM run or ROSE suite
            branch          str  branch of suite
            revision        str  suite revision
            simulationid    int  id for simulation record
            start_date      str  start date for model run (YYYY-MM-DD)
            end_date        str  end date for model run (YYYY-MM-DD)
            sim_start_date  str  start date for simulation (YYYY-MM-DD)
            sim_ends_date   str  start date for simulation (YYYY-MM-DD)
            atmos_mean      str  atmosphere meaning date (YYYY-MM-DD)
            ocean_mean      str  ocean meaning date (YYYY-MM-DD)
            weblink         str  URL to model run information
            upd_by          str  user/process responsible for last update
            upd_date        str  date of last update (YYYY-MM-DD)

        Parameters
        ----------
        modelrunid: int
            id for model run of interest

        Returns
        -------
        dict
            model run information
        """
        if modelrunid is None:
            raise CremInvalidInputException(
                "get_modelrun_by_id: model run identifier must be specified")

        query = ("SELECT suiteid, runname as branch, revision, simulationid, "
                 "start_date, end_date, sim_start_date, sim_end_date, "
                 "atmos_mean, ocean_mean, weblink, upd_by, upd_date "
                 "FROM pt_modelrun "
                 "WHERE `id`= %s ")
        query_param = (modelrunid, )
        return self.single_row_select(query, query_param)

    def get_model_by_id(self, modelid):
        """Retrieves coupled model information by model record id.
        Returned information in dict:
            sname          str     short name for model (e.g. HadGEM3)
            name           str     full name including sub-models
            modeltype      str     code for model type
            info           str     model top level description
            version        str     model version
            releasedate    str     date model released (YYYY-MM-DD)
            specialisation str     vocabulary specialisation
            weblink        str     URL to model information
            upd_by         str     user/process responsible for last update
            upd_date       str     date of last update (YYYY-MM-DD)

        Parameters
        ----------
        modelid: int
            id for coupled model of interest

        Returns
        -------
        dict
            model information (field: value pairs)
        """
        if modelid is None:
            raise CremInvalidInputException(
                "get_model_by_id: model identifier must be specified")

        query = ("SELECT sname, name, info, modeltype, version, releasedate, "
                 "specialisation, weblink, upd_by, upd_date "
                 "FROM mt_coupledmodel "
                 "WHERE `id`= %s ")
        query_param = (modelid, )
        return self.single_row_select(query, query_param)

    def get_grid_by_id(self, gridid):
        """Retrieves grid information by grid record id.
        Returned information in dict:
            sname          str     short name for grid
            name           str     full name
            info           str     model top level description
            cmip_label     str     grid label used for CMIP data sets
            horizontal_construction str horizontal construction method
            vertical_construction str vertical construction method
            dimensions     str     number of dimensions
            cells          str     resolution code (e.g. N96L85)
            horizontal_resolution str approximate horizontal resolution
            vertical_layers       str number of vertical layers
            isuniform      str     1 if uniform grid otherwise 0
            isregular      str     1 if regular grid otherwise 0
            datum          str     datum for this grid
            realms         str     list of realms reporting on this grid
            upd_date       str     date of last update (YYYY-MM-DD)

        Parameters
        ----------
        gridid: int
            id for grid record of interest

        Returns
        -------
        dict
            grid information (field: value pairs)
        """
        if gridid is None:
            raise CremInvalidInputException(
                "get_grid_by_id: grid identifier must be specified")

        query = ("SELECT sname, name, info, cmip_label, "
                 "horizontal_construction, vertical_construction, dimensions, "
                 "cells, horizontal_resolution, vertical_layers, isuniform, "
                 "isregular, datum, realms, upd_date "
                 "FROM mt_grid "
                 "WHERE `id`= %s ")
        query_param = (gridid, )
        return self.single_row_select(query, query_param)

    def list_grids_by_modelid(self, modelid):
        """Retrieves grid information for a component model.
        Returns list of dicts each containing:
            sname          str  short name for grid
            name           str  full name
            info           str  model top level description
            cmip_label     str  grid label used for CMIP data sets
            horizontal_construction str horizontal construction method
            vertical_construction str vertical construction method
            dimensions     str  number of dimensions
            cells          str  resolution code (e.g. N96L85)
            horizontal_resolution  str  approx horizontal resolution
            vertical_layers  str number of vertical layers
            isuniform      str  1 if uniform grid otherwise 0
            isregular      str  1 if regular grid otherwise 0
            datum          str  datum for this grid
            realms         str  list of realms reporting on this grid
            upd_date       str  date of last update (YYYY-MM-DD)

        Parameters
        ----------
        modelid: int
            id for component model of interest

        Returns
        -------
        int
            number of grid records retrieved
        list of dict
            grid information - dict per grid
        """
        if modelid is None:
            raise CremInvalidInputException(
                "list_grids_by_modelid: model identifier must be specified")

        query = ("SELECT sname, name, info, cmip_label, "
                 "horizontal_construction, vertical_construction, dimensions, "
                 "cells, horizontal_resolution, vertical_layers, isuniform, "
                 "isregular, datum, realms, upd_date "
                 "FROM mt_grid "
                 "WHERE `modelid`= %s ")
        query_param = (modelid, )
        grids = self.multi_row_select(query, query_param)
        return len(grids), grids

    def list_couplings_by_modelid(self, modelid):
        """Retrieves coupling information for a coupled model.
        Returns list of dicts each containing:
            id        str  coupling id
            modelid   str  record id for component model (submodel)
            coupler   str  coupler technology/approach used
            coupled   str  summary of coupled variables and how they are
                             coupled
            info      str  description of coupling
            upd_date  str  time of last update
        Parameters
        ----------
        modelid: int
            id of coupled model of interest

        Returns
        -------
        list of dict
            coupling information for model - dict per coupling
        """
        query = ("SELECT id, modelid, coupler, coupled, info, upd_date "
                 "FROM mt_coupling "
                 "WHERE coupledmodelid = %s ")
        query_param = (modelid, )
        couplings = self.multi_row_select(query, query_param)
        return len(couplings), couplings

    def get_submodel_by_id(self, modelid):
        """Retrieves component model information by model record id.
        Returned information in dict:
            sname            str  short name for model (e.g. HadGEM3)
            name             str  full name including sub-models
            info             str  model top level description
            version          str  model version
            code_repository  str  model code repository address
            code_language    str  coding language for submodel
            tuning           str  model tuning details
            grid_id          str  id for grid record mt_grid
            grid_code        str  code for grid (e.g. N96L38, ORCA12)
            grid_info        str  model grid description
            modeltype        str  code for model type
            releasedate      str  date model released (YYYY-MM-DD)
            weblink          str  URL to model information
            upd_date         str  date of last update (YYYY-MM-DD)

        Parameters
        ----------
        modelid: int
            id for component model record of interest

        Returns
        -------
        dict
            component model information
        """
        if modelid is None:
            raise CremInvalidInputException(
                "get_submodel_by_id: model identifier must be specified")

        query = ("SELECT sname, name, info, version, "
                 "code_repository, code_language, grid_id, grid_code, "
                 "grid_info, tuning, modeltype, releasedate, weblink, "
                 "upd_date "
                 "FROM mt_model WHERE `id`= %s ")
        query_param = (modelid, )
        return self.single_row_select(query, query_param)

    def get_domain_by_id(self, domainid):
        """Retrieves domain information by id.
        Returned information in dict:
            id              str  domain id
            sname           str  domain short name
            name            str  domain full name
            info            str  domain description
            realm           str  realm code for this domain
            specialisation  str  specialisation code for this domain
            upd_date        str  time of last update
            esdoc_id        str  id for esdoc specialisation record
            esdoc_hash      str  hash for esdoc specialisation record

        Parameters
        ----------
        domainid: int
            if for domain record of interest

        Returns
        -------
        dict
            domain record information
        """
        if domainid is None:
            raise CremInvalidInputException(
                "get_domain_by_id: domain identifier must be specified")

        query = ("SELECT id, sname, name, info, realm, specialisation, "
                 "upd_date "
                 "FROM mt_domain "
                 "WHERE `id` = %s ")
        query_param = (domainid, )
        return self.single_row_select(query, query_param)

    def list_domains_by_submodelid(self, submodelid):
        """Retrieves all domains (realms) associated with a
        specific component model.

        Returns list of dicts each containing:
            id                str  domain id
            sname             str  domain short name
            name              str  domain full name
            info              str  domain description
            realm             str  realm code for this domain
            specialisation    str  specialisation code for this domain
            upd_date          str  time of last update
            esdoc_id        str  id for esdoc specialisation record
            esdoc_hash      str  hash for esdoc specialisation record
        Parameters
        ----------
        submodelid: int
            id of component model of interest

        Returns
        -------
        int
            number of domain records retrieved
        list of dict
            domain records - dict per record
        """
        query = ("SELECT id, sname, name, info, realm, specialisation, "
                 "upd_date, esdoc_id, esdoc_hash "
                 "FROM mt_domain "
                 "WHERE `modelid` = %s ")

        query_param = (submodelid, )
        domains = self.multi_row_select(query, query_param)
        return len(domains), domains

    def list_topics_by_parent(self, parentid, parent_type):
        """Retrieves all topics associated with either a DOMAIN,
        a GRID or a PROCESS (aka topic)

        Returns list of dicts each containing:
            id              str  topic id
            topic_type      str  domain short name
            s_id            str  specialisation id for topic
            s_label         str  specialisation label for topic
            s_desc          str  specialisation description for topic
            description     str  text description of the process covered
                                 by the topic
            implementation  str  text describing how process was implemented
            keywords        str  list of keywords associated with topic
            specifiedby     str  person responsible for providing topic content
            upd_date        str  time of last update
            esdoc_id        str  id for esdoc specialisation record
            esdoc_hash      str  hash for esdoc specialisation record
        Parameters
        ----------
        parentid: int
            id for entity of interest
        parent_type: str
            code for parent type (e.g DOMAIN|GRID|PROCESS)

        Returns
        -------
        int
            number of topics retrieved
        list of dict
            topic information - dict per topic
        """
        query = ("SELECT id, topic_type, s_id, s_label, s_desc, description, "
                 "implementation, keywords, specifiedby, upd_date, esdoc_id, "
                 "esdoc_hash "
                 "FROM mt_topic "
                 "WHERE `o_id` = %s AND `o_type` = %s "
                 "ORDER BY FIELD(topic_type, 'KEY', 'GRID', 'PROCESS', "
                 "'SUBPROCESS'), s_label")

        query_param = (parentid, parent_type)
        topics = self.multi_row_select(query, query_param)
        return len(topics), topics

    def list_properties_by_topic(self, topicid):
        """Retrieves all model properties associated with a topic

        Returns list of dicts each containing:
            id              str  property id
            s_group_id      str  specialisation group id code
            s_group_label   str  specialisation group label
            s_id            str  specialisation property id code
            s_label         str  specialisation property label
            s_desc          str  specialisation property description
            s_cardinality   str  specialisation property cardinality code
            s_type          str  specialisation property type code
            s_enum_id       str  code for associated enumeration list
                                 if this property is an enum type
            s_enum_open     str  if 1 enumeration list is extensible
            value           str  setting for model property
            notes           str  notes asociated with the property response
            nullreason      str  reason given for no response
            specifiedby     str  person responsible for providing topic content
            upd_date        str  time of last update
            esdoc_id        str  id for esdoc specialisation record
            esdoc_hash      str  hash for esdoc specialisation record
        Parameters
        ----------
        topicid: int
            id for topic of interest

        Returns
        -------
        int
            number of properties for this topic
        list of dict
            property information - dict per property
        """
        query = ("SELECT id, s_group_id, s_group_label, s_group_description, "
                 "s_id, s_label, s_desc, s_cardinality, s_type, s_enum_id, "
                 "s_enum_open, value, notes, nullreason, specifiedby, "
                 "upd_date, esdoc_id, esdoc_hash "
                 "FROM mt_property "
                 "WHERE `topicid` = %s "
                 "ORDER BY `s_group_label`, `s_display`")
        query_param = (topicid, )
        properties = self.multi_row_select(query, query_param)
        return len(properties), properties

    def list_enums_by_property(self, propertyid):
        """Retrieves all enum values associated with a property with
        a type of enum

        Returns list of dicts each containing:
            id              str  enum value id
            s_value         str  value for enumeration item
            s_label         str  label for enumeration item
            s_desc          str  description for enumeration item
            s_extend        str  if 1 this is an additional local item in the
                                 list of enumerations - otherwise was
                                 provided by specialisation
            s_display       str  display order (integer)
            upd_date        str  time of last update
            esdoc_id        str  id for esdoc specialisation record
            esdoc_hash      str  hash for esdoc specialisation record

        Parameters
        ----------
        propertyid: int
            id of property of interest

        Returns
        -------
        int
            number of enumeration values for the property
        list of dict
            enumeration information - dict per value
        """
        query = ("SELECT id, s_value, s_label, s_desc, extend, display, "
                 "upd_date, esdoc_id, esdoc_hash "
                 "FROM mt_propenum "
                 "WHERE `propertyid` = %s "
                 "ORDER BY display")
        query_param = (propertyid, )
        enums = self.multi_row_select(query, query_param)
        return len(enums), enums

    def get_references(self, entity, entityid, context=""):
        """Gets references associated with an entity (e.g experiment).  Also
        supports retrieving references with a specific purpose -
        e.g. a citation for a model

        Returns dict with the following information for each reference:
            id           int  record id
            entity_type  str  entity type (e.g. experiment)
            entity_name  str  short name for entity item (e.g. ssp45)
            purpose      str  purpose of reference (e.g. reference)
            authors      str  document authors
            date         str  date of publication (year)
            title        str  document title
            detail       str  document publication details
            doi          str  document digital object identifier
            weblink      str  url for document
            format       str  document format
            cim_id       str  id for reference in esdoc system
            upd_date     str  date reference last updated

        Parameters
        ----------
        entity: str
            type of entity (e.g. experiment)
        entityid: int
            record id for entity
        context: str
            reference context constraint (e.g. citation)

        Returns
        -------
        int
            number of references returned
        list of dict
            references - dict per reference
        """
        if entity is None:
            raise CremInvalidInputException(
                "get_references: entity type must be specified "
                "(e.g. experiment)")
        if entityid is None:
            raise CremInvalidInputException(
                "get_references: entity record id must be specified")

        if context:
            purpose_valid = self.check_code("reference_context", context)
            if not purpose_valid:
                raise CremInvalidInputException(
                    "get_references: specified context [{}] is "
                    "not recognised".format(context))

        query_param = (entity, entityid)
        query = ("SELECT b.id, a.o_type as entity_type, "
                 "a.o_name as entity_name, purpose, authors, date, title, "
                 "detail, doi, weblink, format, cim_id, a.upd_date "
                 "FROM ut_referencelist as a "
                 "JOIN ut_reference as b ON a.referenceid = b.id "
                 "WHERE `o_type` = %s AND `o_id` = %s ")

        if context:
            query += " AND `purpose`= %s "
            query_param = query_param + (context, )

        query += "ORDER BY authors, date ASC"

        refs = self.multi_row_select(query, query_param)
        return len(refs), refs

    def get_file_manifest_by_id(self, manifestid):
        """Retrieves file manifest information for a data request.  Returned
        information:
            id              str  id for file manifest record
            filename        str  file name
            start_date      str  start date/time for data in file
            end_date        str  end date/time for data in file
            version         str  version code for file when put in MASS
            create_date     str  date/time file was created
            transfer_date   str  date/time file was transferred
            checksum        str  checksum for file
            projectid       str  id for project that file belongs too
            requestid       str  id for request that file belongs too
            upd_by          str  person/process for last update of this record
            upd_date        str  date/time for last update  of this record
        Parameters
        ----------
        manifestid: int
            id for manifest record of interest

        Returns
        -------
        dict
            manifest record field values
        """
        if manifestid is None:
            raise CremInvalidInputException(
                "get_file_manifest_by_id: "
                "manifest identifier must be specified")

        query = ("SELECT id, filename, start_date, end_date, version, "
                 "create_date, transfer_date, checksum, projectid, requestid, "
                 "upd_by, upd_date "
                 "FROM rt_file_manifest "
                 "WHERE `id` = %s ")
        query_param = (manifestid, )
        return self.single_row_select(query, query_param)

    def get_file_manifest_by_request(self, requestid):
        """Retrieves file manifest information for a data request.  Returned
        information:
            id              str  id for file manifest record
            filename        str  file name
            start_date      str  start date/time for data in file
            end_date        str  end date/time for data in file
            version         str  version code for file when put in MASS
            create_date     str  date/time file was created
            transfer_date   str  date/time file was transferred
            checksum        str  checksum for file
            projectid       str  id for project file belongs too
            upd_by          str  person/process for last update of this record
            upd_date        str  date/time for last update  of this record

        Parameters
        ----------
        requestid: int
            id for request of interest

        Returns
        -------
        int
            number of manifest records returned
        list of dict
            manifest records - dict per record
        """
        if requestid is None:
            raise CremInvalidInputException(
                "get_file_manifest_by_request: "
                "request identifier must be specified")

        query = ("SELECT id, filename, start_date, end_date, version, "
                 "create_date, transfer_date, checksum, projectid, requestid, "
                 "upd_by, upd_date "
                 "FROM rt_file_manifest "
                 "WHERE `requestid` = %s ")
        query_param = (requestid, )
        manifest = self.multi_row_select(query, query_param)
        return len(manifest), manifest

    def set_file_manifest(self, manifestinfo):
        """Adds a new manifest record or updates an existing one

        Experiment information dictionary should/may contain:
            id              str  primary key of the experiment
                                 (required if updating)
            filename        str  file name
            start_date      str  start date/time for data in file
            end_date        str  end date/time for data in file
            version         str  version code for file when put in MASS
            create_date     str  date/time file was created
            transfer_date   str  date/time file was transferred
            checksum        str  checksum for file
            projectid       str  id for project file belongs too
            requestid       str  if for request file belongs too
            upd_by          str  person/process inserting/updating record

        Parameters
        ----------
        manifestinfo: dict
            manifest record information (field: value pairs)

        Returns
        -------
        int
            number of rows inserted/updated (should be 1)
        int
            id of record inserted/updated
        """
        if "id" in manifestinfo:
            # update
            # check if record exists
            row = self.get_file_manifest_by_id(manifestinfo["id"])
            if row:
                try:
                    pkey = manifestinfo.pop("id")
                    _ = self.update("rt_file_manifest", manifestinfo,
                                    {"id": pkey})
                    self.log_change("rt_file_manifest", pkey, "update",
                                    manifestinfo["upd_by"], manifestinfo)
                    return 0, pkey
                except Exception as exp:
                    # just in case we want to implement transaction management
                    raise exp
            else:
                raise CremZeroRecordsException(
                    "Could not find an experiment with id {0}".
                    format(manifestinfo["id"]))
        else:
            # insert
            mandatory_keys = [
                "filename", "create_date", "transfer_date", "upd_by"]
            self.validate_mandatory_keys(mandatory_keys, manifestinfo,
                                         "set_file_manifest")

            try:
                num, lastrowid = self.insert("rt_file_manifest", manifestinfo)
                self.log_change("rt_file_manifest", lastrowid, "insert",
                                manifestinfo["upd_by"], manifestinfo)
            except Exception as exp:
                raise exp

            return num, lastrowid

    def del_file_manifest(self, manifestid=None, requestid=None):
        """Deletes file manifest record by id, or request id
        Parameters
        ----------
        manifestid: int
            id of the manifest record to delete
        requestid: int
            id of request for which manifest records are to be deleted

        Returns
        -------
        int
            number of records deleted
        """
        if requestid is None:
            query_param = {"id": manifestid}
        else:
            query_param = {"requestid": requestid}

        return self.delete("rt_file_manifest", query_param)

    @staticmethod
    def validate_mandatory_keys(keys, fields, method):
        """Tests if a dictionary contains listed keys.
        Parameters
        ----------
        keys: list
            list of mandatory keys
        fields: dict
            dict of fields to be inserted into table
        method: str
            method name

        Returns
        -------
        bool
            True if mandatory keys ok else raise exception
        """
        for mandatory_key in keys:
            if mandatory_key not in fields or fields[mandatory_key] is None:
                raise CremInvalidInputException(
                    "{0}: {1} not specified when creating {0}"
                    .format(method, mandatory_key))
        return True

    def get_user_by_name(self, name):
        """Retrieves user information by name.

        Parameters
        ----------
        name: str
            user name

        Returns
        -------
        dict
            user record field values
        """
        if name is None:
            raise CremInvalidInputException(
                "get_user_by_name: user name must be specified ")

        query = ("SELECT username, email, fullname, groupid, active "
                 "FROM ct_users  "
                 "WHERE username = %s")
        query_param = (name, )

        return self.single_row_select(query, query_param)

    def log_change(self, table, rowid, operation, user, fields=None):
        """A simple logging method serialising and storing information
        about database changes in the importer_audit table.

        Parameters
        ----------
        table: str
            name of a table affected by operation
        rowid: int
            id of table row affected by operation
        operation: str
            one of the following: insert/update/delete
        user: str
            username that performed the operation
        fields: dict
            dict containing data to be inserted/updated

        Returns
        -------
        bool
            True if change successfully logged
        """
        if operation in ["insert", "update", "delete"]:
            timestamp = datetime.fromtimestamp(time.time())
            data = {
                "tablename": table,
                "tid": rowid,
                "action": operation,
                "datetime": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "user": user
            }
            if operation == "update" or operation == "insert":
                data["description"] = json.dumps(fields)

            _, _ = self.insert("at_audit_log", data)
        else:
            raise Exception("Invalid operation type {0}".format(operation))
        return True

    def get_license_text_by_id(self, license_id):
        """
        Return the license text held in the ``ut_commontxt`` table with
        under the supplied ID

        Parameters
        ----------
        license_id: int
            License identifier (primary key in ``ut_commontxt``)

        Returns
        -------
        : str
            License text.
        """
        query = ("SELECT content "
                 "FROM ut_commontxt "
                 "WHERE category = %s AND id = %s")

        query_params = ('data_license', license_id)
        return self.single_row_select(query, query_params)
