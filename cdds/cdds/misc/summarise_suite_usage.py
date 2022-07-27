#!/usr/bin/env python3
# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
"""
Calculate total usage of a set of suites and present summary stats
"""
import argparse
from collections import defaultdict
import datetime
import subprocess
import sys


def parse_args(args=None):
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser(description='Summarise CPU usage')
    parser.add_argument('-s', '--summary', action='store_true',
                        help='Only provide summary totals')
    parser.add_argument('-q', '--queue', action='store_true',
                        help='Provide queueing information rather than CPU time')
    parser.add_argument('suite_names', nargs='+', help='Names of suites')

    arguments = parser.parse_args(args)
    return arguments.suite_names, arguments.summary, arguments.queue


def main():
    """
    Main routine
    """
    suite_names, summary, queue = parse_args()

    suite_total = defaultdict(int)
    suite_total_queue = defaultdict(int)
    r_data = defaultdict(list)
    q_data = defaultdict(list)

    def t(x):
       return datetime.datetime.strptime(x, '%Y-%m-%dT%H:%M:%SZ')

    for suite in suite_names:
        result = subprocess.check_output(['cylc', 'report-timings', '--raw', suite], universal_newlines=True )
        for line in result.split('\n'):
            line_list = [i for i in line.split(' ') if i is not '']
            if line[:4] == 'name' or not line:
                continue
            sub_time = t(line_list[4])
            start_time = t(line_list[5])
            succeed_time = t(line_list[6])

            q_t = (start_time - sub_time).seconds
            r_t = (succeed_time - start_time).seconds

            r_data[line_list[0]].append(r_t)
            q_data[line_list[0]].append(q_t)
            suite_total[suite] += r_t
            suite_total_queue[suite] += q_t

    if queue:
        print_data(q_data, suite_total_queue, summary)
    else:
        print_data(r_data, suite_total, summary)


def print_data(data, suite_total, summary):
    """
    Print results

    Parameters
    ----------
    data : dict
        dictionary of data to work with {suite_name: [job times]}
    suite_total : dict
        Summary by suite.
    summary : bool
        only print summary data
    """
    total = 0
    for k, v in sorted(data.items()):
        if not summary:
            print('{: <35}: min = {}, mean = {:.2f}, max = {}, sum = {} s'.format(k, min(v), sum(v)/len(v), max(v), sum(v)))
        total += sum(v)

    for k, v in sorted(suite_total.items()):
       print('Suite: {} total: {:.2f} hours'.format(k, v/3600))

    print('Total: {:.2f} hours'.format(total/3600))


if __name__ == '__main__':
    main()
