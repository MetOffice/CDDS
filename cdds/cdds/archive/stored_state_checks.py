# (C) British Crown Copyright 2019-2021, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`stored_state_checks` module contains the code to check what the
current state of already stored data is.
"""
import os

from cdds.common.plugins.plugins import PluginStore

from cdds.archive.constants import DATA_PUBLICATION_STATUS_DICT


def check_state_already_published(var_dict):
    """
    Use the files to archive and files already archived to
    checker if this archiving operation is attempting to
    publish files for an already published and currently
    avauilable dataset.

    Parameters
    ----------
    var_dict: dict
        A dictionary containing all the  information specific to
        this |MIP output variable| required to archive the relevant
        |output netCDF files|.

    Returns
    -------
    : str
        The type of archiving operation required.
    """
    stored_data = var_dict['stored_data']
    try:
        published_data = stored_data['AVAILABLE']
    except KeyError:
        return None
    if not published_data:
        return None

    # calculate time range of data
    model_file_info = PluginStore.instance().get_plugin().model_file_info()
    file_list = [os.path.split(f1)[-1]
                 for dt, dt_list in list(published_data.items())
                 for f1 in dt_list
                 ]
    start_dt, end_dt = model_file_info.get_date_range(file_list, var_dict['frequency'])
    input_date_range = var_dict['date_range']

    # the only valid date range when there is data in the available state is
    # to be appending data, so we only need to check that the start date of
    # the new data is the same as the end date of the previously published
    # data, and that the end date of the new data is after that. No other
    # range of dates is an acceptable, and will result in a critical error for
    # this variable.
    if input_date_range[0] == end_dt and input_date_range[1] > end_dt:
        # if checks pass, then this is an append operation, which
        # will be handled by another filter.
        return None
    if input_date_range[1] == start_dt and input_date_range[0] < start_dt:
        # if checks pass, then this is a prepend operation, which
        # will be handled by another filter.
        return None
    return 'ALREADY_PUBLISHED'


def check_state_extending_embargoed(var_dict):
    """
    Use the files to archive and files already archived to
    checker whether appending/prepending to embargoed data
    is required.

    Parameters
    ----------
    var_dict: dict
        A dictionary containing all the  information specific to
        this |MIP output variable| required to archive the relevant
        |output netCDF files|.

    Returns
    -------
    : str
        The type of archiving operation required.
    """
    stored_data = var_dict['stored_data']
    try:
        unpublished_data = stored_data['EMBARGOED']
    except KeyError:
        return None
    if not unpublished_data:
        return None

    return _calculate_extending_state(var_dict, unpublished_data)


def check_state_extending_published(var_dict):
    """
    Use the files to archive and files already archived to
    checker whether appending/prepending to published data
    is required.

    Parameters
    ----------
    var_dict: dict
        A dictionary containing all the  information specific to
        this |MIP output variable| required to archive the relevant
        |output netCDF files|.

    Returns
    -------
    : str
        The type of archiving operation required.
    """
    stored_data = var_dict['stored_data']
    try:
        published_data = stored_data['AVAILABLE']
    except KeyError:
        return None
    if not published_data:
        return None

    return _calculate_extending_state(var_dict, published_data)


def _calculate_extending_state(var_dict, archived_data):
    model_file_info = PluginStore.instance().get_plugin().model_file_info()
    file_list = [os.path.split(file_name)[-1]
                 for date, file_list in list(archived_data.items())
                 for file_name in file_list
                 ]
    start_date, end_date = model_file_info.get_date_range(file_list, var_dict['frequency'])
    new_start_date, new_end_date = var_dict['date_range']

    # To be appending, the start date of the new data must be the same as
    # the end date of the previously published data, and the end date of
    # the new data must be after that date.
    if new_start_date == end_date and new_end_date > end_date:
        # if checks pass, then this is an append operation, which
        # will be handled by another filter.
        return 'APPENDING'
    if new_end_date == start_date and new_start_date < start_date:
        return 'PREPENDING'
    return None


def check_state_recovery_continuation(var_dict):
    """
    Use the files to archive and files already archived to
    checker whether this archiving operation is continuing from
    a previous unfinished archiving operation.

    Parameters
    ----------
    var_dict: dict
        A dictionary containing all the  information specific to
        this |MIP output variable| required to archive the relevant
        |output netCDF files|.

    Returns
    -------
    : str
        The type of archiving operation required.
    """
    stored_data = var_dict['stored_data']
    try:
        unpublished_data = stored_data['EMBARGOED']
    except KeyError:
        return None
    if not unpublished_data:
        return None

    # calculate time range of data
    model_file_info = PluginStore.instance().get_plugin().model_file_info()
    file_list = [os.path.split(f1)[-1]
                 for dt, dt_list in list(unpublished_data.items())
                 for f1 in dt_list
                 ]
    if not file_list:
        return None
    start_dt, end_dt = model_file_info.get_date_range(file_list, var_dict['frequency'])
    new_data_start, new_data_end = var_dict['date_range']

    # for this to be a match to recovery mode, the data already in mass must
    # be a subset of the data to be published.
    if new_data_start <= start_dt and new_data_end >= end_dt:
        return 'PROCESSING_CONTINUATION'

    return None


def check_state_withdrawn(var_dict):
    """
    Use the files to archive and files already archived to
    checker whether the data being archived is replacing
    a version that was previously withdrawn.

    Parameters
    ----------
    var_dict: dict
        A dictionary containing all the  information specific to
        this |MIP output variable| required to archive the relevant
        |output netCDF files|.

    Returns
    -------
    : str
        The type of archiving operation required.
    """
    status_key = 'PREVIOUSLY_WITHDRAWN'
    stored_data = var_dict['stored_data']
    if 'WITHDRAWN' not in list(stored_data.keys()):
        return None
    withdrawn_data = stored_data['WITHDRAWN']
    file_list = [os.path.split(f1)[-1]
                 for dt, dt_list in list(withdrawn_data.items())
                 for f1 in dt_list
                 ]
    if not file_list:
        return None

    return status_key


def check_state_previously_published_datestamp(var_dict):
    """
    Use the files to archive and files already archived to
    checker whether this archiving operation is trying to
    published data using a previously published datestamp
    version.

    Parameters
    ----------
    var_dict: dict
        A dictionary containing all the  information specific to
        this |MIP output variable| required to archive the relevant
        |output netCDF files|.

    Returns
    -------
    : str
        The type of archiving operation required.
    """
    datestamp = var_dict['new_datestamp']
    stored_data = var_dict['stored_data']
    status_key = 'DATESTAMP_REUSE'
    published_states = list(DATA_PUBLICATION_STATUS_DICT.keys())
    published_states.remove('EMBARGOED')
    for state in published_states:
        try:
            if datestamp in list(stored_data[state].keys()):
                return status_key
        except KeyError:
            pass
    return None


def check_state_first_publication(var_dict):
    """
    If stored_data dictionary is empty, this is the first publication.

    Parameters
    ----------
    var_dict: dict
        A dictionary containing all the relevant info about this variable
        for processing.

    Returns
    -------
    : str
        If this is first publication, the string FIRST_PUBLICATION will be
        returned. If not, None will be returned.
    """
    if not var_dict['stored_data']:
        return 'FIRST_PUBLICATION'
    stored_data = var_dict['stored_data']
    file_list = [os.path.split(f1)[-1]
                 for status, status_data in list(stored_data.items())
                 for dt, dt_list in list(status_data.items())
                 for f1 in dt_list
                 ]
    if not file_list:
        return 'FIRST_PUBLICATION'
    return None


def check_state_multiple_embargoed(var_dict):
    """
    Check if there is already a datestamp in embargoed, different to the
    datestamp being published.

    Parameters
    ----------
    var_dict: dict
        A dictionary containing all the relevant info about this variable
        for processing.

    Returns
    -------
    : str
        If there is already data with a different datestamp in the embargoed
        state, the string FIRST_PUBLICATION will be
        returned. If not, None will be returned.
    """
    try:
        stored_data = var_dict['stored_data']
        embargoed_data = stored_data['EMBARGOED']
    except KeyError:
        return None
    if len(embargoed_data) > 1:
        return 'MULTIPLE_EMBARGOED'
    if len(embargoed_data) == 1:
        if var_dict['new_datestamp'] not in list(embargoed_data.keys()):
            return 'MULTIPLE_EMBARGOED'
    return None


def get_stored_state_checkers():
    """
    Get the list of functions to apply to the dsata for each
    |MIP output variable| dictionary to check what archiving
    operation is required based on the files to archive and
    the current files already archived.

    Returns
    -------
    : list
        A list of functions to check the stored data state.
    """
    # The order of these checkers is important
    # Make sure they are listed in the order that checks should be run
    # Checks for error states should be listed first, followed by valid
    # states
    mass_state_checkers = [
        # error state checks
        check_state_previously_published_datestamp,
        check_state_already_published,
        check_state_multiple_embargoed,
        # valid state checks
        check_state_extending_published,
        check_state_extending_embargoed,
        check_state_recovery_continuation,
        check_state_withdrawn,
        check_state_first_publication,
    ]
    return mass_state_checkers


def get_stored_state(var_dict):
    """
    Get the archiving operation required for this |MIP output variable| based
    on the state of already stored data.

    Parameters
    ----------
    var_dict: dict
        A dictionary containing all the relevant info about this variable
        for processing.

    Returns
    -------
    : str
        The state of the stored data for this variable and the type of
        archiving operation required.
    """
    checkers = get_stored_state_checkers()
    for checker in checkers:
        new_state = checker(var_dict)
        if new_state:
            return new_state

    # If we get to this state,  none of the status checkers were a match
    # so we have an error of unknown type for this variable.
    # If the state of stored seems valid, then you may need to add or edit
    # a checker to capture that particular valid which is not currently being
    # handled
    new_state = 'UNKNOWN'
    return new_state
