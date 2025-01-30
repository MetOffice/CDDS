# (C) British Crown Copyright 2024-2025, Met Office.
# Please see LICENSE.rst for license details.
import os
import tempfile

from metomi.isodatetime.data import TimePoint

from cdds.common.request.common_section import CommonSection
from cdds.common.request.metadata_section import MetadataSection
from cdds.common.request.data_section import DataSection
from cdds.common.request.attributes_section import GlobalAttributesSection
from cdds.common.request.misc_section import MiscSection
from cdds.common.request.conversion_section import ConversionSection
from cdds.common.request.inventory_section import InventorySection
from cdds.common.request.request import Request


def simple_request():
    variable_list_file = tempfile.mktemp()
    with open(variable_list_file, 'w') as fh:
        fh.writelines(['Amon/tas:ap5'])

    root_proc_dir = tempfile.mkdtemp(prefix='proc')
    root_data_dir = tempfile.mkdtemp(prefix='data')

    cdds_etc_dir = os.environ['CDDS_ETC']

    conversion_section = ConversionSection()
    inventory_section = InventorySection(inventory_check=False)
    misc_section = MiscSection()
    data_section = DataSection(
        data_version='v20240212',
        end_date=TimePoint(year=2015, month_of_year=1, day_of_month=1),
        mass_data_class='crum',
        start_date=TimePoint(year=1979, month_of_year=1, day_of_month=1),
        max_file_size=20e9,
        model_workflow_id='u-bp880',
        model_workflow_branch='cdds',
        model_workflow_revision='HEAD',
        streams=['ap4', 'ap5', 'ap6'],
        output_mass_root='',
        output_mass_suffix='',
        variable_list_file=variable_list_file
    )
    common_section = CommonSection(
        mip_table_dir=os.path.join(cdds_etc_dir, 'mip_tables/CMIP6/01.00.29/'),
        mode='strict',
        package='amip_ll',
        workflow_basename='UKESM1-0-LL_amip_r1i1p1f4',
        root_proc_dir=root_proc_dir,
        root_data_dir=root_data_dir,
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
        calendar='360_day',
        experiment_id='amip',
        institution_id='MOHC',
        license=('CMIP6 model data produced by MOHC is licensed under a Creative Commons Attribution '
                 'ShareAlike 4.0 International License (https://creativecommons.org/licenses). Consult '
                 'https://pcmdi.llnl.gov/CMIP6/TermsOfUse for terms of use governing CMIP6 output, '
                 'including citation requirements and proper acknowledgment. Further information about '
                 'this data, including some limitations, can be found via the further_info_url (recorded '
                 'as a global attribute in this file) . The data producers and data providers make no '
                 'warranty, either express or implied, including, but not limited to, warranties of '
                 'merchantability and fitness for a particular purpose. All liabilities arising from '
                 'the supply of the information (including any liability arising in negligence) are '
                 'excluded to the fullest extent permitted by law.'),
        mip='CMIP',
        mip_era='CMIP6',
        sub_experiment_id='none',
        variant_label='r1i1p1f4',
        model_id='UKESM1-0-LL',
        model_type=['AGCM', 'AER', 'CHEM']
    )

    return Request(common=common_section,
                   data=data_section,
                   metadata=metadata_section,
                   misc=misc_section,
                   inventory=inventory_section,
                   conversion=conversion_section,
                   netcdf_global_attributes=GlobalAttributesSection())
