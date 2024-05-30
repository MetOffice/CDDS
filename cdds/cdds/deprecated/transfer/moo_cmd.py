# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
import logging

from cdds.deprecated.transfer import moo

"""Simple wrappers to run some MOOSE commands. All methods will raise
either moo.MassError or moo.RetryableMassError exception if their
command fails.

Public methods:
    dir_exists -- return True if directory exists in MASs
    get -- run moo get with force overwrite and non-default transfer
        threads
    ls -- run moo ls to list directories by name
    ls_tree -- run a recursive moo listing that will fit in memory
    mkdir -- run moo mkdir, creating parent dirs as necessary
    mv -- run a moo mv to rename files/directories
    put -- run moo put with no options
    put_safe_overwrite -- run moo put with the -F (safe overwrite)
        option
    rmdir -- run moo rmdir to delete an empty directory
"""

LS_ONLY = 'LS_ONLY'


def mkdir(moose_dir, simulation=False):
    """Create the specified MASS directory, creating parent
    directories as necessary.

    Arguments:
    moose_dir -- (str) path to directory to be created.
    simulation -- (bool) if true simulate moo command.
    """
    moo.run_moo_cmd("mkdir", ["-p", moose_dir], simulation=simulation)
    return


def rmdir(moose_dir, simulation=False):
    """Remove the specified (empty) MASS directory.

    Arguments:
    moose_dir -- (str) path to directory to be removed.
    simulation -- (bool) if true simulate moo command.
    """
    moo.run_moo_cmd("rmdir", [moose_dir], simulation=simulation)
    return


def put(local, remote, simulation=False):
    """Run moo put to send file(s) to specified destination.

    Arguments:
    local -- (str) path to file(s) to put (can include wildcard)
    remote -- (str) MASS destination directory
    simulation -- (bool) if true simulate moo command.
    """
    arg = local + [remote]
    moo.run_moo_cmd("put", arg, simulation=simulation)
    return


def put_safe_overwrite(local, remote, simulation=False):
    """Run moo put with the "safe overwrite" option to send file(s) to
    specified destination.

    Arguments:
    local -- (str) path to file(s) to put (can include wildcard)
    remote -- (str) MASS destination directory.
    simulation -- (bool) if true simulate moo command.
    """
    arg = ["-F"] + local + [remote]
    moo.run_moo_cmd("put", arg, simulation=simulation)
    return


def get(remote, local, transfer_threads, simulation=False, logger=None):
    """Run moo get to copy file(s) from MASS to local directory. The
    "force overwrite" option will be switched on.

    Arguments:
    remote -- (str) path to file(s) on MASS to copy (can include
    wildcards).
    local -- (str) path to local destination directory.
    transfer_threads -- (str) number of transfer threads to use to copy
    files.
    simulation -- (bool) if true simulate moo command.
    logger -- (logging.Logger) Logger to use. If omitted a logger will
    be obtained within :func:`cdds.deprecated.transfer.moo.run_moo_cmd`.
    """
    arg = ["-f", "-j", transfer_threads, remote, local]
    moo.run_moo_cmd("get", arg, simulation=simulation, logger=logger)
    return


def ls(moose_dir, simulation=False, logger=None):
    """Run an ls to list the contents of a directory. Does not
    recusrively list sub-directories. Returns a list of strings
    containing the stdout of the "moo ls" command.

    Arguments:
    moose_dir -- (str) path to MASS directory to list
    simulation -- (bool) if true simulate moo command.
    logger -- (logging.Logger) Logger to use. If omitted a logger will
    be obtained within :func:`cdds.deprecated.transfer.moo.run_moo_cmd`
    """
    if simulation == LS_ONLY:
        result = moo.run_moo_cmd("ls", ["-d"] + [moose_dir], logger=logger)
    else:
        result = moo.run_moo_cmd("ls", ["-d"] + [moose_dir],
                                 simulation=simulation, logger=logger)
    return result


def ls_file_sizes(moose_dir, simulation=False, logger=None):
    """
    Run an ls to list the contents of a directory and the
    corresponding file sizes.

    Parameters
    ----------
    moose_dir : str
        Moose URI of directory in MASS to list.
    simulation : bool, optional
        If true simulate running the moo command
    logger: :class:`logging.Logger`, optional
        Logger to use. If omitted a logger will be obtained within
        :func:`cdds.deprecated.transfer.moo.run_moo_cmd`.

    Returns
    -------
    : dict
        Moose URIs for each file in the specified directory and the
        corresponding sizes in bytes.
    """
    file_size_index = 4
    file_uri_index = -1
    if simulation == LS_ONLY:
        listing = moo.run_moo_cmd("ls", ["-l"] + [moose_dir], logger=logger)
    else:
        listing = moo.run_moo_cmd("ls", ["-l"] + [moose_dir],
                                  simulation=simulation, logger=logger)
    result = {}
    for line in listing:
        entry = line.split()
        # check line type; F = File, D = Directory, C = Collection
        if entry[0] != "F":
            continue
        result[entry[file_uri_index]] = int(entry[file_size_index])

    return result


def ls_tree(moose_dir, simulation=False):
    """Run a recursive "moo ls" command. This command uses paging
    options to ensure that the list fits into memory at all times. It
    returns the stdout of the command (list of strings in XML format).

    Arguments:
    moose_dir -- (str) path to top loevel directory to list.
    simulation -- (bool) if true simulate moo command.
    """
    if simulation == LS_ONLY:
        result = moo.run_moo_cmd("ls", ["-xR", "-p1-1000:25000", moose_dir])
    else:
        result = moo.run_moo_cmd("ls", ["-xR", "-p1-1000:25000", moose_dir],
                                 simulation=simulation)
    return result


def mv(old, new, simulation=False):
    """Run a mv command to rename a MASS directory.

    Arguments:
    old -- (str) path to original MASS path
    new -- (str) path to new MASS path
    simulation -- (bool) if true simulate moo command.
    """
    moo.run_moo_cmd("mv", [old, new], simulation=simulation)
    return


def dir_exists(moose_path, simulation=False):
    """Return True if specified MASS path exists, False otherwise.

    Arguments:
    moose_path -- (str) MASS path to check
    simulation -- (bool) if true simulate moo command.
    """
    logger = logging.getLogger(__name__)
    logger.debug('Checking MASS for existence of "{}"'.format(moose_path))
    out = moo.run_moo_cmd("test", ["-d", moose_path], simulation=simulation)
    if simulation:
        return True
    if out[0] == "true":
        return True
    else:
        return False


def kill_command(command_id, logger=None):
    """
    Run a moo kill command to attempt to halt a moose command.

    Parameters
    ----------
    command_id : str
        Command id of the moose command to attempt to kill.
    logger : :class:`logging.Logger`, optional
        Logger to use. If omitted a logger will be obtained within
        :func:`cdds.deprecated.transfer.moo.run_moo_cmd`.

    Returns
    -------
    : str
        stdout from kill command.
    """
    out = moo.run_moo_cmd("kill", [command_id], logger=logger)
    return out
