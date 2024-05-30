# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.

ARISE_LICENSE = ('ARISE data produced by MOHC is licensed under the Open Government License v3 '
                 '(https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/)')

CMIP6_LICENSE = ('CMIP6 model data produced by MOHC is licensed '
                 'under a Creative Commons Attribution ShareAlike '
                 '4.0 International License '
                 '(https://creativecommons.org/licenses). Consult '
                 'https://pcmdi.llnl.gov/CMIP6/TermsOfUse for '
                 'terms of use governing CMIP6 output, including '
                 'citation requirements and proper acknowledgment. '
                 'Further information about this data, including '
                 'some limitations, can be found via the '
                 'further_info_url (recorded as a global attribute '
                 'in this file) . The data producers and data '
                 'providers make no warranty, either express or '
                 'implied, including, but not limited to, '
                 'warranties of merchantability and fitness for a '
                 'particular purpose. All liabilities arising from '
                 'the supply of the information (including any '
                 'liability arising in negligence) are excluded to '
                 'the fullest extent permitted by law.')

CORDEX_LICENSE = ('Creative Commons Attribution 4.0 International License '
                  '(CC BY 4.0; https://creativecommons.org/licenses/by/4.0/).')

GCMODELDEV_LICENSE = ('GCModelDev model data is licensed under the Open Government License v3 '
                      '(https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/)')

DEBUG = True

COMPARE_NETCDF = (
    'nccmp -dmgfbi {tolerance} {history} {options} --globalex=cmor_version,creation_date,cv_version,'
    'data_specs_version,table_info,tracking_id,_NCProperties {output} {reference}'
)

COMPARE_NETCDF_META = (
    'nccmp -mgfbi --Attribute=history --globalex=cmor_version,creation_date,cv_version,'
    'data_specs_version,table_info,tracking_id,_NCProperties {output} {reference}'
)
