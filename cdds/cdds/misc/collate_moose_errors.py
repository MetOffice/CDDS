# (C) British Crown Copyright 2026, Met Office.
# Please see LICENSE.md for license details.
"""Collect one MOOSE failure line per command ID from the extract and archive logs of a stream."""
import argparse
import fcntl
import re
from collections import defaultdict
from pathlib import Path
from typing import Iterable, Optional

from cdds.common.cdds_files.cdds_directories import log_directory
from cdds.common.request.request import Request, read_request

ERROR_COLLATION_DIR = "moose_command_errors"
LOG_PATTERNS = {
    "extract": "cdds_extract_{}_*.log",
    "archive": "cdds_store_{}_*.log",
}
# Match any log line with a command ID followed by a parenthesized status tag.
MOOSE_FAILURE_PATTERN = re.compile(r"command-id=([^,\s'\"]+),\s+\([A-Z][A-Z0-9_]*\)")
LOG_DATE_PATTERN = re.compile(r"^(\d{4}-\d{2}-\d{2}) \d{2}:\d{2}:\d{2}")
# Noise removed from a failure line when it is first written to the collated log (extract, then transfer).
LOG_LINE_PREFIXES = (
    "cdds.extract.common.run_moo_cmd DEBUG: moo output: ",
    "cdds.extract.common.run_moo_cmd INFO: moo output: ",
    "MOO command standard error ",
)
# ``(date, line, source log path)`` keyed by command ID.
Failures = dict[str, tuple[str, str, Path]]


def collect_failures(lines: Iterable[str], path: Path, failures: Failures) -> None:
    """Add the date, first failure line and source path for each new command ID in ``lines`` to ``failures``.

    Parameters
    ----------
    lines: Iterable[str]
        Log lines to scan.
    path: Path
        Log file the lines were read from.
    failures: Failures
        ``(date, line, path)`` keyed by command ID, updated in place.
    """
    log_date = ""
    timestamp = ""
    for line in lines:
        date_match = LOG_DATE_PATTERN.match(line)
        # Continuation lines of multi-line messages carry no timestamp, so keep the last one seen.
        if date_match:
            log_date = date_match.group(1)
            timestamp = date_match.group(0)
        match = MOOSE_FAILURE_PATTERN.search(line)
        if match:
            if not date_match:
                line = "{} {}".format(timestamp, line)
            failures.setdefault(match.group(1), (log_date, line, path))


def read_failures(paths: Iterable[Path]) -> Failures:
    """Return failures found in ``paths``, keeping the first occurrence of each command ID.

    Parameters
    ----------
    paths: Iterable[Path]
        Log files to scan.

    Returns
    -------
    Failures
        ``(date, line, path)`` keyed by command ID.
    """
    failures: Failures = {}
    for path in paths:
        with path.open() as log_file:
            collect_failures(log_file, path, failures)
    return failures


def find_stream_logs(request: Request, stream: str) -> list[Path]:
    """Return the extract and archive logs for ``stream``.

    Parameters
    ----------
    request: Request
        The request being processed.
    stream: str
        Stream name.

    Returns
    -------
    list[Path]
        Paths of the matching log files.
    """
    logs: list[Path] = []
    for component, pattern in LOG_PATTERNS.items():
        log_dir = log_directory(request, component)
        if log_dir:
            logs.extend(sorted(Path(log_dir).glob(pattern.format(stream))))
    return logs


def store_failures(errors_dir: Path, logs: Iterable[Path], stream: str) -> int:
    """Append failures not already recorded in ``errors_dir`` to daily logs named after each failure's date.

    Parameters
    ----------
    errors_dir: Path
        Directory holding the daily MOOSE failure logs.
    logs: Iterable[Path]
        Log files to scan.
    stream: str
        Stream name, appended to each stored line along with the source log path.

    Returns
    -------
    int
        Number of new command IDs stored.
    """
    errors_dir.mkdir(parents=True, exist_ok=True)
    with (errors_dir / ".lock").open("w") as lock_file:
        # Several streams may collate at once.
        fcntl.flock(lock_file, fcntl.LOCK_EX)
        existing = read_failures(errors_dir.glob("{}_*.log".format(ERROR_COLLATION_DIR)))

        new_by_date: dict[str, list[str]] = defaultdict(list)
        for command_id, (log_date, line, path) in read_failures(logs).items():
            if command_id not in existing:
                # Only newly stored lines are trimmed; source logs and already stored lines are left unchanged.
                for prefix in LOG_LINE_PREFIXES:
                    line = line.replace(prefix, "", 1)
                line = line.rstrip("\n")
                new_by_date[log_date].append(
                    "{} stream:{}, log origin: {}\n".format(line, stream, path.resolve())
                )

        for log_date, lines in new_by_date.items():
            errors_log = errors_dir / "{}_{}.log".format(ERROR_COLLATION_DIR, log_date)
            with errors_log.open("a") as errors_file:
                errors_file.writelines(lines)
    return sum(len(lines) for lines in new_by_date.values())


def parse_args(arguments: Optional[list[str]]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request", help="The full path to the request configuration file")
    parser.add_argument("-s", "--stream", required=True, help="The stream to collate MOOSE errors for")
    return parser.parse_args(arguments)


def main_collate_moose_errors(arguments: Optional[list[str]] = None) -> int:
    """Collate MOOSE command failures for a stream into daily logs in ``<root_proc_dir>/moose_command_errors/``.

    Parameters
    ----------
    arguments: Optional[list[str]]
        The command line arguments to be parsed.

    Returns
    -------
    int
        Exit code.
    """
    args = parse_args(arguments)
    request = read_request(args.request)
    errors_dir = Path(request.common.root_proc_dir) / ERROR_COLLATION_DIR
    logs = find_stream_logs(request, args.stream)
    new_count = store_failures(errors_dir, logs, args.stream)
    print(
        "Collating any MOOSE errors from the logs for record keeping and debugging purposes.\n"
        "Stored {} new moose failure command ID(s) from {} log(s) to {}".format(new_count, len(logs), errors_dir)
    )
    return 0
