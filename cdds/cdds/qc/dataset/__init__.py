# (C) British Crown Copyright 2017-2026, Met Office.
# Please see LICENSE.md for license details.

from cdds.qc.dataset.cmip6 import Cmip6Dataset
from cdds.qc.dataset.cmip7 import Cmip7Dataset
from cdds.qc.dataset.cordex import CordexDataset


class DatasetFactory:

    DATASET_CLASSES = [Cmip6Dataset, Cmip7Dataset, CordexDataset]

    @classmethod
    def of(cls, mip_era, root, request, mip_tables, mip_table=None, start=None, end=None, logger=None, stream=None):
        for structured_dataset_class in DatasetFactory.DATASET_CLASSES:
            if structured_dataset_class.is_responsible(mip_era):
                return structured_dataset_class(root, request, mip_tables, mip_table, start, end, logger, stream)
        raise KeyError('Found no StructuredDataset Class responsible for project: {}'.format(mip_era))
