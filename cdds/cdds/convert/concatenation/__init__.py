# (C) British Crown Copyright 2017-2021, Met Office.
# Please see LICENSE.rst for license details.
"""
CMOR netCDF file concatenation routines
"""
import glob
import logging
import os
import sqlite3
import time
import multiprocessing

from cdds.common import run_command
from cdds.convert.constants import (DEFAULT_SQLITE_TIMEOUT, NCRCAT,
                                    TASK_STATUS_COMPLETE, TASK_STATUS_STARTED,
                                    TASK_STATUS_FAILED)
from cdds.convert.exceptions import ConcatenationError


def prepare_to_concatenate_files(input_files, output_file, dummy_run):
    """
    Make any necessary peparation for the concatenation operation. This
    includes creating the output dirctory if it does not yet exist.

    Parameters
    ----------
    input_files: list
        A list of paths to the input files for the concatenation.
    output_file: str
        The path where output file from the concatenation will be written.
    dummy_run: Boolean
        If true, the concatenation will not be done, and suitable dry run log
        messages will be output.
    """
    logger = logging.getLogger(__name__)
    if dummy_run:
        logger.info('Dummy run: no preparatory work for concatenation.')
        return
    output_dir = os.path.dirname(output_file)
    if os.path.isdir(output_dir):
        logger.info('No preparatory work for concatenation. Continuing')
    else:
        logger.info('Creating output directory: {0}'.format(output_dir))
        os.makedirs(output_dir)
        logger.info('Directory created.')


def concatenate_files(input_files, output_file, candidate_file,
                      dummy_run=False):
    """
    Perform the concatenation operation.

    Parameters
    ----------
    input_files : list
        Names of the input files
    output_file : str
        Name of the output file
    candidate_file: str
        The name of the temporary file that ncrcat will write to.
    dummy_run : bool, optional
        If True print the command to be executed rather than execute
        it.

    Returns
    -------
    str
        Command used to perform the concatenation.

    Raises
    ------
    ConcatenationError
        if the ncrcat concatenation operation fails
    """
    logger = logging.getLogger(__name__)
    command = NCRCAT + input_files + ['-o', candidate_file]
    if dummy_run:
        logger.info('Dummy command: "{}"'.format(' '.join(command)))
    else:
        try:
            logger.info('Running command: "{}"'.format(' '.join(command)))
            run_command(command, 'Failed to concatenate netCDF data',
                        ConcatenationError, environment=os.environ)
        except ConcatenationError as err:
            logger.exception(err)
            raise
        os.rename(candidate_file, output_file)
    return ' '.join(command)


def move_single_file(input_file, output_file, dummy_run=False):
    """
    Perform the concatenation operation.

    Parameters
    ----------
    input_files : str
        Names of the input file
    output_file : str
        Name of the output file
    dummy_run : bool, optional
        If True print the command to be executed rather than execute
        it.

    Returns
    -------
    str
        The moving message containing SRC and DEST for os.rename.

    """
    logger = logging.getLogger(__name__)
    msg = 'Moving "{}" to "{}"'.format(input_file, output_file)

    if dummy_run:
        logger.info('Dummy command: "{}"'.format(msg))
    else:
        logger.info(msg)
        os.rename(input_file, output_file)

    return msg


def batch_concatenation(task_db, nworkers, timeout=DEFAULT_SQLITE_TIMEOUT,
                        **kwargs):
    """
    Manage the concatenations defined in task_db using nworkers threads
    to run processing in parallel. Tasks are organised by variable,
    i.e. all the concatenations required for a single variable are
    worked through in sequence, with separate threads handling the
    work for different variables.

    Parameters
    ----------
    task_db : str
        name of the sqlite database containing task information.
    nworkers : int
        number of threads to used to perform concatenations
    timeout : int, optional
        Time out for sql database connection

    Returns
    -------
    list
        output from each call to concatenation_task
    """
    kwargs['timeout'] = timeout
    logger = logging.getLogger(__name__)
    logger.info('Connecting to task database "{}"'.format(task_db))
    task_conn = sqlite3.connect(task_db, timeout=timeout)
    logger.info('Retrieving list of tasks')
    task_cursor = task_conn.cursor()
    variable_sql = ('SELECT DISTINCT variable, COUNT(1)'
                    'FROM concatenation_tasks WHERE status!=?'
                    'GROUP BY variable')
    work_to_do = list(task_cursor.execute(variable_sql,
                                          [TASK_STATUS_COMPLETE]))
    msg = 'Found {} tasks:\n'.format(len(work_to_do))
    for i in work_to_do:
        msg += '  {0} ({1})\n'.format(*i)
    logger.info(msg)

    if nworkers > 1:
        task_pool = multiprocessing.Pool(processes=nworkers)
        results = []
        for variable, nfiles in work_to_do:
            logger.info('Adding concatenation for {} ({} tasks) to pool'
                        ''.format(variable, nfiles))
            res = task_pool.apply_async(concatenation_task,
                                        (variable, task_db), kwargs)
            results.append(res)
        # wait for completion
        output = []
        for i in results:
            try:
                result = i.get()
            except Exception as err:
                logger.critical('concatenation_task for {} failed'
                                ''.format(variable))
                raise err
            output.append(result)
    else:
        results = []
        for variable, nfiles in work_to_do:
            logger.info('Performing concatenation for {} ({} tasks)'
                        ''.format(variable, nfiles))
            res = concatenation_task(variable, task_db, **kwargs)
            results += res
        output = results

    if any([isinstance(result, Exception) for result in results]):
        msg = 'Concatenation errors found. See log for details'
        logger.critical(msg)
        raise RuntimeError(msg)
    else:
        logger.info('Concatenations complete')

    return output


def concatenation_task(variable, task_db, timeout=DEFAULT_SQLITE_TIMEOUT,
                       **kwargs):
    """
    Routine to manage the processing of the specified variable

    Parameters
    ----------
    variable : str
        String of the format {mip table}/{variable} describing the
        variable to process.
    task_db : str
        name of the sqlite database containing task information.
    timeout : int, optional
        Time out for sqlite data base connections

    Returns
    -------
    list
        results from each call to run_single_concatenation_task
    """
    db_conn = sqlite3.connect(task_db, timeout=timeout)
    logger = logging.getLogger(__name__)
    logger.info('task running for {} under pid {}'
                ''.format(variable, os.getpid()))
    sql = ('SELECT output_file, input_files, candidate_file, status '
           'FROM concatenation_tasks WHERE variable = ?')
    task_cursor = db_conn.cursor()
    tasks_db = task_cursor.execute(sql, [variable])
    task_list = []
    # extract a task list from the database
    for task1 in tasks_db:
        task_list += [{'output_file': task1[0],
                       'input_files': task1[1].split(),
                       'candidate_file': task1[2],
                       'status': task1[3]}]

    # loop through the extracted tasks doing the required work
    results = []
    for task_num, task in enumerate(task_list):
        output_file = task['output_file']
        input_files = task['input_files']
        candidate_file = task['candidate_file']
        status = task['status']
        logger.info('{1} - Processing task for output {0}'.format(output_file,
                                                                  task_num))
        if not input_files:
            logger.info('No input files to process for '
                        ''.format(output_file))
            continue
        if status == TASK_STATUS_COMPLETE:
            logger.info('TASKS COMPLETE: Skipping completed task to generate'
                        '"{outfile}"'.format(outfile=output_file))
            continue
        elif status == TASK_STATUS_STARTED:
            timestamp_sql = ('SELECT start_timestamp FROM concatenation_tasks '
                             'WHERE output_file = ?')
            start_timestamp = task_cursor.execute(timestamp_sql, [output_file])
            logger.info('Output file "{out}" has status="{stat}" at time {ts}.'
                        ''.format(out=output_file, stat=TASK_STATUS_STARTED,
                                  ts=start_timestamp))
        else:
            logger.info('Task for output file {of} has status {stat}'
                        ''.format(of=output_file, stat=status))

        logger.info('Calling processing function for output {0}.'
                    ''.format(output_file))
        results.append(run_single_concatenation_task(
            db_conn, output_file, input_files, candidate_file, **kwargs))
    return results


def run_single_concatenation_task(db_conn, output_file, input_files,
                                  candidate_file, dummy_run=False,
                                  delete_source=True, **kwargs):
    """
    Wrapper to run a single concatenation task and update the task
    database accordingly.

    Parameters
    ----------
    db_conn : sqlite database connection
        connection to the task database
    output_file : str
        file to be created
    candidate_file: str
        The name of the temporary file that ncrcat will write to.
    input_files : list
        list of files to be concatenated
    dummy_run : bool, optional
        if True simulate the concatenation process and do not make any
        changes to the task database.
    delete_source : bool, optional
        if True delete the original files

    Returns
    -------
    list
        Results of the call to concatenate_files. Includes Exceptions
        raised if commands fail.
    """
    logger = logging.getLogger(__name__)
    task_cursor = db_conn.cursor()

    update_timestamp_sql = ('UPDATE concatenation_tasks '
                            'SET start_timestamp = CURRENT_TIMESTAMP, '
                            'status = "{}" '
                            'WHERE output_file = ?'
                            '').format(TASK_STATUS_STARTED)
    if dummy_run:
        logger.info('skipping update for task start')
    else:
        result = task_cursor.execute(update_timestamp_sql, [output_file])
        assert result.rowcount == 1, ('update of concatenation_tasks list '
                                      'failed:\n' + update_timestamp_sql)
        db_conn.commit()

    prepare_to_concatenate_files(input_files, output_file, dummy_run=dummy_run)

    try:
        logger.info('executing concatenation for file {outfile}'
                    ''.format(outfile=output_file))
        if len(input_files) == 1:
            result = move_single_file(input_files[0], output_file, dummy_run=dummy_run)
        else:
            result = concatenate_files(input_files, output_file, candidate_file,
                                       dummy_run=dummy_run)
        status = TASK_STATUS_COMPLETE
    except ConcatenationError as err:
        logger.critical('Concatenation of "{}" into "{}" failed with error '
                        '"{}"'.format(input_files, output_file, err))
        status = TASK_STATUS_FAILED
        # If failed return the Exception
        result = err

    update_status_sql = ('UPDATE concatenation_tasks '
                         'SET complete_timestamp = CURRENT_TIMESTAMP, '
                         'status = ? '
                         'WHERE output_file = ?')
    if dummy_run:
        logger.info('Skipped updating database as this is a dummy run')
    else:
        task_cursor.execute(update_status_sql, [status, output_file])
        db_conn.commit()

    logger.info('Reported status = {} for file "{}"'
                ''.format(status, output_file))

    if status == TASK_STATUS_COMPLETE and not dummy_run and delete_source and len(input_files) != 1:
        delete_originals(db_conn, output_file)
    return result


def delete_originals(db_conn, output_file):
    """
    Delete the original files after checking that a concatenation task
    has succeeded.

    Parameters
    ----------
    db_conn : sqlite database connection
        Connection to the task database
    output_file : str
        File to delete the source files for
    """
    logger = logging.getLogger(__name__)
    task_cursor = db_conn.cursor()
    logger.info('Confirming completion for "{}"'.format(output_file))
    # Safety net: check concatenation has completed and output file exists
    status_check_sql = ('SELECT status FROM concatenation_tasks '
                        'WHERE output_file = ?')
    status_obj = task_cursor.execute(status_check_sql, [output_file])
    status = status_obj.fetchone()
    if not status[0] == TASK_STATUS_COMPLETE:
        msg = ('Status for output_file "{}" is "{}", but must be "{}" '
               'prior to deletion.'.format(output_file, status,
                                           TASK_STATUS_COMPLETE))
        logger.error(msg)
        raise ConcatenationError(msg)
    if not os.path.exists(output_file):
        msg = ('Cannot delete input_files for output_file "{}"; output_file '
               'not found'.format(output_file))
        logger.error(msg)
        raise ConcatenationError(msg)

    input_files_sql = ('SELECT input_files FROM concatenation_tasks '
                       'WHERE output_file = ?')
    input_files_obj = task_cursor.execute(input_files_sql, [output_file])
    input_files = input_files_obj.fetchone()[0].split()
    logger.info('Found {} files for deletion: {}'
                ''.format(len(input_files), ', '.join(input_files)))
    for input_file in input_files:
        try:
            os.unlink(input_file)
        except OSError as err:
            logger.error('Deletion of "{}" failed. Error: {}'
                         ''.format(input_file, err))
            raise err

    logger.info('Deletions complete.')


if __name__ == '__main__':
    pass
