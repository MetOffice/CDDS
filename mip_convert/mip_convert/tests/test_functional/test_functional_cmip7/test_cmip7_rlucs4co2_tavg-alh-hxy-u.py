# (C) British Crown Copyright 2022-2026, Met Office.
# Please see LICENSE.md for license details.
import os

import pytest

from mip_convert.tests.test_functional.test_command_line import AbstractFunctionalTests
from mip_convert.tests.test_functional.utils.configurations import Cmip7TestData, SpecificInfo
from mip_convert.tests.test_functional.utils.directories import (get_cmor_log, get_output_dir,
                                                                 MODEL_OUTPUT_DIR,
                                                                 ROOT_OUTPUT_CASES_DIR,
                                                                 ROOT_ANCIL_TESTING_DIR)


class TestCmip7_rlucs4co2_tavg_alh_hxy_u(AbstractFunctionalTests):

    def get_test_data(self):
        test_location = os.path.join(ROOT_OUTPUT_CASES_DIR, 'test_CMIP7_atmos_rlucs4co2_tavg-alh-hxy-u')
        return Cmip7TestData(
            mip_table="atmos",
            variables=["rlucs4co2_tavg-alh-hxy-u"],
            specific_info=SpecificInfo(
                common={"test_location": test_location},
                cmor_setup={"cmor_log_file": get_cmor_log(test_location)},
                cmor_dataset={
                    "output_dir": get_output_dir(test_location),
                    "branch_date_in_child": "1850-01-01T00:00:00",
                    "branch_date_in_parent": "3384-01-01T00:00:00",
                    "variant_label": "r1i1p1f1",
                    "experiment_id": "esm-piControl",
                    "parent_experiment_id": "esm-piControl-spinup",
                },
                request={
                    "ancil_files": " ".join(
                        [
                            os.path.join(ROOT_ANCIL_TESTING_DIR, "UKESM1-3-LL", "qrparm.orog.pp"),
                            os.path.join(ROOT_ANCIL_TESTING_DIR, "UKESM1-3-LL", "qrparm.landfrac.pp"),
                        ]
                    ),
                    "model_output_dir": MODEL_OUTPUT_DIR,
                    "mip_convert_plugin": "UKESM1p3",
                    "run_bounds": "1900-01-01T00:00:00 1900-03-01T00:00:00",
                    "suite_id": "u-dw498",
                },
                global_attributes={
                    "further_info_url": "https://furtherinfo.es-doc.org/CMIP7.MOHC.UKESM1-3-LL.esm-piControl.none.r1i1p1f1",
                    "table_id": "atmos"
                },
                streams={"ap5": {"CMIP7_atmos@mon": "rlucs4co2_tavg-alh-hxy-u"}},
                other={
                    "reference_version": "v2",
                    "filenames": [
                        "rlucs4co2_tavg-alh-hxy-u_mon_glb_g100_UKESM1-3-LL_esm-piControl_r1i1p1f1_190001-190002.nc"
                    ],
                    "ignore_history": True,
                },
            ),
        )

    @pytest.mark.slow
    def test_cmip7_mon_rlucs4co2(self):
        self.maxDiff = True
        self.check_convert(plugin_id="CMIP7")
