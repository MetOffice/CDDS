# function that iterates over env vars in turn and prints them. If any arent set  or paths dont exist it should be flagged provides 1 exit code if it fails
#put wrapper into bin

import os
import pytest
from cdds import _DEV

# jasmin:
# CYLC_VERSION : 8
# LC_ALL : en_GB.UTF-8
# TZ : UTC
# CDDS_PLATFORM : JASMIN
# CDDS_ETC : $HOME/etc
# CDDS_ENV_COMMAND : $HOME/software/miniforge3/bin/activate $HOME/conda_environments/cdds-X.Y.Z

# metoffice = {
# "CYLC_VERSION" : "8",
# "LC_ALL" : en_GB.UTF-8 < doesnt exist?????,
# "TZ" : "UTC",
# "CDDS_PLATFORM" : "AZURE",
# "CDDS_ETC" : "$HOME/etc", <this needs to check the location resolves with os.exists_expand_vars
# "CDDS_ENV_COMMAND" : "conda activate $HOME/conda_environments/cdds-3.2.0", 
# }
# os.environ['CDDS_ENV_COMMAND']

# only needs to check all are set, not specific values

def check_environment_variables():
    """
    Check if all required environment variables are set and valid.
    """
    required_vars = [
        'CDDS_PLATFORM',
        'CDDS_ETC',
        'CDDS_ENV_COMMAND',
        'CYLC_VERSION',
        'TZ'
    ]
    #create a set^

    for var in required_vars:
        value = os.getenv(var)
        if not value:
            raise EnvironmentError(f"Required environment variable '{var}' is not set.")
        
        # Check if the path exists if it's a path variable
        if 'CDDS_ETC' in var or 'CDDS_ENV_COMMAND' in var:
            expanded_value = os.path.expandvars(value)
            if not os.path.exists(expanded_value):
                raise EnvironmentError(f"Path '{expanded_value}' for '{var}' does not exist.")

def test_environment_variable():
    # Set an environment variable for testing
    breakpoint()    
    os.environ['TEST_ENV_VAR'] = 'test_value'
    
    # Check if the environment variable is set correctly
    assert os.getenv('TEST_ENV_VAR') == 'test_value'
    
    # Clean up by removing the environment variable
    del os.environ['TEST_ENV_VAR']