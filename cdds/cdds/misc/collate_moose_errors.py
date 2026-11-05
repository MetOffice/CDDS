# (C) British Crown Copyright 2026, Met Office.
# Please see LICENSE.md for license details.
"""Collect one MOOSE failure line per command ID from the extract and archive logs of a stream."""
import argparse
import fcntl
import re
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

from cdds.common.cdds_files.cdds_directories import log_directory
from cdds.common.request.request import Request, read_request

ERRORS_NAME = "moose_command_errors"
LOG_PATTERNS = {
    "extract": "cdds_extract_{}_*.log",
    "archive": "cdds_store_{}_*.log",
}
# Match any log line with a command ID followed by a parenthesized status tag.
MOOSE_FAILURE_PATTERN = re.compile(r"command-id=([^,\s'\"]+),\s+\([A-Z][A-Z0-9_]*\)")
LOG_DATE_PATTERN = re.compile(r"^(\d{4}-\d{2}-\d{2}) \d{2}:\d{2}:\d{2}")


def collect_failures(lines: Iterable[str], failures: dict[str, Tuple[str, str]]) -> None:
    """Add the date and first failure line for each new command ID in ``lines`` to ``failures``.

    Parameters
    ----------
    lines: Iterable[str]
        Log lines to scan.
    failures: dict[str, Tuple[str, str]]
        ``(date, line)`` keyed by command ID, updated in place.
    """
    log_date = ""
    for line in lines:
        date_match = LOG_DATE_PATTERN.match(line)
        # Continuation lines of multi-line messages carry no date, so keep the last one seen.
        if date_match:
            log_date = date_match.group(1)
        match = MOOSE_FAILURE_PATTERN.search(line)
        if match:
            failures.setdefault(match.group(1), (log_date, line))


def read_failures(paths: Iterable[Path]) -> dict[str, Tuple[str, str]]:
    """Return failures found in ``paths``, keeping the first occurrence of each command ID.

    Parameters
    ----------
    paths: Iterable[Path]
        Log files to scan.

    Returns
    -------
    dict[str, Tuple[str, str]]
        ``(date, line)`` keyed by command ID.
    """
    failures: dict[str, Tuple[str, str]] = {}
    for path in paths:
        with path.open(encoding="utf-8", errors="replace") as log_file:
            collect_failures(log_file, failures)
    return failures


def find_stream_logs(request: Request, stream: str) -> List[Path]:
    """Return the extract and archive logs for ``stream``.

    Parameters
    ----------
    request: Request
        The request being processed.
    stream: str
        Stream name.

    Returns
    -------
    List[Path]
        Paths of the matching log files.
    """
    logs: List[Path] = []
    for component, pattern in LOG_PATTERNS.items():
        log_dir = log_directory(request, component)
        if log_dir and Path(log_dir).is_dir():
            logs.extend(sorted(Path(log_dir).glob(pattern.format(stream))))
    return logs


def store_failures(errors_dir: Path, logs: Iterable[Path]) -> int:
    """Append failures not already recorded in ``errors_dir`` to daily logs named after each failure's date.

    Parameters
    ----------
    errors_dir: Path
        Directory holding the daily MOOSE failure logs.
    logs: Iterable[Path]
        Log files to scan.

    Returns
    -------
    int
        Number of new command IDs stored.
    """
    errors_dir.mkdir(parents=True, exist_ok=True)
    with (errors_dir / ".lock").open("w") as lock_file:
        # Several streams may collate at once.
        fcntl.flock(lock_file, fcntl.LOCK_EX)
        existing = read_failures(errors_dir.glob("{}_*.log".format(ERRORS_NAME)))

        new_by_date: dict[str, List[str]] = defaultdict(list)
        for command_id, (log_date, line) in read_failures(logs).items():
            if command_id not in existing:
                new_by_date[log_date or date.today().isoformat()].append(line)

        for log_date, lines in new_by_date.items():
            errors_log = errors_dir / "{}_{}.log".format(ERRORS_NAME, log_date)
            with errors_log.open("a", encoding="utf-8") as errors_file:
                errors_file.writelines(lines)
    return sum(len(lines) for lines in new_by_date.values())


def parse_args(arguments: Optional[List[str]]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request", help="The full path to the request configuration file")
    parser.add_argument("-s", "--stream", required=True, help="The stream to collate MOOSE errors for")
    return parser.parse_args(arguments)


def main_collate_moose_errors(arguments: Optional[List[str]] = None) -> int:
    """Collate MOOSE command failures for a stream into daily logs in ``<root_proc_dir>/moose_command_errors/``.

    Parameters
    ----------
    arguments: Optional[List[str]]
        The command line arguments to be parsed.

    Returns
    -------
    int
        Exit code.
    """
    args = parse_args(arguments)
    request = read_request(args.request)
    errors_dir = Path(request.common.root_proc_dir) / ERRORS_NAME
    logs = find_stream_logs(request, args.stream)
    new_count = store_failures(errors_dir, logs)
    print("Stored {} new moose failure command ID(s) from {} log(s) in {}".format(new_count, len(logs), errors_dir))
    return 0
