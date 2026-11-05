# (C) British Crown Copyright 2026, Met Office.
# Please see LICENSE.md for license details.
"""Collect one MOOSE failure line per command ID from the extract and archive logs of a stream."""
import argparse
import fcntl
import re
from pathlib import Path
from typing import Iterable, List, Optional

from cdds.common.cdds_files.cdds_directories import log_directory
from cdds.common.request.request import Request, read_request

CENTRAL_LOG_NAME = "moose_command_errors.log"
LOG_PATTERNS = {
    "extract": "cdds_extract_{}_*.log",
    "archive": "cdds_store_{}_*.log",
}
# Match any log line with a command ID followed by a parenthesized status tag.
MOOSE_FAILURE_PATTERN = re.compile(r"command-id=([^,\s'\"]+),\s+\([A-Z][A-Z0-9_]*\)")


def collect_failures(lines: Iterable[str], failures: dict[str, str]) -> None:
    """Add the first failure line for each new command ID in ``lines`` to ``failures``.

    Parameters
    ----------
    lines: Iterable[str]
        Log lines to scan.
    failures: dict[str, str]
        Failure lines keyed by command ID, updated in place.
    """
    for line in lines:
        match = MOOSE_FAILURE_PATTERN.search(line)
        if match:
            failures.setdefault(match.group(1), line)


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


def store_failures(central_log: Path, logs: Iterable[Path]) -> int:
    """Append failure lines for command IDs not already in ``central_log``.

    Parameters
    ----------
    central_log: Path
        Shared log of MOOSE failures.
    logs: Iterable[Path]
        Log files to scan.

    Returns
    -------
    int
        Number of new command IDs stored.
    """
    with central_log.open("a+", encoding="utf-8", errors="replace") as central_file:
        # Lock held across read and append as several streams may write at once.
        fcntl.flock(central_file, fcntl.LOCK_EX)
        central_file.seek(0)
        existing: dict[str, str] = {}
        collect_failures(central_file, existing)

        failures = dict(existing)
        for log_path in logs:
            with log_path.open(encoding="utf-8", errors="replace") as log_file:
                collect_failures(log_file, failures)

        new_lines = [line for command_id, line in failures.items() if command_id not in existing]
        central_file.writelines(new_lines)
    return len(new_lines)


def parse_args(arguments: Optional[List[str]]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request", help="The full path to the request configuration file")
    parser.add_argument("-s", "--stream", required=True, help="The stream to collate MOOSE errors for")
    return parser.parse_args(arguments)


def main_collate_moose_errors(arguments: Optional[List[str]] = None) -> int:
    """Collate MOOSE command failures for a stream into the central log under ``root_proc_dir``.

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
    central_log = Path(request.common.root_proc_dir) / CENTRAL_LOG_NAME
    logs = find_stream_logs(request, args.stream)
    new_count = store_failures(central_log, logs)
    print("Stored {} new failure command ID(s) from {} log(s) in {}".format(new_count, len(logs), central_log))
    return 0
