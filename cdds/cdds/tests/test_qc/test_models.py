# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.

import unittest
import cdds.qc.models as qc_models
from cdds.common.sqlite import execute_insert_query


class DatabaseTestCase(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.db = qc_models.setup_db(":memory:")
        self.cursor = self.db.cursor()

        execute_insert_query(self.cursor, "qc_run", {
            "basepath": "foo",
            "run_id": 5,
            "mip_table": "Amon"
        })
        self.db.commit()
        qc_run_id = self.cursor.lastrowid

        # dataset1, AERmon/ua/r1i1p1f1, 2 error messages
        qc_dataset_id = self._insert_dataset(
            qc_run_id,
            "dataset1.nc",
            "/foo/bar",
            "AERmon",
            "r1i1p1f1",
            "ua"
        )

        execute_insert_query(self.cursor, "qc_message", {
            "qc_dataset_id": qc_dataset_id,
            "message": "message 1",
            "status": qc_models.STATUS_ERROR,
            "checker": "bar",
        })

        execute_insert_query(self.cursor, "qc_message", {
            "qc_dataset_id": qc_dataset_id,
            "message": "message 2",
            "status": qc_models.STATUS_ERROR,
            "checker": "bar",
        })

        # dataset2, AERmon/ua/r2i1p1f1, 2 error messages
        qc_dataset_id = self._insert_dataset(
            qc_run_id,
            "dataset2.nc",
            "/foo/bar",
            "AERmon",
            "r2i1p1f1",
            "ua"
        )

        execute_insert_query(self.cursor, "qc_message", {
            "qc_dataset_id": qc_dataset_id,
            "message": "message 1",
            "status": qc_models.STATUS_ERROR,
            "checker": "bar",
        })

        execute_insert_query(self.cursor, "qc_message", {
            "qc_dataset_id": qc_dataset_id,
            "message": "message 2",
            "status": qc_models.STATUS_ERROR,
            "checker": "bar",
        })

        self.db.commit()

        # dataset3, AERmon / p1 / r1i1p1f1, 1 ignored message
        qc_dataset_id = self._insert_dataset(
            qc_run_id,
            "dataset3.nc",
            "/foo/bar",
            "AERmon",
            "r1i1p1f1",
            "pr"
        )

        execute_insert_query(self.cursor, "qc_message", {
            "qc_dataset_id": qc_dataset_id,
            "message": "ignored message 1",
            "status": qc_models.STATUS_IGNORED,
            "checker": "bar",
        })

        # dataset4, AERmon / p1 / r1i1p1f1, 1 error and 1 ignored message
        qc_dataset_id = self._insert_dataset(
            qc_run_id,
            "dataset4.nc",
            "/foo/bar",
            "Amon",
            "r1i1p1f1",
            "pr"
        )

        execute_insert_query(self.cursor, "qc_message", {
            "qc_dataset_id": qc_dataset_id,
            "message": "ignored message 2",
            "status": qc_models.STATUS_IGNORED,
            "checker": "bar",
        })

        execute_insert_query(self.cursor, "qc_message", {
            "qc_dataset_id": qc_dataset_id,
            "message": "error message 1",
            "status": qc_models.STATUS_ERROR,
            "checker": "bar",
        })

        # dataset3, AERmon / p1 / r1i1p1f1, no errors
        self._insert_dataset(
            qc_run_id,
            "dataset5.nc",
            "/foo/bar",
            "Amon",
            "r1i1p1f1",
            "tas"
        )

    def test_database_setup(self):
        rows = qc_models.get_qc_runs(self.cursor, 5).fetchall()
        self.assertEqual(1, len(rows))

    def test_retrieving_datasets(self):
        rows = qc_models.get_qc_files(self.cursor, 1).fetchall()
        self.assertEqual(5, len(rows))

    def test_error_counts(self):
        rows = qc_models.get_error_counts(self.cursor, 5).fetchall()
        self.assertEqual(3, len(rows))

    def test_variable_aggregation(self):
        rows = qc_models.get_errors_by_variable(self.cursor, 5).fetchall()
        self.assertEqual(3, len(rows))

    def test_validated_variables(self):
        rows = qc_models.get_validated_variables(self.cursor, 5).fetchall()
        self.assertEqual(2, len(rows))
        reference = ["AERmon/pr;/foo/bar", "Amon/tas;/foo/bar"]
        for mip_table, directory, validated_variable in rows:
            self.assertIn("{}/{};{}".format(
                mip_table, validated_variable, directory
            ), reference)

    def test_validated_variables_with_ignored_messages(self):
        rows = qc_models.get_validated_variables(
            self.cursor, 5, True).fetchall()
        self.assertEqual(1, len(rows))
        reference = ["Amon/tas;/foo/bar"]
        for mip_table, directory, validated_variable in rows:
            self.assertIn("{}/{};{}".format(
                mip_table, validated_variable, directory
            ), reference)

    def _insert_dataset(self, qc_run_id, filename, directory,
                        mip_table, variant, variable):
        execute_insert_query(self.cursor, "qc_dataset", {
            "qc_run_id": qc_run_id,
            "filename": filename,
            "variable_directory": directory,
            "summary": qc_models.SUMMARY_STARTED,
            "realization_index": (
                "CMIP6_HadGEM3-GC31-LL_abrupt-4xCO2_none_{}_{}_{}_gn".format(
                    mip_table, variant, variable)),
            "model": "HadGEM3-GC31-LL",
            "experiment": "abrupt-4xCO2 : none",
            "mip_table": mip_table,
            "variant": variant,
            "variable": variable,
            "variable_name": variable,
            "grid": "gn",
        })
        self.db.commit()
        return self.cursor.lastrowid


if __name__ == "__main__":
    unittest.main()
