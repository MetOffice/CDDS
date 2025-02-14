# (C) British Crown Copyright 2019-2025, Met Office.
# Please see LICENSE.md for license details.
"""
The :mod:`mass` module interact with the MASS archiving system.
"""
import logging
import subprocess
import re

from cdds.common.mass_exception import (MassError, DirAlreadyExistMassError, FileNotExistMassError,
                                        VariableArchivingError, MassFailure)
from cdds.common.mass_record import get_records_from_stdout


def mass_list_dir(mass_path, simulation):
    """
    List the contents of a directory in the MASS archive.

    Parameters
    ----------
    mass_path: str
        The location in mass to list the contents of.
    simulation: bool
        If true, do not execute MASS commands, but output the command that
        would be run to the log.

    Returns
    -------
    : list
        A list of strings with mass locations for archived files.
    """
    logger = logging.getLogger(__name__)
    moo_cmd = ['moo', 'ls', mass_path]
    if simulation:
        logger.info('simulating mass command: {cmd}'
                    ''.format(cmd=' '.join(moo_cmd)))
        return []
    try:
        stdout_str = run_mass_command(moo_cmd)
        logger.debug('moo ls output:\n{0}'.format(stdout_str))
    except subprocess.CalledProcessError:
        stdout_str = ''
        logger.critical('Error getting listing of a directory in MASS.')
    except RuntimeError as e:
        logger.critical(str(e))
        raise e
    mass_paths = [s1 for s1 in stdout_str.split('\n') if s1]
    return mass_paths


def mass_test(mass_path, simulation):
    """
    Returns if a directory or set exists with given MASS path.

    Parameters
    ----------
    mass_path: str
        The location in mass to check.
    simulation: bool
        If true, do not execute MASS commands, but output the command that
        would be run to the log.

    Returns
    -------
    : bool
        True if directory/set with given MASS path exists else False.
    """
    logger = logging.getLogger(__name__)
    moo_cmd = ['moo', 'test', mass_path]
    if simulation:
        logger.info('Simulating mass command: {}'.format(' '.join(moo_cmd)))
        return True

    try:
        stdout = run_mass_command(moo_cmd)
        logger.debug('{} output:\n{}'.format(' '.join(moo_cmd), stdout))
    except subprocess.CalledProcessError as e:
        logger.critical('Error testing if MASS location exists.')
    except RuntimeError as e:
        logger.critical(str(e))
        raise e
    return 'true' in stdout.lower()


def mass_rm_empty_dirs(mass_root_path, search_mass_paths=None, simulation=False):
    """
    Remove all empty directories recursively containing at the given
    MASS location.

    Parameters
    ----------
    mass_root_path: str
        The location in MASS containing all directories that should
        check for emptiness.
    search_mass_paths: list (optional)
        The location of the MASS directories containing in the MASS root path that
        should be check for emptiness. If None, all paths will be checked.
    simulation: bool (optional)
        If true, do not execute MASS commands, but output the command that
        would be run to the log.

    Returns
    -------
    : list
        The list of MASS records that have been removed.
    """
    logger = logging.getLogger(__name__)
    empty_dirs = mass_list_empty_dirs(mass_root_path, search_mass_paths, simulation)
    empty_dirs.sort(key=len, reverse=True)

    if empty_dirs is None or empty_dirs == []:
        logger.info('No empty directories found. Nothing to delete.')
    else:
        logger.info('Deleting following empty directories: {}'.format(', '.join(empty_dirs)))

    for mass_dir in empty_dirs:
        mass_rmdir(mass_dir, simulation)
        logger.debug('Deleted empty directory: {}'.format(mass_dir))
    return empty_dirs


def mass_list_empty_dirs(mass_path, search_mass_paths=None, simulation=False):
    """
    Lists all empty directories recursively containing at the given
    MASS location and that paths are matching at least one of the
    given MASS searched paths.

    Parameters
    ----------
    mass_path: str
        The location in MASS containing all directories that should
        check for emptiness.
    search_mass_paths: list (optional)
        The location of the MASS directories containing in the given MASS path
        that should be check for emptiness. If None, all paths will be checked.
    simulation: bool (optional)
        If true, do not execute MASS commands, but output the command that
        would be run to the log.

    Returns
    -------
    : list
        The list of MASS records of the empty directories.
    """
    logger = logging.getLogger(__name__)
    moo_cmd = ['moo', 'ls', '-Rl', mass_path]
    if simulation:
        logger.info('Simulating mass command: {}'.format(' '.join(moo_cmd)))
        return []

    try:
        stdout = run_mass_command(moo_cmd)
        logger.debug('{} output:\n{}'.format(' '.join(moo_cmd), stdout))
    except FileNotExistMassError:
        stdout = ''
    except subprocess.CalledProcessError:
        stdout = ''
        logger.critical('Error getting listing of a directory in MASS.')
    except RuntimeError as e:
        logger.critical(str(e))
        raise e

    record_map = get_records_from_stdout(stdout, search_mass_paths)
    empty_dirs = {k: v for k, v in record_map.items() if v.is_dir and v.is_empty}
    return list(empty_dirs.keys())


def mass_list_records(mass_path, simulation=False):
    """
    Lists the contents of a directory in the MASS and creates for each content a corresponding
    MassRecord. These records will be returned in a dictionary according their path to the
    corresponding content in MASS.

    :param mass_path: The location in MASS to list the contents of
    :type mass_path: str
    :param simulation: If true, do not execute MASS commands, but output the command that
                       would be run to the log. (Default: False)
    :type simulation: bool
    :return: Dictionary of mass records where keys are the record paths and values
             the corresponding MassRecord.
    :rtype: dict
    """
    logger = logging.getLogger(__name__)
    moo_cmd = ['moo', 'ls', '-Rl', mass_path]
    if simulation:
        logger.info('Simulating mass command: {}'.format(' '.join(moo_cmd)))
        return []

    try:
        stdout = run_mass_command(moo_cmd)
        logger.debug('{} output:\n{}'.format(' '.join(moo_cmd), stdout))
    except FileNotExistMassError:
        logger.debug('The MASS URI "{}" does not exist.'.format(mass_path))
        stdout = ''
    except subprocess.CalledProcessError:
        stdout = ''
        logger.critical('Error getting listing of a directory in MASS.')
    except RuntimeError as e:
        logger.critical(str(e))
        raise e

    record_map = get_records_from_stdout(stdout)
    return record_map


def mass_list_files_recursively(mass_path, simulation):
    """
    List the contents of a directory in the MASS archive.

    Parameters
    ----------
    mass_path: str
        The location in mass to list the contents of.
    simulation: bool
        If true, do not execute MASS commands, but output the command that
        would be run to the log.

    Returns
    -------
    : list
        A list of strings with mass locations for archived files.
    """
    logger = logging.getLogger(__name__)
    moo_cmd = ['moo', 'ls', '-Rl', mass_path]
    if simulation:
        logger.info('simulating mass command: {cmd}'
                    ''.format(cmd=' '.join(moo_cmd)))
        return []
    try:
        stdout_str = run_mass_command(moo_cmd)
    except subprocess.CalledProcessError:
        stdout_str = ''
        logger.critical('Error getting listing of a directory in MASS.')
    except RuntimeError as e:
        logger.critical(str(e))
        raise e
    mass_paths = [s1 for s1 in stdout_str.split('\n') if s1]
    datasets = {}
    for m in mass_paths:
        if m[0] == 'F':
            elems = [s1 for s1 in m.split()]
            (mip, institution, model, experiment, variant, mip_table, variable, grid, status,
             timestamp, filename) = elems[8].split('/')[6:]
            if filename.endswith('.nc'):
                dataset_id = '{}.{}.{}.{}.{}.{}.{}.{}.{}'.format(
                    'CMIP6', mip, institution, model, experiment, variant, mip_table, variable, grid)
                if dataset_id not in datasets:
                    datasets[dataset_id] = {
                        'status': status,
                        'timestamp': timestamp,
                        'files': []
                    }
                datasets[dataset_id]['files'].append({
                    'filesize': elems[4],
                    'filename': filename,
                    'mass_path': elems[8]
                })
    return datasets


def mass_isdir(mass_path, simulation):
    """
    Check whether the specified directory currently exists in MASS.

    Parameters
    ----------
    mass_path: str
        The location in mass to check for the presence of a directory.
    simulation: bool
        If true, do not execute MASS commands, but output the command that
        would be run to the log.

    Returns
    -------
    : bool
        Return whether specified directory exists in MASS.

    Raises
    ------
    VariableArchivingEror
        Raised if there is an error executing any of the mass commands.

    """
    logger = logging.getLogger(__name__)
    moo_cmd = ['moo', 'test', '-d', mass_path]
    if simulation:
        logger.info('simulating mass command: {cmd}'
                    ''.format(cmd=' '.join(moo_cmd)))
        return False
    try:
        stdout_str = run_mass_command(moo_cmd)
    except subprocess.CalledProcessError:
        stdout_str = ''
        logger.critical('Error checking for existence of a directory in MASS.')
    except RuntimeError as e:
        logger.critical(str(e))
        raise e
    is_dir = 'true' in stdout_str
    return is_dir


def mass_mkdir(mass_path, simulation, create_parents, exist_ok=False):
    """
    Create a directory in MASS at the specified location.

    Parameters
    ----------
    mass_path: str
        The location in mass to create a directory.
    simulation: bool
        If true, do not execute MASS commands, but output the command that
        would be run to the log.
    create_parents: bool
        If true, create any parent directories required.
    exist_ok: bool
        If true, do not raise an error if trying to create an already existing
        directory in MASS. (Default: False)

    Returns
    -------
    : bool
        Return whether specified directory exists in MASS.

    Raises
    ------
    VariableArchivingEror
        Raised if there is an error executing any of the mass commands.

    DirAlreadyExistMassError
        Raised if try to create an already existing directory and the
        exit_ok flag is set to False.
    """
    logger = logging.getLogger(__name__)
    moo_cmd = ['moo', 'mkdir']
    if create_parents:
        moo_cmd += ['-p']
    moo_cmd += [mass_path]
    if simulation:
        logger.info('simulating mass command: {cmd}'
                    ''.format(cmd=' '.join(moo_cmd)))
        return

    try:
        stdout_str = run_mass_command(moo_cmd)
        logger.debug('creating directory in mass {0}'.format(mass_path))
        logger.debug('moo mkdir output:\n{0}'.format(stdout_str))
    except DirAlreadyExistMassError as error:
        if not exist_ok:
            logger.critical(error.msg)
            raise error
    except subprocess.CalledProcessError:
        logger.critical('error creating directory in MASS {0}'
                        ''.format(mass_path))
        raise VariableArchivingError()
    except RuntimeError as e:
        logger.critical(str(e))
        raise VariableArchivingError()


def mass_put(input_files, mass_path, simulation, check_mass_location):
    """
    Add each of the specified files to the archive at the given location.

    Parameters
    ----------
    input_files: list
        A list of string representing file paths for the
        |output netCDF files| to be archived.
    mass_path: str
        The location to archive the files to.
    simulation: bool
        If true, do not execute MASS commands, but output the command that
        would be run to the log.
    check_mass_location: bool
        If true, check whether the location in the archive exists, and
        create a directory there if  it does not, before archiving the files.

    Returns
    -------
    None

    Raises
    ------
    VariableArchivingEror
        Raised if there is an error executing any of the mass commands.
    """
    logger = logging.getLogger(__name__)
    if check_mass_location:
        mass_mkdir(mass_path, create_parents=True, simulation=simulation, exist_ok=True)
    moo_cmd = ['moo', 'put'] + input_files + [mass_path]
    if simulation:
        logger.info('simulating mass command: {cmd}'
                    ''.format(cmd=' '.join(moo_cmd)))
        return
    try:
        logger.debug('putting files in mass.\ninput:\n{0}\ndest:{1}'
                     ''.format('\n'.join(input_files),
                               mass_path))
        stdout_str = run_mass_command(moo_cmd)
        logger.debug('moo put output:\n{0}'.format(stdout_str))
    except subprocess.CalledProcessError:
        logger.critical('error putting files in MASS {0}'
                        ''.format(mass_path))
        raise VariableArchivingError()
    except RuntimeError as e:
        logger.critical(str(e))
        raise VariableArchivingError()


def mass_move(src_mass_files, dest_mass_path, simulation, check_mass_location):
    """
    Add each of the specified files to the archive at the given location.

    Parameters
    ----------
    src_mass_files: list
        A list of string representing locations in the archive from
        which to move files.
    mass_path: str
        The location in the archive to move the files to.
    simulation: bool
        If true, do not execute MASS commands, but output the command that
        would be run to the log.
    check_mass_location: bool
        If true, check whether the location in the archive exists, and
        create a directory there if  it does not, before archiving the files.

    Returns
    -------
    None

    Raises
    ------
    VariableArchivingEror
        Raised if there is an error executing any of the mass commands.
    """
    logger = logging.getLogger(__name__)
    if check_mass_location:
        mass_mkdir(dest_mass_path, create_parents=True, simulation=simulation, exist_ok=True)
    moo_cmd = ['moo', 'mv'] + src_mass_files + [dest_mass_path]
    if simulation:
        logger.info('simulating mass command: {cmd}'
                    ''.format(cmd=' '.join(moo_cmd)))
        return
    try:
        logger.debug('moving files in mass.\ninput:\n{0}dest:{1}'
                     ''.format('\n'.join(src_mass_files),
                               dest_mass_path))
        stdout_str = run_mass_command(moo_cmd)
        logger.debug('moo mv output:\n{0}'.format(stdout_str))
    except subprocess.CalledProcessError:
        logger.critical('error moving files in MASS {0}'
                        ''.format(src_mass_files))
        raise VariableArchivingError()
    except RuntimeError as e:
        logger.critical(str(e))
        raise VariableArchivingError()


def mass_rmdir(mass_dir, simulation):
    logger = logging.getLogger(__name__)
    moo_cmd = ['moo', 'rmdir', mass_dir]
    if simulation:
        logger.info('simulating mass command: {cmd}'
                    ''.format(cmd=moo_cmd))
        return
    try:
        logger.debug('deleting directory in mass: {dir}'
                     ''.format(dir=mass_dir))
        stdout_str = run_mass_command(moo_cmd)
        logger.debug('moo rmdir output:\n{0}'.format(stdout_str))
    except subprocess.CalledProcessError:
        logger.critical('error deleting directory in MASS {0}'
                        ''.format(mass_dir))
        raise VariableArchivingError()
    except RuntimeError as e:
        logger.critical(str(e))
        raise VariableArchivingError()


def mass_available(simulation):
    """
    Returns True if it successfully runs an si command.

    Note: there is no "is moo available" command, but "moo si" is the closest in intent.
    Although a successful "si" means that MASS is up, it doesn't mean that MASS is
    accepting commands of every type. MASS can be accepting "si" but not "get" commands,
    for example.

    Parameters
    ----------
    simulation: bool
        If true, do not execute MASS commands, but output the command that
        would be run to the log.

    Returns
    -------
    : bool
        Return whether MASS is available or not.
    """
    logger = logging.getLogger(__name__)
    moo_cmd = ['moo', 'si']
    if simulation:
        logger.info('Simulating mass command: {}'.format(' '.join(moo_cmd)))
        return True

    available = True
    try:
        logger.debug('Check if MASS is available')
        run_mass_command(moo_cmd)
    except subprocess.CalledProcessError as e:
        logger.critical('Problem to run MASS command {}: {}'.format(' '.join(moo_cmd), str(e)))
        available = False
    except RuntimeError as e:
        logger.critical('MASS is not available: {}'.format(str(e)))
        available = False
    return available


def mass_info(simulation):
    """
    Returns if MASS is available and which commands can be processed and which not.

    Parameters
    ----------
    simulation: bool
        If true, do not execute MASS commands, but output the command that
        would be run to the log.

    Returns
    -------
    : bool, dict
        Return whether MASS is available and can except commands of specific
        types or not.
        And returns a dictionary contains all commands and if they can be processed
        or not. (key: name of command, value: True if processable else False)
    """
    logger = logging.getLogger(__name__)
    moo_cmd = ['moo', 'si', '-l']

    if simulation:
        logger.info('Simulating mass command: {}'.format(' '.join(moo_cmd)))
        return True, {}

    if not mass_available(simulation):
        return False, {}

    processable = False
    cmds = {}
    try:
        logger.debug('Check if MASS can process commands')
        stdout = run_mass_command(moo_cmd)
        processable = True
    except subprocess.CalledProcessError as e:
        stdout = ''
        logger.critical('Problem to run MASS command {}: {}'.format(' '.join(moo_cmd), str(e)))
    except RuntimeError as e:
        logger.critical('MASS is not available: {}'.format(str(e)))
        raise e

    cmd_pattern = '([A-Z]*) commands enabled: ([A-Za-z]*)'
    for line in stdout.split('\n'):
        match = re.search(cmd_pattern, line)
        if match is not None:
            cmds[match.group(1)] = match.group(2).lower() == 'true'

    return processable, cmds


def run_mass_command(command):
    """
    Run the command in a new process using :class:`subprocess.Popen`.

    Parameters
    ----------
    command: list of strings
        The command to run.

    Returns
    -------
    : str
        The standard output from the command.
    """
    logger = logging.getLogger(__name__)
    process = subprocess.Popen(command,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               universal_newlines=True)
    (stdout, stderr) = process.communicate()
    return_code = process.returncode

    if return_code == 2 and 'TSSC_FILE_DOES_NOT_EXIST' in stderr:
        not_exist_error = MassFailure.NOT_EXIST_ERROR
        logger.debug(not_exist_error.get_message(command, stdout, stderr))
        raise FileNotExistMassError(command)
    elif return_code == 2:
        user_error = MassFailure.USER_ERROR
        logger.critical(user_error.get_message(command, stdout, stderr))
        raise MassError(user_error, command)
    elif return_code == 3:
        system_error = MassFailure.SYSTEM_ERROR
        logger.critical(system_error.get_message(command, stdout, stderr))
        raise MassError(system_error, command)
    elif return_code == 4:
        client_error = MassFailure.CLIENT_ERROR
        logger.critical(client_error.get_message(command, stdout, stderr))
        raise MassError(client_error, command)
    elif return_code == 5:
        access_error = MassFailure.ACCESS_ERROR
        logger.critical(access_error.get_message(command, stdout, stderr))
        raise MassError(access_error, command)
    elif return_code == 10:
        access_error = MassFailure.DIR_ALREADY_EXIST_ERROR
        logger.debug(access_error.get_message(command, stdout, stderr))
        raise DirAlreadyExistMassError(command)
    elif return_code != 0:
        command_str = ' '.join(command)
        msg = 'Problem running command "{}" (return code: {}): {}'.format(command_str, return_code, stderr)
        raise RuntimeError(msg)

    return stdout
