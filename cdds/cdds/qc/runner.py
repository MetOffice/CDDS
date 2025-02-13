# (C) British Crown Copyright 2018-2024, Met Office.
# Please see LICENSE.md for license details.

import logging
import datetime
import time
import os
import inspect
import json
from compliance_checker.runner import CheckSuite
from cdds.common.constants import (
    APPROVED_VARS_FILENAME_TEMPLATE,
    APPROVED_VARS_FILENAME_STREAM_TEMPLATE,
)
from cdds.common.plugins.plugins import PluginStore
from cdds.common.sqlite import execute_insert_query
from cdds.qc.plugins.base.dataset import StructuredDataset
from cdds.qc.common import NoDataForQualityCheck
from cdds.qc.models import (
    setup_db,
    get_qc_runs, get_qc_files, get_error_counts, get_aggregated_errors,
    get_validated_variables
)
from cdds.qc.constants import (
    STATUS_ERROR, STATUS_WARNING, STATUS_IGNORED,
    SUMMARY_STARTED, SUMMARY_FAILED, SUMMARY_PASSED,
    QC_REPORT_STREAM_FILENAME, QC_REPORT_FILENAME)
from cdds.qc.contiguity_checker import CollectionsCheck


class QCRunner(object):
    """Wrapper class for managing QC run configuration"""

    def __init__(self, db_path, create_db=True):
        """Constructor

        Parameters
        ----------
        db_path: string
            path to the sqlite3 database
        create_db: bool
            If true the database file will be created on the fly
        """
        if not os.path.isfile(db_path) and not create_db:
            raise Exception(
                "Database file {} does not exist, provide a correct location"
                " or run models.py to initialise it".format(db_path))
        self.check_suite = None
        self.db = setup_db(db_path)
        self.logger = logging.getLogger(__name__)

    def init_suite(self, check_suite, dataset, relaxed_cmor=False):
        """
        Configures IOOS QC checker and prepares a dataset to be checked

        Parameters
        ----------
        check_suite: CheckSuite
            An instance of ioos qc checker
        dataset: StructuredDataset
            An instance of a dataset to be qc-ed
        relaxed_cmor: bool
            If set to True then CMIP6 checks will be performed with relaxed CMOR validation
        """

        assert isinstance(check_suite, CheckSuite)
        assert isinstance(dataset, StructuredDataset)

        self.check_suite = check_suite
        self.check_suite.load_all_available_checkers()
        self.relaxed_cmor = relaxed_cmor
        self.dataset = dataset

    def get_checks(self, checker_name):
        """
        A helper method listing all avaiable and loaded checks

        Parameters
        ----------
        checker_name: string
            Name of a checker to inspect

        Returns
        -------
        : list
            A list of checker methods
        """

        assert self.check_suite.checkers, "No checkers could be found"
        assert checker_name in self.check_suite.checkers, (
            "Checker {} does not exist".format(checker_name))

        methods = inspect.getmembers(
            self.check_suite.checkers[checker_name](), inspect.ismethod)
        return [x[0] for x in methods if x[0].startswith("check_")]

    def run_tests(self, mip_tables_dir, request, run_id=None):
        """
        Runs all ioos and ad-hoc checks

        Parameters
        ----------
        mip_tables_dir: str
            Path to a directory with mip tables files
        request: cdds.common.request.request.Request
            Request object
        run_id: int
            An arbitrary identifier that can be used for grouping multiple qc
            runs

        Returns
        -------
        : int
            Run id of the test.
        """
        plugin = PluginStore.instance().get_plugin()
        cv_prefix = plugin.mip_table_prefix()
        cv_location = os.path.join(mip_tables_dir, '{}{}_CV.json'.format(cv_prefix, request.metadata.mip_era))

        conf = {
            "cmip6": {
                "mip_tables_dir": mip_tables_dir,
                "cv_location": cv_location,
                "request": request,
                "relaxed_cmor": self.relaxed_cmor,
                "global_attributes_cache": self.dataset.global_attributes_cache
            },
            "cf17": {
                "standard_names_version": request.common.standard_names_version,
                "standard_names_dir": request.common.standard_names_dir,
                "global_attributes_cache": self.dataset.global_attributes_cache
            },
            "cordex": {
                "mip_tables_dir": mip_tables_dir,
                "cv_location": cv_location,
                "request": request,
                "global_attributes_cache": self.dataset.global_attributes_cache
            }
        }
        for checker_key in conf.keys():
            if checker_key not in self.check_suite.checkers.keys():
                msg = "Could not find qc plugin {}. Please make sure it has been installed.".format(checker_key)
                self.logger.critical(msg)
                raise ModuleNotFoundError(msg)

        if self.dataset.file_count == 0:
            message = 'No data found for QC to check.'
            self.logger.critical(message)
            raise NoDataForQualityCheck(message)

        if run_id is None:
            run_id = int(time.time())
        self.logger.info("Starting QC tests")
        cursor = self.db.cursor()
        execute_insert_query(cursor, "qc_run", {
            "basepath": self.dataset.root,
            "run_id": run_id,
            "mip_table": self.dataset.mip_table
        })
        self.db.commit()
        qc_run_id = cursor.lastrowid
        contiguity_checker = CollectionsCheck(request)
        self.logger.info("Checking filenames")
        file_errors = self.dataset.check_filenames_and_sizes()
        self.logger.info("Checking time contiguity")
        crs = contiguity_checker.perform_checks(self.dataset)
        aggr = self.dataset.get_aggregated_files(False)
        self.logger.info("Checking individual files")

        est_count = self.dataset.file_count
        counter = 0
        for index in aggr:
            for data_file in aggr[index]:
                drs = index.split('_')
                if request.common.force_plugin == 'CORDEX':
                    execute_insert_query(cursor, "qc_dataset", {
                        "qc_run_id": qc_run_id,
                        "filename": os.path.basename(data_file),
                        "variable_directory": os.path.dirname(data_file),
                        "summary": SUMMARY_STARTED,
                        "realization_index": index,
                        "model": drs[1],
                        "experiment": drs[6],
                        "mip_table": drs[2],
                        "variant": drs[3],
                        "variable": self.dataset.var_names[index],
                        "variable_name": self.dataset.var_names[index],
                        "grid": drs[4],
                    })
                else:
                    execute_insert_query(cursor, "qc_dataset", {
                        "qc_run_id": qc_run_id,
                        "filename": os.path.basename(data_file),
                        "variable_directory": os.path.dirname(data_file),
                        "summary": SUMMARY_STARTED,
                        "realization_index": index,
                        "model": drs[1],
                        "experiment": (drs[2] + " : " + drs[3]
                                       if drs[3] != 'none' else drs[2]),
                        "mip_table": drs[4],
                        "variant": drs[5],
                        "variable": drs[6],
                        "variable_name": self.dataset.var_names[index],
                        "grid": drs[7],
                    })
                self.db.commit()
                qc_dataset_id = cursor.lastrowid
                with self.check_suite.load_dataset(data_file) as ds:
                    if request.common.force_plugin == 'CORDEX':
                        output = self.check_suite.run(ds, conf, [], "cf17", "cordex")
                    else:
                        output = self.check_suite.run(ds, conf, [], "cf17", "cmip6")
                invalid = self._parse_and_log(cursor, output, qc_dataset_id)
                if data_file in crs[1] and crs[1][data_file]:
                    for msg in crs[1][data_file]:
                        execute_insert_query(cursor, "qc_message", {
                            "qc_dataset_id": qc_dataset_id,
                            "message": msg["message"],
                            "status": STATUS_ERROR,
                            "checker": crs[0],
                        })
                        self.db.commit()
                    invalid = True

                if data_file in file_errors:
                    for msg in file_errors[data_file]:
                        execute_insert_query(cursor, "qc_message", {
                            "qc_dataset_id": qc_dataset_id,
                            "message": msg,
                            "status": STATUS_ERROR,
                            "checker": "Filename and size checker",
                        })
                        self.db.commit()
                    invalid = True

                cursor.execute(
                    "UPDATE qc_dataset "
                    "SET summary = ? "
                    "WHERE id = ?", (
                        SUMMARY_FAILED if invalid else SUMMARY_PASSED,
                        qc_dataset_id
                    )
                )
                self.db.commit()
                counter += 1
                if counter % 100 == 0:
                    self.logger.info(
                        "Completed {}/{}".format(counter, est_count))
        self.logger.info("All tests completed")
        cursor.execute(
            "UPDATE qc_run "
            "SET finished = ? "
            "WHERE id = ?", (
                datetime.datetime.utcnow(),
                qc_run_id
            )
        )
        self.db.commit()
        return run_id

    def generate_report(self, run_id, location="", process_all=False,
                        with_details=False):
        """
        Generates a json report for a given run_id

        Parameters
        ----------
        run_id: int
            An arbitrary identifier that can be used for grouping multiple qc
            runs
        location: str
            Where to save the report
        process_all: boolean
            If True, the report won't ignore some dubious CF warnings
        with_details: boolean
            If True, the report will include the "details section"
        """
        datetime_suffix = str(
            datetime.datetime.now().replace(microsecond=0).isoformat()
        ).replace(":", "")

        if self.dataset.stream:
            dest_variables = os.path.join(
                location, APPROVED_VARS_FILENAME_STREAM_TEMPLATE.format(
                    dt=datetime_suffix, stream_id=self.dataset.stream))
            qc_report_fname = QC_REPORT_STREAM_FILENAME.format(
                dt=datetime_suffix, stream_id=self.dataset.stream)
        else:
            dest_variables = os.path.join(
                location,
                APPROVED_VARS_FILENAME_TEMPLATE.format(dt=datetime_suffix))
            qc_report_fname = QC_REPORT_FILENAME.format(dt=datetime_suffix)
        dest_filename = os.path.join(location, qc_report_fname)

        output = {
            "run_id": run_id,
            "aggregated_summary": [],
            "details": [],
        }

        cursor = self.db.cursor()
        if with_details:
            output["details"] = self._get_error_details(
                cursor, run_id, process_all)
        output["aggregated_summary"] = self._get_aggregated_errors(
            cursor, run_id, process_all)
        number_of_errors = len(output["aggregated_summary"])
        if number_of_errors:
            self.logger.critical(
                "{} issues found with the provided dataset,"
                "please check the QC report in {}".format(
                    number_of_errors, dest_filename))
        if self.relaxed_cmor:
            output["relaxed_cmor"] = "Running QC with relaxed CMIP6 validation"
        if not process_all:
            output["ignored_errors"] = self.get_ignored_messages()
        with open(dest_filename, 'w') as outfile:
            json.dump(output, outfile, indent=4, ensure_ascii=False)
        with open(dest_variables, 'w') as outfile:
            for mip_table, var_dir, var_name in get_validated_variables(
                    cursor, run_id).fetchall():
                outfile.write("{}/{};{}\n".format(
                    mip_table, var_name, var_dir))
        return output

    def _get_error_details(self, cursor, run_id, process_all):
        """
        Retrieves and processes error messages

        Parameters
        ----------
        cursor: sqlite3.Cursor
            An active db cursor
        run_id: int
            Run id
        process_all: bool
            Should we ignore some messages

        Returns
        -------
            : list
            List containing error messages and other meta data
        """
        output = []
        qc_runs = get_qc_runs(cursor, run_id)
        for qc_run in qc_runs:
            # one element for each MIP table
            item = {
                "mip_table_filter": qc_run[1],
                "results": [],
                "db_id": qc_run[0]
            }

            # generate reports by MIP table
            qc_files = get_qc_files(cursor, qc_run[0])
            for qc_file in qc_files:
                err_msg = str(qc_file[4].encode('utf-8'))
                if process_all or self._process_errors(err_msg):
                    item["results"].append({
                        "experiment": qc_file[0].split(':')[0],
                        "mip_table": qc_file[1],
                        "variable": qc_file[2],
                        "filename": qc_file[3],
                        "errors": err_msg,
                    })
            output.append(item)
        return output

    def _get_error_summary(self, cursor, run_id):
        """
        Retrieves and processes error summaries

        Parameters
        ----------
        cursor: sqlite3.Cursor
            An active db cursor
        run_id: int
            Run id

        Returns
        -------
            : list
            List containing error statistics
        """
        output = []
        ec_rows = get_error_counts(cursor, run_id).fetchall()
        for r in ec_rows:
            output.append({
                "mip_table": r[0],
                "variable": r[1],
                "filename": r[2],
                "error_count": r[3],
            })
        return output

    def _get_aggregated_errors(self, cursor, run_id, process_all):
        """
        Retrieves and processes aggregated errors

        Parameters
        ----------
        cursor: sqlite3.Cursor
            An active db cursor
        run_id: int
            Run id
        process_all: bool
            Should we ignore some messages

        Returns
        -------
            : list
            List containing aggregated errors
        """

        output = []
        agg_rows = get_aggregated_errors(
            cursor, run_id, process_all).fetchall()
        for r in agg_rows:
            output.append({
                "mip_table": r[0],
                "checker": r[1],
                "error_message": r[2],
                "affected_files": r[3],
                "affected_vars": "|".join(list(set(r[4].split("|")))),
            })
        return output

    def _process_children(self, elem):
        """
        Flattens a message tuple

        Parameters
        ----------
        elem: tuple
            A tuple with QC results

        Returns
        : list
            A flattened list with error messages
        -------
        """

        errors = []
        if type(elem) == str:
            errors.append(elem)
        elif len(elem.children) == 0:
            for msg in elem.msgs:
                errors.append("{}: {}".format(elem.name, msg))
        else:
            for child in elem.children:
                errors += self._process_children(child)
        return errors

    def _parse_and_log(self, cursor, result, qc_dataset_id):
        """
        Parses a result instance returned by the QC checker and saves it
        in the database

        Parameters
        ----------
        cursor: sqlite3.Cursor
            An active db cursor
        result: tuple
            A tuple with QC results
        qc_dataset_id:
            Dataset table identifier

        Returns
        -------
        : boolean
            True if the run was a success, i.e. the checked dataset was
            validated, and there were no other errors raised when running
            QC checks.
        """
        errors = False
        for checker, rpair in list(result.items()):
            for elem in rpair[0]:
                # process if actual score is lower than expected score
                if elem.value[0] < elem.value[1]:
                    msgs = self._process_children(elem)
                    for msg in msgs:
                        if self._process_errors(msg):
                            status = STATUS_ERROR
                        else:
                            status = STATUS_IGNORED
                        execute_insert_query(cursor, "qc_message", {
                            "qc_dataset_id": qc_dataset_id,
                            "message": msg,
                            "status": status,
                            "checker": checker,
                        })
                    errors = True
            # test for exceptions and other errors
            if bool(rpair[1]):
                errors = True
                # not empty
                for elem in rpair[1]:
                    msgs = self._process_children(elem)
                    for msg in msgs:
                        if self._process_errors(msg):
                            status = STATUS_ERROR
                        else:
                            status = STATUS_IGNORED
                        execute_insert_query(cursor, "qc_message", {
                            "qc_dataset_id": qc_dataset_id,
                            "message": msg,
                            "status": status,
                            "checker": checker,
                        })
        self.db.commit()
        return errors

    def _process_errors(self, message):
        """
        An ugly metod evaluate error messages and discard/downgrade those
        we don't really care about
        e.g. things that are too difficult to implement in the qc module

        Parameters
        ----------
        message: str
            QC message to be evaluated
        Returns
        -------
        : bool
            True if the message is to be included in the QC results
        """
        if any([m in message for m in list(self.get_ignored_messages().keys())]):
            # ignore this message
            return False
        return True

    def get_ignored_messages(self):
        """
        A dictionary containing strings of error messages to ignore along with
        the reason

        Returns
        -------
        : dict
            A dictionary with message strings as keys
        """
        msg_dictionary = {
            "2.6.2 Recommended Attributes: references should be defined": (
                "Ignoring this recommendation"),
            "Cell measure variable areacell": (
                "cell measures in CMIP6 are often formatted in"
                " a non-standard way"),
            "cell_measures: Cell measure variable": (
                "cell measures in CMIP6 are often formatted in"
                " a non-standard way"),
            "cell_measures: The cell_measures attribute for variable": (
                "for handling the OR keyword in variables with sea ice mask"),
            "dimensions are not in the recommended order": (
                "Ignoring this recommendation"),
            "7.1 Cell boundaries are valid for variable plev": (
                "ignored for single pressure levels"),
            "7.1 Cell boundaries are valid for variable depth": (
                "ignored for single depth levels"),
            "If there is no standardized information, the keyword comment": (
                "for handling variables with sea ice mask"),
            "9.1 Feature Types are all the same": (
                "applicable only to CF sites"),
            "defines either standard_name or axis": (
                "ignored for eORCA vertices lat/lon"),
            "Either long_name or standard_name is highly recommended": (
                "ignored for some non-compliant variables"),
            "must be a string compatible with UDUNITS": ("ignored for formula terms"),
            "must map to the correct computed_standard_name": ("non-mandatory"),
            "latitude variable 'vertices_latitude' should define standard_name='latitude' or axis='Y'": (
                "non-mandatory"),
            "longitude variable 'vertices_longitude' should define standard_name='longitude' or axis='X'": (
                "non-mandatory"),
            "7.1 Cell Boundaries: Boundary variable": "Ignored because of buggy scalar variable implementation",
            "does not match a dimension, area or auxiliary coordinate": "does not work for collapsed coords, see #2548"
        }
        return msg_dictionary
