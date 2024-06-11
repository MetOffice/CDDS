# Simulation Ticket Review Procedure

After a package is processed by following the [operational procedure](../operational_procedure/cmip6.md), the user assigns 
the ticket to a member of the CDDS team to review the processing and then perform the final step to submit the data for 
publication. This document describes the steps that need to be performed in the review. The check before publishing steps 
should also be done by the user who processed the data to check that the processing has been successful. The final publication 
steps can only be performed by a member of the CDDS teams with the required permission.

## Checklist before publication

!!! info
      All the following checks can be combined in a single command by running:
      ```bash
      . ~cdds/bin/setup_env_for_cdds <version>
      cdds_sim_review <location of request.cfg>
      ```

- [x] Check the critical issues log in the `critical_issues.log` for each component. 
      See the [operational procedure](../operational_procedure/cmip6.md) for more details.

!!! info
    You can use following command to check for critical logs:
    ```bash
    grep -irn "critical"  $CDDS_PROC_DIR --exclude "*.py" --exclude "*.svn*"
    ```

- [x] Check the QC report in `$CDDS_PROC_DIR/qualitycheck/report_<date-time>.json`.  The `aggregated_summary` and `details` 
      fields should be empty.

- [x] Check approved variables list that expected variables have been added.

- [x] Check that variables with recently reported issues are not in the approved variables list.

- [x] Check permissions for `proc/archive/log`. It should have write permissions for everyone, so `move_in_mass` can work.

!!! info
    You can check the premissions for `proc/archive/log` by running following command:
    ```bash
    ls -l $CDDS_PROC_DIR/transfer/ | grep log
    ```
    The permission should be `drwxrwxrwx` for the log directory.

- [x] Look for any partial files left over from the concatenation process using the find command:
      ```bash
      find $CDDS_DATA_DIR/output/*_* -type f
      ```

## Submission for publication

In order to complete the submission, you will need access to the `els055` server. Only members of the CDDS team are 
expected to do this part.

- [x] After completing the pre-publication checks, add a message to the ticket to confirm that the processing was successful.
- [x] Log on to `els055`.

!!! info
       If you have not logged on before, please see the section below on setting up `els055`.

- [x] Run the `move_in_mass` command that was generated when running `cdds_sim_review`.

!!! example
    ```bash
    move_in_mass request.json -p --original_state=embargoed --new_state=available --mass_location=production --variables_list_file=approved_variables_YYYY-MM-DDThhmmss.txt
    ```

- [x] When `move_in_mass` has completed, check for errors in the log file: `$CDDS_PROC_DIR/archive/log/move_in_mass_<date-time>.log`

!!! info
    Use `grep` to search for any `CRITICAL` messages in the log file:
    ```bash
    grep "CRITICAL" $CDDS_PROC_DIR/archive/log/move_in_mass_<date-time>.log
    ```
    The `<date-time>` must be replaced to the time stamp of the log file.

- [x] Confirm that the last line includes the phrase `Moving complete`.

- [x] Check the message queue to confirm that messages are waiting for processing.

!!! info
    - For CMIP6, you can use following command to confirm that shows the messages are waiting for processing:
      ```bash
      list_queue CMIP6_available
      ```
    - For CMIP6Plus, you can use following command to confirm that shows the messages are waiting for processing:
      ```bash
      list_queue CMIP6Plus_available
      ```

- [x] Once you are happy that the `move_in_mass` command has executed successfully, add a message stating this to the 
      ticket, change the status of the ticket to `approved` and reassign to the original user for teardown and closing.

## Setting up els055

- [x] Create a new file `~/.cdds_credentials`.

- [x] Contact [Matt Mizielinski](mailto:matt.mizielinski@metoffice.gov.uk) for the required settings.