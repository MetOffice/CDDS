# CDDS Sim Review

The sim_review package extracts information to facilitate reviewing whether simulation tickets
have been correctly processed before the data is submitted for publication. This is useful because it ensures that simulations do not contain any critical issues or intermediate files prior to publication. This package works with `qc` to check report details and clearly show the content of approved variables files. At the end of the process, a data submission command is provided to the user ready for use.

Sim review is embeded as part of the `cdds_convert` script, hence it is not neccesary to run it as a separate process. However, the user can easily do so by activating the CDDS environment and using the command line tool `cdds_sim_review <path_to_request_file>`.

## An overview of Sim Review

The user configures the sim_review process using the `request` file.
The cdds_sim_review script then performs the following processing steps:

* Searches for critical issues in `prepare`. This typically reveals errors such as streams existing with the variable list that are not given in the request file or unrecognsied variables.
* Highlights any `extract` validation failures and the associated logfile.
* Clearly prints to the user any critical issues with the `convert` process on a stream-by-stream basis, nothing the variable, error and the number of cycles in which this error appears.
* Checks for critical issues in any data that has been marked as ready to archive.
* Communicates with `qc` to show the details of each `qc` report.
* Opens and prints the contents of any approved variables files to the user.
* Generates and provides a ready-to-use command for data submission.