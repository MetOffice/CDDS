# (C) British Crown Copyright 2019-2021, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`constants` module contains constants (values that should never
be changes by a user and exist for readability and maintainability
purposes) for CDDS Prepare.
"""
ACTIVATE = 'activate'
ALLOWED_POSITIVE = ['up', 'down', None]
ARCHIVE_LOG_DIRECTORY_PERMISSIONS = 0o777

# Fields in which a change between data request versions is critical
CRITICAL_FIELDS = ['dimensions', 'cell_methods', 'units', 'positive']

CICE_HISTFREQ_FOR_VALIDATION = {'d': 10, 'h': 24}
CICE_VARIABLE_REMAP = {'icepresent': 'ice_present'}
DEACTIVATE = 'deactivate'
DEACTIVATION_RULE_LOCATION = 'https://code.metoffice.gov.uk/svn/cdds/variable_issues/trunk/'
EPILOG = ('For a full description of this script, please refer to the '
          'documentation available via '
          'https://code.metoffice.gov.uk/doc/cdds/cdds_prepare/index.html')
INSERT = 'insert'
FALLBACK_EXPERIMENT_ID = 'piControl'

# 'KNOWN_GOOD_VARIABLES' is a dictionary keyed first by a tuple describing the
# data request versions being used then by the MIP table, with the key being a
# list of variables which are known to be good.  For example, if the
# 'cell_methods' of a particular 'MIP requested variable' has changed,
# but this doesn't change how it is interpreted or produced, an entry
# should be added to approve the 'MIP requested variable' for a given
# version of the data request.
KNOWN_GOOD_VARIABLES = {
    ('01.00.10', '01.00.29'): {
        '6hrLev': ['ec550aer', 'pfull'],
        '6hrPlevPt': ['vortmean'],
        'Amon': ['fco2antt', 'fco2fos', 'fco2nat'],
        'E3hrPt': ['parasolRefl'],
        'Eday': ['hursminCrop', 'mlotst', 't20d'],
        'Emon': ['evspsblpot', 'hus', 'sfcWindmax', 'sweLut', 'thetaot',
                 'thetaot2000', 'thetaot300', 'thetaot700',
                 'gppLut', 'hflsLut', 'hfssLut', 'hussLut', 'laiLut',
                 'nppLut', 'rlusLut', 'rsusLut', 'tasLut', 'tslsiLut',
                 'grassFracC3', 'grassFracC4'],
        'EmonZ': ['sltbasin'],
        'Ofx': ['areacello', 'deptho', 'hfgeou'],
        'Omon': ['bfeos', 'bsios', 'chldiatos', 'chlmiscos', 'dfeos',
                 'hfx', 'hfy', 'hfbasin', 'hfbasinpadv', 'hfbasinpmadv',
                 'hfbasinpmdiff', 'htovgyre', 'htovovrt',
                 'intpcalcite', 'intpoc', 'intppmisc', 'msftyzmpa',
                 'no3os', 'o2os', 'o2satos', 'phynos', 'phypos', 'physios',
                 'ponos', 'popos', 'sios',
                 'sltovgyre', 'sltovovrt'],
        'SIday': ['sispeed', 'sitemptop', 'sithick', 'sitimefrac'],
        'SImon': ['sfdsi', 'siage', 'sicompstren', 'sidconcdyn', 'sidconcth',
                  'sidmassdyn', 'sidmassevapsubl', 'sidmassgrowthbot',
                  'sidmassgrowthwat', 'sidmasslat', 'sidmassmeltbot',
                  'sidmassmelttop', 'sidmasssi', 'sidmassth', 'sidragtop',
                  'sifb', 'siflcondbot', 'siflcondtop', 'siflfwbot',
                  'siflfwdrain', 'sifllatstop', 'sifllwdtop', 'sifllwutop',
                  'siflsenstop', 'siflsensupbot', 'siflswdtop', 'siflswutop',
                  'sihc', 'simass', 'sipr', 'sirdgconc', 'sirdgthick',
                  'sisaltmass', 'sisnconc', 'sisnhc', 'sisnmass', 'sispeed',
                  'sistrxubot', 'sistryubot', 'sitempbot', 'sitemptop',
                  'sithick', 'sitimefrac', 'sivol', 'sndmassdyn',
                  'sndmassmelt', 'sndmasssi', 'sndmasssnf'],
        'fx': ['areacella', 'mrsofc']},
    ('01.00.10', '01.00.31beta'): {
        '6hrLev': ['ec550aer', 'pfull'],
        '6hrPlevPt': ['vortmean'],
        'Amon': ['fco2antt', 'fco2fos', 'fco2nat'],
        'E3hrPt': ['parasolRefl'],
        'Eday': ['hursminCrop', 'mlotst', 't20d'],
        'Emon': ['evspsblpot', 'hus', 'sfcWindmax', 'sweLut',
                 'thetaot', 'thetaot2000', 'thetaot300', 'thetaot700',
                 'vegHeightPasture',
                 'gppLut', 'hflsLut', 'hfssLut', 'hussLut', 'laiLut', 'nppLut',
                 'rlusLut', 'rsusLut', 'tasLut', 'tslsiLut', 'grassFracC3',
                 'grassFracC4'],
        'EmonZ': ['sltbasin'],
        'Ofx': ['areacello', 'deptho', 'hfgeou'],
        'Omon': ['bfeos', 'bsios', 'chldiatos', 'chlmiscos', 'dfeos',
                 'hfx', 'hfy', 'hfbasin', 'hfbasinpadv', 'hfbasinpmadv',
                 'hfbasinpmdiff', 'htovgyre', 'htovovrt',
                 'intpcalcite', 'intpoc', 'intppmisc', 'masscello',
                 'msftyzmpa',
                 'no3os', 'o2os', 'o2satos', 'phynos', 'phypos', 'physios',
                 'ponos', 'popos', 'sios', 'sltovgyre', 'sltovovrt', 'wmo'],
        'SIday': ['sispeed', 'sitemptop', 'sithick', 'sitimefrac'],
        'SImon': ['sfdsi', 'siage', 'sicompstren', 'sidconcdyn', 'sidconcth',
                  'sidmassdyn', 'sidmassevapsubl', 'sidmassgrowthbot',
                  'sidmassgrowthwat', 'sidmasslat', 'sidmassmeltbot',
                  'sidmassmelttop', 'sidmasssi', 'sidmassth', 'sidragtop',
                  'sifb', 'siflcondbot', 'siflcondtop', 'siflfwbot',
                  'siflfwdrain', 'sifllatstop', 'sifllwdtop', 'sifllwutop',
                  'siflsenstop', 'siflsensupbot', 'siflswdtop', 'siflswutop',
                  'sihc', 'simass', 'sipr', 'sirdgconc', 'sirdgthick',
                  'sisaltmass', 'sisnconc', 'sisnhc', 'sisnmass', 'sispeed',
                  'sistrxubot', 'sistryubot', 'sitempbot', 'sitemptop',
                  'sithick', 'sitimefrac', 'sivol', 'sndmassdyn',
                  'sndmassmelt', 'sndmasssi', 'sndmasssnf'],
        'fx': ['areacella', 'mrsofc']},
    ('01.00.10', '01.00.32'): {
        '6hrLev': ['ec550aer', 'pfull'],
        '6hrPlevPt': ['vortmean'],
        'Amon': ['fco2antt', 'fco2fos', 'fco2nat'],
        'E3hrPt': ['parasolRefl'],
        'Eday': ['hursminCrop', 'mlotst', 't20d'],
        'Emon': ['evspsblpot', 'hus', 'sfcWindmax', 'sweLut',
                 'thetaot', 'thetaot2000', 'thetaot300', 'thetaot700',
                 'vegHeightPasture',
                 'gppLut', 'hflsLut', 'hfssLut', 'hussLut', 'laiLut', 'nppLut',
                 'rlusLut', 'rsusLut', 'tasLut', 'tslsiLut', 'grassFracC3',
                 'grassFracC4'],
        'EmonZ': ['sltbasin'],
        'Ofx': ['areacello', 'deptho', 'hfgeou'],
        'Omon': ['bfeos', 'bsios', 'chldiatos', 'chlmiscos', 'dfeos',
                 'hfx', 'hfy', 'hfbasin', 'hfbasinpadv', 'hfbasinpmadv',
                 'hfbasinpmdiff', 'htovgyre', 'htovovrt',
                 'intpcalcite', 'intpoc', 'intppmisc', 'masscello',
                 'msftyzmpa',
                 'no3os', 'o2os', 'o2satos', 'phynos', 'phypos', 'physios',
                 'ponos', 'popos', 'sios', 'sltovgyre', 'sltovovrt', 'wmo'],
        'SIday': ['sispeed', 'sitemptop', 'sithick', 'sitimefrac'],
        'SImon': ['sfdsi', 'siage', 'sicompstren', 'sidconcdyn', 'sidconcth',
                  'sidmassdyn', 'sidmassevapsubl', 'sidmassgrowthbot',
                  'sidmassgrowthwat', 'sidmasslat', 'sidmassmeltbot',
                  'sidmassmelttop', 'sidmasssi', 'sidmassth', 'sidragtop',
                  'sifb', 'siflcondbot', 'siflcondtop', 'siflfwbot',
                  'siflfwdrain', 'sifllatstop', 'sifllwdtop', 'sifllwutop',
                  'siflsenstop', 'siflsensupbot', 'siflswdtop', 'siflswutop',
                  'sihc', 'simass', 'sipr', 'sirdgconc', 'sirdgthick',
                  'sisaltmass', 'sisnconc', 'sisnhc', 'sisnmass', 'sispeed',
                  'sistrxubot', 'sistryubot', 'sitempbot', 'sitemptop',
                  'sithick', 'sitimefrac', 'sivol', 'sndmassdyn',
                  'sndmassmelt', 'sndmasssi', 'sndmasssnf'],
        'fx': ['areacella', 'mrsofc']},
    ('01.00.17', '01.00.29'): {
        '6hrLev': ['pfull'],
        'Amon': ['fco2antt', 'fco2fos', 'fco2nat'],
        'E3hrPt': ['parasolRefl'],
        'Eday': ['hursminCrop', 'mlotst', 't20d'],
        'Emon': ['sweLut', 'thetaot', 'thetaot2000', 'thetaot300',
                 'thetaot700', 'vegHeight', 'gppLut', 'hflsLut', 'hfssLut',
                 'hussLut', 'laiLut', 'nppLut', 'rlusLut', 'rsusLut', 'tasLut',
                 'tslsiLut', 'grassFracC3', 'grassFracC4'],
        'EmonZ': ['sltbasin'],
        'Ofx': ['deptho', 'hfgeou'],
        'Omon': ['bfeos', 'bsios', 'chldiatos', 'chlmiscos', 'dfeos',
                 'intdic', 'intpbfe', 'intpbsi', 'intpbn', 'intpbp',
                 'intpp', 'intppdiat',
                 'hfbasin', 'hfbasinpadv', 'hfbasinpmadv', 'hfbasinpmdiff',
                 'htovgyre', 'htovovrt', 'intpcalcite', 'intpoc', 'intppmisc',
                 'msftyzmpa',
                 'no3os', 'o2os', 'o2satos', 'phynos', 'phypos', 'physios',
                 'ponos', 'popos', 'sios',
                 'sltovgyre', 'sltovovrt'],
        'SIday': ['sispeed', 'sitemptop', 'sithick', 'sitimefrac'],
        'SImon': ['sfdsi', 'siage', 'sicompstren', 'sidconcdyn', 'sidconcth',
                  'sidmassdyn', 'sidmassevapsubl', 'sidmassgrowthbot',
                  'sidmassgrowthwat', 'sidmasslat', 'sidmassmeltbot',
                  'sidmassmelttop', 'sidmasssi', 'sidmassth', 'sidragtop',
                  'sifb', 'siflcondbot', 'siflcondtop', 'siflfwbot',
                  'siflfwdrain', 'sifllatstop', 'sifllwdtop', 'sifllwutop',
                  'siflsenstop', 'siflsensupbot', 'siflswdtop', 'siflswutop',
                  'sihc', 'simass', 'sipr', 'sirdgconc', 'sirdgthick',
                  'sisaltmass', 'sisnconc', 'sisnhc', 'sisnmass', 'sispeed',
                  'sistrxubot', 'sistryubot', 'sitempbot', 'sitemptop',
                  'sithick', 'sitimefrac', 'sivol', 'sndmassdyn',
                  'sndmassmelt', 'sndmasssi', 'sndmasssnf']},
    ('01.00.17', '01.00.31beta'): {
        '6hrLev': ['pfull'],
        'Amon': ['fco2antt', 'fco2fos', 'fco2nat'],
        'E3hrPt': ['parasolRefl'],
        'Eday': ['hursminCrop', 'mlotst', 't20d'],
        'Emon': ['sweLut', 'thetaot', 'thetaot2000', 'thetaot300',
                 'thetaot700', 'vegHeight', 'vegHeightPasture',
                 'gppLut', 'hflsLut', 'hfssLut', 'hussLut', 'laiLut', 'nppLut',
                 'rlusLut', 'rsusLut', 'tasLut', 'tslsiLut', 'grassFracC3',
                 'grassFracC4'],
        'EmonZ': ['sltbasin'],
        'LImon': ['sftgif'],
        'Ofx': ['deptho', 'hfgeou'],
        'Omon': ['bfeos', 'bsios', 'chldiatos', 'chlmiscos', 'dfeos',
                 'intdic', 'intpbfe', 'intpbsi', 'intpp', 'intpbn', 'intpbp',
                 'intppdiat',
                 'hfbasin', 'hfbasinpadv', 'hfbasinpmadv', 'hfbasinpmdiff',
                 'htovgyre', 'htovovrt', 'intpcalcite', 'intpoc', 'intppmisc',
                 'masscello', 'msftyzmpa',
                 'no3os', 'o2os', 'o2satos', 'phynos', 'phypos', 'physios',
                 'ponos', 'popos', 'sios',
                 'sltovgyre', 'sltovovrt', 'wmo'],
        'SIday': ['sispeed', 'sitemptop', 'sithick', 'sitimefrac'],
        'SImon': ['sfdsi', 'siage', 'sicompstren', 'sidconcdyn', 'sidconcth',
                  'sidmassdyn', 'sidmassevapsubl', 'sidmassgrowthbot',
                  'sidmassgrowthwat', 'sidmasslat', 'sidmassmeltbot',
                  'sidmassmelttop', 'sidmasssi', 'sidmassth', 'sidragtop',
                  'sifb', 'siflcondbot', 'siflcondtop', 'siflfwbot',
                  'siflfwdrain', 'sifllatstop', 'sifllwdtop', 'sifllwutop',
                  'siflsenstop', 'siflsensupbot', 'siflswdtop', 'siflswutop',
                  'sihc', 'simass', 'sipr', 'sirdgconc', 'sirdgthick',
                  'sisaltmass', 'sisnconc', 'sisnhc', 'sisnmass', 'sispeed',
                  'sistrxubot', 'sistryubot', 'sitempbot', 'sitemptop',
                  'sithick', 'sitimefrac', 'sivol', 'sndmassdyn',
                  'sndmassmelt', 'sndmasssi', 'sndmasssnf']},
    ('01.00.17', '01.00.32'): {
        '6hrLev': ['pfull'],
        'Amon': ['fco2antt', 'fco2fos', 'fco2nat'],
        'E3hrPt': ['parasolRefl'],
        'Eday': ['hursminCrop', 'mlotst', 't20d'],
        'Emon': ['sweLut', 'thetaot', 'thetaot2000', 'thetaot300',
                 'thetaot700', 'vegHeight', 'vegHeightPasture',
                 'gppLut', 'hflsLut', 'hfssLut', 'hussLut', 'laiLut', 'nppLut',
                 'rlusLut', 'rsusLut', 'tasLut', 'tslsiLut', 'grassFracC3',
                 'grassFracC4'],
        'EmonZ': ['sltbasin'],
        'Ofx': ['deptho', 'hfgeou'],
        'Omon': ['bfeos', 'bsios', 'chldiatos', 'chlmiscos', 'dfeos',
                 'intdic', 'intpbfe', 'intpbsi', 'intpp', 'intpbn', 'intpbp',
                 'intppdiat',
                 'hfbasin', 'hfbasinpadv', 'hfbasinpmadv', 'hfbasinpmdiff',
                 'htovgyre', 'htovovrt', 'intpcalcite', 'intpoc', 'intppmisc',
                 'masscello', 'msftyzmpa',
                 'no3os', 'o2os', 'o2satos', 'phynos', 'phypos', 'physios',
                 'ponos', 'popos', 'sios',
                 'sltovgyre', 'sltovovrt', 'wmo'],
        'SIday': ['sispeed', 'sitemptop', 'sithick', 'sitimefrac'],
        'SImon': ['sfdsi', 'siage', 'sicompstren', 'sidconcdyn', 'sidconcth',
                  'sidmassdyn', 'sidmassevapsubl', 'sidmassgrowthbot',
                  'sidmassgrowthwat', 'sidmasslat', 'sidmassmeltbot',
                  'sidmassmelttop', 'sidmasssi', 'sidmassth', 'sidragtop',
                  'sifb', 'siflcondbot', 'siflcondtop', 'siflfwbot',
                  'siflfwdrain', 'sifllatstop', 'sifllwdtop', 'sifllwutop',
                  'siflsenstop', 'siflsensupbot', 'siflswdtop', 'siflswutop',
                  'sihc', 'simass', 'sipr', 'sirdgconc', 'sirdgthick',
                  'sisaltmass', 'sisnconc', 'sisnhc', 'sisnmass', 'sispeed',
                  'sistrxubot', 'sistryubot', 'sitempbot', 'sitemptop',
                  'sithick', 'sitimefrac', 'sivol', 'sndmassdyn',
                  'sndmassmelt', 'sndmasssi', 'sndmasssnf']},
}
MIP_TABLES_DIR = '/home/h03/cdds/etc/mip_tables/CMIP6/01.00.29'
MODEL_TYPE_MAP = {'atmos': ('AGCM', 'AOGCM'),
                  'ocean': ('AOGCM', 'OGCM')}
OBGC_MODEL_STRING = 'BGC'

# The following relates the NEMO and CICE output streams to a string used to
# identify the frequency of a particular variable. For CICE this is the flag
# in the namelist, while for NEMO it is the id attribute within a file_group
# object inside the iodef.xml file.
OCEAN_STREAMS = {'inm': 'd', 'ind': 'h', 'ond': '1d', 'onm': '1m'}
PRIORITY_UNSET = 99

# Log messages that variable is / is not in inventory:
VARIABLE_IN_INVENTORY_LOG = 'Variable "{}/{}" is in the inventory database settings active: "{}".'
VARIABLE_NOT_IN_INVENTORY_LOG = 'Variable "{}/{}" can not be found in the inventory database.'

# Comments of approved variable that in inventory
VARIABLE_IN_INVENTORY_COMMENT = 'Data set "{}" version "{}" found in inventory with status "{}"'
