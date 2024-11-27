# (C) British Crown Copyright 2023, Met Office.
from datetime import datetime
import os
import os.path
from pathlib import Path
import sqlite3


def monitor_workflows(workflow_base_name, task_base_name, status, streams):
    """A custom XTrigger function that can mointor task completion status in
    multiple workflows.

    Parameters
    ----------
    workflow_base_name : str
        A workflow base name that will be combined with each stream.
    task_base_name : str
        The task of interest in the workflow being monitored. 
    status : str
        The status of the task that will satisify this XTrigger.
    streams : str
        A list of streams delimited by an underscore e.g "ap4_ap5_onm"   

    Returns
    -------
    tuple
        A tuple of (bool, dict)
    """
    results = []
    for stream in streams.split("_"):
        workflow_name = f"{workflow_base_name}_{stream}"
        task_name = f"{task_base_name}_{stream}"
        workflow_completed = check_workflow(workflow_name, task_name, status)
        results.append(workflow_completed)

        if not workflow_completed:
            break

    return (True, {}) if all(results) else (False, {})


def check_workflow(workflow_name, task, status):
    """Check that a particular task has completed in specific workflow.

    Parameters
    ----------
    workflow_name : str
        The name of the workflow to check.
    task : str
        The task of interest e.g. "completion_ap5"
    status : str
        The status of the task e.g. "succeeded"

    Returns
    -------
    bool
        Will return True if the task has succeed, otherwise False.
    """
    cylc_run_dir = os.path.expandvars(os.path.join("$HOME", "cylc-run"))
    self_workflow_db = Path(cylc_run_dir, os.environ["CYLC_WORKFLOW_ID"], "log", "db")
    target_workflow_db = Path(cylc_run_dir, workflow_name, "log", "db")

    if not target_workflow_db.exists():
        print("XTDEBUG: Trigger NOT Satisifed: Target workflow doesn't exist.")
        return False

    def _get_modified_time(db_path):
        unix_epoch = os.stat(db_path).st_mtime
        return datetime.fromtimestamp(unix_epoch)

    if _get_modified_time(target_workflow_db) < _get_modified_time(self_workflow_db):
        print("XTDEBUG: Trigger NOT satisfied: Target workflow modified before running workflow.")
        return False

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
                return True

    print("XTDEBUG: Trigger NOT Satisfied:")
    return False
