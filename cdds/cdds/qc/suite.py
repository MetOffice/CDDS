# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.

import sys
from collections import defaultdict
from compliance_checker.runner import CheckSuite


class QCSuite(CheckSuite):
    """
    Extending standard check suite to add some configuration capabilities
    """

    def _get_valid_checkers(self, ds, checker_names):
        """
        Returns a filtered list of 2-tuples: (name, valid checker) based on
        the ds object's type and the user selected names.

        Parameters
        ----------
        ds: netCDF4.Dataset
            A single dataset the QC will be run for
        checker_names: list
            List of checker names.

        Returns
        -------
        : list
            List of valid checkers
        """
        assert self.checkers, "No checkers could be found."
        if not checker_names:
            checker_names = list(self.checkers.keys())
        args = [(name, self.checkers[name])
                for name in checker_names if name in self.checkers]
        valid = []
        all_checked = set([a[1] for a in args])  # only class types
        checker_queue = set(args)

        while checker_queue:
            name, a = checker_queue.pop()
            # is the current dataset type in the supported filetypes
            # for the checker class?
            supported = False
            for supported_ds in a.supported_ds:
                if isinstance(ds, supported_ds):
                    supported = True
            if supported:
                valid.append((name, a))
            # add any subclasses of the checker class
            for subc in a.__subclasses__():
                if subc not in all_checked:
                    all_checked.add(subc)
                    checker_queue.add((name, subc))

        return valid

    def run(self, ds, checker_config, skip_checks, *checker_names):
        """
        Runs this CheckSuite on the dataset with all the passed Checker
        instances.
        Returns a dictionary mapping checker names to a 2-tuple of their
        grouped scores and errors/exceptions while running checks.
        """

        ret_val = {}
        checkers = self._get_valid_checkers(ds, checker_names)
        if not checkers:
            print((
                "No valid checkers found for tests '{}'".format(
                    ",".join(checker_names))))

        for checker_name, checker_class in checkers:
            try:
                if checker_name in checker_config:
                    checker = checker_class(
                        config=checker_config[checker_name])
                else:
                    checker = checker_class()
            except TypeError:
                checker = checker_class()
            checker.setup(ds)

            checks = self._get_checks(checker, defaultdict(lambda: None))
            vals = []
            errs = {}  # check method name -> (exc, traceback)
            for c, max_level in checks:
                try:
                    vals.extend(self._run_check(c, ds, max_level))
                except Exception as e:
                    errs[c.__func__.__name__] = (e, sys.exc_info()[2])
            # score the results we got back
            groups = self.scores(vals)
            ret_val[checker_name] = groups, errs
        return ret_val
