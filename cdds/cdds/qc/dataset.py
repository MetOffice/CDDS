# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.

from cdds.qc.plugins.cmip6.dataset import Cmip6Dataset
from cdds.qc.plugins.cf17.dataset import Cf17Dataset
from cdds.qc.plugins.cordex.dataset import CordexDataset


class DatasetFactory:

    DATASET_CLASSES = [Cmip6Dataset, Cf17Dataset, CordexDataset]

    @classmethod
    def of(cls, mip_era, root, request, mip_tables, mip_table=None, start=None, end=None, logger=None, stream=None):
        for dataset_clazz in DatasetFactory.DATASET_CLASSES:
            if dataset_clazz.is_responsible(mip_era):
                return dataset_clazz(root, request, mip_tables, mip_table, start, end, logger, stream)
        raise KeyError('Found no structured dataset class for project: {}'.format(mip_era))
