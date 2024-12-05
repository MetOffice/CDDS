# (C) British Crown Copyright 2023, Met Office.
from datetime import datetime
import os
import os.path
from pathlib import Path
import sqlite3


def check_workflow(workflow_name, task, status):
    """Check that a particular task has completed in specific workflow.

    Assumes that there will be only one such task in the workflow.

    Parameters
    ----------
    workflow_name : str
        The name of the workflow to check.
    task : str
        The task of interest e.g. "workflow_complete"
    status : str
        The status of the task e.g. "succeeded"

    Returns
    -------
    tuple : tuple[boo, dict]
        A tuple of (bool, dict)
    """
    cylc_run_dir = os.path.expandvars(os.path.join("$HOME", "cylc-run"))
    self_workflow_db = Path(cylc_run_dir, os.environ["CYLC_WORKFLOW_ID"], "log", "db")
    target_workflow_db = Path(cylc_run_dir, workflow_name, "log", "db")

    if not target_workflow_db.exists():
        print("XTDEBUG: Trigger NOT Satisifed: Target workflow doesn't exist.")
        return (False, {})

    def _get_modified_time(db_path):
        unix_epoch = os.stat(db_path).st_mtime
        return datetime.fromtimestamp(unix_epoch)

    if _get_modified_time(target_workflow_db) < _get_modified_time(self_workflow_db):
        print("XTDEBUG: Trigger NOT satisfied: Target workflow modified before running workflow.")
        return (False, {})

    target_db_conn = sqlite3.connect(target_workflow_db, timeout=1.0)
    task_completion_query = (
        f"SELECT name, cycle, status FROM task_states WHERE name = '{task}'"
    )
    query_result = target_db_conn.execute(task_completion_query).fetchall()
    target_db_conn.close()

    if query_result:
        for task_name, task_cycle, task_status in query_result:
            print("XTDEBUG:", task_name, task_cycle, task_status)
            if task_name == task and task_status == status:
                print("XTDEBUG: Trigger IS Satisfied:")
                return (True, {})

    print("XTDEBUG: Trigger NOT Satisfied:")
    return (False, {})
