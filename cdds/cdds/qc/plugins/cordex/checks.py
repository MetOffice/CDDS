# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.
from cdds.qc.plugins.base.checks import CheckTask
from cdds.qc.plugins.base.validators import BaseValidatorFactory


class CordexAttributesCheckTask(CheckTask):
    DRIVING_SOURCE_REGEX = r"^([a-zA-Z\d\-_\.\s]+) \(\d{4}\)"

    def __init__(self, check_cache):
        super(CordexAttributesCheckTask, self).__init__(check_cache)

    def execute(self, netcdf_file, attr_dict):
        validator = self._cache.cv_validator
        cordex_dict = {
            "driving_experiment_id": validator.experiment_validator(getattr(netcdf_file, "driving_experiment_id")),
            "driving_institution_id": validator.institution_validator(getattr(netcdf_file, "driving_institution_id")),
            "driving_source_id": BaseValidatorFactory.string_validator(self.DRIVING_SOURCE_REGEX),
            "driving_variant_label": BaseValidatorFactory.value_in_validator([
                "r{}i{}p{}f{}".format(
                    attr_dict["realization_index"],
                    attr_dict["initialization_index"],
                    attr_dict["physics_index"],
                    attr_dict["forcing_index"]),
            ])
        }
        for k, v in cordex_dict.items():
            self._exists_and_valid(netcdf_file, k, v)
