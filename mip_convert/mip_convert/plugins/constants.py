# (C) British Crown Copyright 2016-2025, Met Office.
# Please see LICENSE.md for license details.
"""The :mod:`constants` module contains the constants available for use
in the |model to MIP mapping| expressions.
"""


REQUIRED_MAPPING_OPTIONS = ['dimension', 'expression', 'mip_table_id', 'positive', 'status', 'units']


def all_constants():
    """Return the names and values of the constants available for use in
    the |model to MIP mapping| expressions.

    Since the values of the constants are used to replace the names of
    the constants in the |model to MIP mapping| expressions, the values
    are stored as strings.

    Returns
    -------
    dict
        The names and values of the constants available for use in the
        |model to MIP mapping| expressions.
    """
    return dict(list(constants().items()) + list(pressure_levels().items()))


def constants():
    return {
        # Constants:
        'ACCELERATION_DUE_TO_EARTH_GRAVITY': '9.80665',  # m s-2 (Value taken from the UM)
        'ATOMIC_MASS_OF_C': '12.',  # g mol-1
        'C_TO_N_RATIO': '6.625',  # mol C (mol N)-1 (Molar C to N ratio of phytoplankton in marine bgc model)
        'C_TO_N_RATIO_ZOO': '5.625',  # mol C (mol N)-1 (Molar C to N ratio of zooplankton in marine bgc model)
        'CONV_C_ORGM': '1.4',  # C/ Organic matter ratio
        'DAYS_IN_YEAR': '360.',  # day year-1
        'FE_TO_N_RATIO': '3.00E-05',  # mol Fe (mol N)-1 (Molar Fe to N ratio in marine bgc model)
        'FRESHWATER_DENSITY': '1000.',  # kg m-3
        'ICE_DENSITY': '917.',  # kg m-3
        'LATENT_HEAT_OF_FREEZING': '334000.',  # J kg-1
        'MOLECULAR_MASS_OF_AIR': '28.97',  # g mol-1
        'MOLECULAR_MASS_OF_BRCL': '115.5',  # g mol-1
        'MOLECULAR_MASS_OF_BRO': '96.',  # g mol-1
        'MOLECULAR_MASS_OF_BROMINE': '80.',  # g mol-1
        'MOLECULAR_MASS_OF_BRONO2': '142.',  # g mol-1
        'MOLECULAR_MASS_OF_CH3COCH3': '58.',  # g mol-1
        'MOLECULAR_MASS_OF_CH4': '16.',  # g mol-1
        'MOLECULAR_MASS_OF_CHLORINE': '35.5',  # g mol-1
        'MOLECULAR_MASS_OF_CLOX': '51.5',  # g mol-1 (X avoids confusion with CLONO2)
        'MOLECULAR_MASS_OF_CL2O2': '103.',  # g mol-1
        'MOLECULAR_MASS_OF_CLONO2': '97.5',  # g mol-1
        'MOLECULAR_MASS_OF_CO': '28.',  # g mol-1
        'MOLECULAR_MASS_OF_CO2': '44.01',  # g mol-1
        'MOLECULAR_MASS_OF_C2H6': '30.',  # g mol-1
        'MOLECULAR_MASS_OF_C3H8': '44.',  # g mol-1
        'MOLECULAR_MASS_OF_CFC11': '137.5',  # g mol-1 (CFCl3)
        'MOLECULAR_MASS_OF_CFC12': '121.',  # g mol-1 (CF2Cl2)
        'MOLECULAR_MASS_OF_DMS': '62.1',  # g mol-1 (dimethyl sulfide, C2H6S)
        'MOLECULAR_MASS_OF_HBR': '81.',  # g mol-1
        'MOLECULAR_MASS_OF_HOBR': '97.',  # g mol-1
        'MOLECULAR_MASS_OF_HCHO': '30.',  # g mol-1
        'MOLECULAR_MASS_OF_HCL': '36.5',  # g mol-1
        'MOLECULAR_MASS_OF_HNO3': '63.',  # g mol-1
        'MOLECULAR_MASS_OF_HO2': '33.',  # g mol-1
        'MOLECULAR_MASS_OF_HO2NO2': '79.',  # g mol-1
        'MOLECULAR_MASS_OF_HOCL': '52.5',  # g mol-1
        'MOLECULAR_MASS_OF_HONO': '47.',  # g mol-1
        'MOLECULAR_MASS_OF_H2SO4': '98.',  # g mol-1
        'MOLECULAR_MASS_OF_ISOPRENE': '68.',  # g mol-1 (C5H8)
        'MOLECULAR_MASS_OF_ME2CO': '58.',  # g mol-1 (ACETONE)
        'MOLECULAR_MASS_OF_MECHO': '44.',  # g mol-1
        'MOLECULAR_MASS_OF_MEOH': '32.',  # g mol-1
        'MOLECULAR_MASS_OF_MONOTERPENE': '136.24',  # g mol-1 (C10H16)
        'MOLECULAR_MASS_OF_MEONO2': '77.',  # g mol-1
        'MOLECULAR_MASS_OF_NITROGEN': '14.',  # g mol-1
        'MOLECULAR_MASS_OF_NACL': '58.44',  # g mol-1
        'MOLECULAR_MASS_OF_NO': '30.',  # g mol-1
        'MOLECULAR_MASS_OF_NO2': '46.',  # g mol-1
        'MOLECULAR_MASS_OF_NO3': '62.',  # g mol-1
        'MOLECULAR_MASS_OF_N2O': '44.',  # g mol-1
        'MOLECULAR_MASS_OF_N2O5': '108.',  # g mol-1
        'MOLECULAR_MASS_OF_OCLO': '67.5',  # g mol-1
        'MOLECULAR_MASS_OF_OH': '17.',  # g mol-1
        'MOLECULAR_MASS_OF_O3': '48.',  # g mol-1
        'MOLECULAR_MASS_OF_PAN': '121.',  # g mol-1 (peroxyacetyl nitrate, C2H3NO5)
        'MOLECULAR_MASS_OF_SO2': '64.',  # g mol-1
        'MOLECULAR_MASS_OF_SO4': '96.',  # g mol-1
        'P_TO_N_RATIO': '0.0625',  # mol P (mol N)-1 (Molar P to N ratio in marine bgc model)
        'REF_SALINITY': '8.',
        'SEAWATER_DENSITY': '1026.',  # kg m-3
        'SECONDS_IN_DAY': '86400.',  # s day-1
        'SECONDS_IN_HOUR': '3600.',  # s hour-1
        'SNOW_DENSITY': '330.',  # kg m-3
        'SPECIFIC_GAS_CONSTANT_DRY_AIR': '287.058',  # J K-1 kg-1
        'SPECIFIC_HEAT_OF_DRY_AIR': '1005.',  # J K-1 kg-1
    }


def pressure_levels():
    return {
        # Pressure levels, taken from version 01.00.15 of the data
        # request (http://clipc-services.ceda.ac.uk/dreq/index.html)
        # are stored here in units of 'hPa' for consistency with the
        # units in the 'model output files':
        'P10': '10.0',
        'P100': '100.0',
        'P200': '200.0',
        'P220': '220.0',
        'P500': '500.0',
        'P560': '560.0',
        'P700': '700.0',
        'P750': '750.0',
        'P840': '840.0',
        'P850': '850.0',
        'P925': '925.0',
        'P1000': '1000.0',
        'PL700': '700.0',
        'PLEV3': '850.0 500.0 250.0',
        'PLEV3h': '100.0 10.0 1.0',
        'PLEV4': '925.0 850.0 500.0 250.0',
        'PLEV7C': '900.0 740.0 620.0 500.0 375.0 245.0 90.0',
        'PLEV7H': '925.0 850.0 700.0 600.0 500.0 250.0 50.0',
        'PLEV8': '1000.0 850.0 700.0 500.0 250.0 100.0 50.0 10.0',
        'PLEV10': '1000.0 850.0 700.0 500.0 250.0 150.0 100.0 70.0 50.0 10.0',
        'PLEV17': ('1000.0 925.0 850.0 700.0 600.0 500.0 400.0 300.0 250.0 '
                   '200.0 150.0 100.0 70.0 50.0 30.0 20.0 10.0'),
        'PLEV19': ('1000.0 925.0 850.0 700.0 600.0 500.0 400.0 300.0 250.0 '
                   '200.0 150.0 100.0 70.0 50.0 30.0 20.0 10.0 5.0 1.0'),
        'PLEV23': ('1000.0 925.0 850.0 700.0 600.0 500.0 400.0 300.0 250.0 '
                   '200.0 150.0 100.0 70.0 50.0 30.0 20.0 10.0 7.0 5.0 3.0 '
                   '2.0 1.0 0.4'),
        'PLEV27': ('1000.0 975.0 950.0 925.0 900.0 875.0 850.0 825.0 800.0 '
                   '775.0 750.0 700.0 650.0 600.0 550.0 500.0 450.0 400.0 '
                   '350.0 300.0 250.0 225.0 200.0 175.0 150.0 125.0 100.0'),
        'PLEV39': ('1000.0 925.0 850.0 700.0 600.0 500.0 400.0 300.0 250.0 '
                   '200.0 170.0 150.0 130.0 115.0 100.0 90.0 80.0 70.0 50.0 '
                   '30.0 20.0 15.0 10.0 7.0 5.0 3.0 2.0 1.5 1.0 0.7 0.5 0.4 '
                   '0.3 0.2 0.15 0.10 0.07 0.05 0.03'),
        # Extras for UKCP
        'P20': '20.0',
        'P30': '30.0',
        'P50': '50.0',
        'P70': '70.0',
        'P150': '150.0',
        'P250': '250.0',
        'P300': '300.0',
        'P400': '400.0',
        'P600': '600.0',
    }
