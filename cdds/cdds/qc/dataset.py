# (C) British Crown Copyright 2017-2025, Met Office.
# Please see LICENSE.md for license details.

from cdds.qc.plugins.cf1_7.dataset import Cf17Dataset
from cdds.qc.plugins.cmip6.dataset import Cmip6Dataset
from cdds.qc.plugins.cmip7.dataset import Cmip7Dataset
from cdds.qc.plugins.cordex.dataset import CordexDataset


class DatasetFactory:

    DATASET_CLASSES = [Cmip6Dataset, Cmip7Dataset, Cf17Dataset, CordexDataset]

    @classmethod
    def of(cls, mip_era, root, request, mip_tables, mip_table=None, start=None, end=None, logger=None, stream=None):
        for dataset_clazz in DatasetFactory.DATASET_CLASSES:
            if dataset_clazz.is_responsible(mip_era):
                return dataset_clazz(root, request, mip_tables, mip_table, start, end, logger, stream)
        raise KeyError('Found no structured dataset class for project: {}'.format(mip_era))
