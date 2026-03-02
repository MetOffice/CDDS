# (C) British Crown Copyright 2026, Met Office.
# Please see LICENSE.md for license details.
import os
from pathlib import Path

import pytest
from metomi.isodatetime.data import TimePoint

from cdds.common.request.attributes_section import GlobalAttributesSection
from cdds.common.request.common_section import CommonSection
from cdds.common.request.conversion_section import ConversionSection
from cdds.common.request.data_section import DataSection
from cdds.common.request.inventory_section import InventorySection
from cdds.common.request.metadata_section import MetadataSection
from cdds.common.request.misc_section import MiscSection
from cdds.common.request.request import Request


@pytest.fixture
def cmip7_request(tmp_path: Path):
    variable_list_file = tmp_path / "variable_list.txt"
    variable_list_file.write_text("Amon/tas:ap5")

    root_proc_dir = Path(tmp_path, "proc")
    root_data_dir = Path(tmp_path, "data")

    cdds_etc_dir = os.environ['CDDS_ETC']

    conversion_section = ConversionSection()
    inventory_section = InventorySection()
    misc_section = MiscSection()
    data_section = DataSection(
        data_version='v20240212',
        end_date=TimePoint(year=2015, month_of_year=1, day_of_month=1),
        mass_data_class='crum',
        start_date=TimePoint(year=1979, month_of_year=1, day_of_month=1),
        max_file_size=20e9,
        model_workflow_id='u-bp880',
        streams=['ap5'],
        variable_list_file=str(variable_list_file)
    )
    common_section = CommonSection(
        mip_table_dir=os.path.join(cdds_etc_dir, "mip_tables", "CMIP7", "DR-1.2.2.2-v1.0.1"),
        mode='strict',
        package='round-1',
        workflow_basename='UKESM1-3-LL_amip_r1i1p1f4',
        root_proc_dir=str(root_proc_dir),
        root_data_dir=str(root_data_dir),
        root_ancil_dir=os.path.join(cdds_etc_dir, 'ancil'),
        root_hybrid_heights_dir=os.path.join(cdds_etc_dir, 'vertical_coordinates'),
        root_replacement_coordinates_dir=os.path.join(cdds_etc_dir, 'horizontal_coordinates'),
        sites_file=os.path.join(cdds_etc_dir, 'cfmip2/cfmip2-sites-orog.txt'),
        standard_names_version='latest',
        standard_names_dir=os.path.join(cdds_etc_dir, 'standard_names')
    )
    metadata_section = MetadataSection(
        branch_method='no parent',
        base_date=TimePoint(year=1850, month_of_year=1, day_of_month=1),
        calendar='gregorian',
        experiment_id='amip',
        institution_id='MOHC',
        license=('CC BY 4.0'),
        mip='CMIP',
        mip_era='CMIP7',
        variant_label='r1i1p1f1',
        model_id='UKESM1-3-LL',
        model_type=['AGCM', 'AER', 'CHEM']
    )

    return Request(common=common_section,
                   data=data_section,
                   metadata=metadata_section,
                   misc=misc_section,
                   inventory=inventory_section,
                   conversion=conversion_section,
                   netcdf_global_attributes=GlobalAttributesSection())
