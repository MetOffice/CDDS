# (C) British Crown Copyright 2010-2021, Met Office.
# Please see LICENSE.rst for license details.
"""
Classes and functions for performing quality control operations.
"""
from numpy import ndarray, ma

from mip_convert.plugins.quality_control import (BoundsChecker,
                                                 OutOfBoundsError,
                                                 PASS_VALUE,
                                                 SET_TO_FILL_VALUE,
                                                 SET_TO_VALID_VALUE,
                                                 RAISE_EXCEPTION,
                                                 UM_MDI)


__docformat__ = "epytext"


class MaskedArrayBoundsChecker(BoundsChecker):
    """
    Class for checking and, if required, adjusting numpy MaskedArrays.
    """

    def __init__(self, fill_value=UM_MDI, valid_min=None, valid_max=None, tol_min=None, tol_max=None,
                 tol_min_action=RAISE_EXCEPTION, tol_max_action=RAISE_EXCEPTION, oob_action=RAISE_EXCEPTION):

        super(MaskedArrayBoundsChecker, self).__init__(fill_value, valid_min, valid_max, tol_min, tol_max,
                                                       tol_min_action, tol_max_action, oob_action)

    def check_bounds(self, array):
        """
        This implementation uses boolean index arrays to locate and, if required, update array values.
        It does multiple (fast) read-only passes over the input masked array to generate index arrays
        of any elements that need to be operated upon. The index array has the same shape and size as
        the input array, but performance appears to be good in spite of this.

        In general the idiom goes as follows:

           ind = array < some_value   # get a boolean index array whose elements are True where
                                      # array[i] matches the test (< some_value in this instance)
           if ind.any() :             # if some values were found...
              array[ind] = new_value  # ...do something

        @param array: A MaskedArray object containing the array of values to check.
        @type  array: MaskedArray
        @return: The total number of reset values, which may be 0.
        @raise OutOfBoundsError: Raised if an array value is out of bounds and oob_action is set to
           the constant RAISE_EXCEPTION.
        """
        self.stats = dict(total=0, tol_min=0, tol_max=0, oob_min=0, oob_max=0)
        if self.tol_min_action == PASS_VALUE and (self.tol_max_action == PASS_VALUE and self.oob_action == PASS_VALUE):
            return 0

        # if we're going to fail, then fail early so we don't make nugatory array updates
        self._check_for_oob_values(array)

        # do lower bounds checks
        self._check_lower_bounds(array)

        # do upper bounds checks
        self._check_upper_bounds(array)

        # compute total number of reset values
        total = (self.stats['tol_min'] + self.stats['tol_max'] + self.stats['oob_min'] + self.stats['oob_max'])
        self.stats['total'] = total
        self.logger.debug("Results of bounds-check: %s" % self.stats)
        return self.stats['total']

    def _check_for_oob_values(self, array):
        """
        Check for out-of-bounds values, raising an OutOfBoundsError if
        any are detected.
        """
        # check for lower out-of-bounds values
        if self.valid_min is not None:
            if self.tol_min_action == RAISE_EXCEPTION or (self.oob_action == RAISE_EXCEPTION):
                minval = self.valid_min

                if self.tol_min_action != RAISE_EXCEPTION and (self.tol_min is not None):
                    # use tol_min if a non-exception action is defined for the lower tolerance band
                    minval = self.tol_min
                ind = array < minval

                if ind.any():
                    bad = array[ind].compressed()
                    self.stats['oob_min'] = bad.size
                    raise OutOfBoundsError(bad[0], vmin=minval)

        # check for upper out-of-bounds values
        if self.valid_max is not None:

            if self.tol_max_action == RAISE_EXCEPTION or self.oob_action == RAISE_EXCEPTION:
                maxval = self.valid_max
                if self.tol_max_action != RAISE_EXCEPTION and self.tol_max is not None:
                    # use tol_max if a non-exception action is defined for the upper tolerance band
                    maxval = self.tol_max
                ind = array > maxval

                if ind.any():
                    bad = array[ind].compressed()
                    self.stats['oob_max'] = bad.size
                    raise OutOfBoundsError(bad[0], vmax=maxval)

    def _check_lower_bounds(self, array):
        """
        Check and, if required, adjust values in or below the lower tolerance zone.
        """
        # if valid_min is defined then do lower bounds checks in 1 or 2 passes
        if self.valid_min is not None:
            # check for values in the lower tolerance zone
            if self.tol_min is not None and self.tol_min_action != PASS_VALUE:
                ind = (array >= self.tol_min) & (array < self.valid_min)

                if ind.any():
                    if self.tol_min_action == SET_TO_VALID_VALUE:
                        array[ind] = self.valid_min
                        self.stats['tol_min'] = ind.nonzero()[0].size
                    elif self.tol_min_action == SET_TO_FILL_VALUE:
                        array[ind] = ma.masked
                        self.stats['tol_min'] = ind.nonzero()[0].size

            # check for lower out-of-bounds values
            if self.oob_action == SET_TO_FILL_VALUE:
                if self.tol_min is None:
                    ind = array < self.valid_min
                else:
                    ind = array < self.tol_min
                if ind.any():
                    array[ind] = ma.masked
                    self.stats['oob_min'] = ind.nonzero()[0].size

    def _check_upper_bounds(self, array):
        """
        Check and, if required, adjust values in or below the upper tolerance zone.
        """
        # if valid_max is defined then do upper bounds checks in 1 or 2 passes
        if self.valid_max is not None:
            # 1: check for values in the upper tolerance zone
            if self.tol_max is not None and self.tol_max_action != PASS_VALUE:
                ind = (array > self.valid_max) & (array <= self.tol_max)

                if ind.any():
                    if self.tol_max_action == SET_TO_VALID_VALUE:
                        array[ind] = self.valid_max
                        self.stats['tol_max'] = ind.nonzero()[0].size
                    elif self.tol_max_action == SET_TO_FILL_VALUE:
                        array[ind] = ma.masked
                        self.stats['tol_max'] = ind.nonzero()[0].size

            # 2: check for upper out-of-bounds values
            if self.oob_action == SET_TO_FILL_VALUE:
                if self.tol_max is None:
                    ind = array > self.valid_max
                else:
                    ind = array > self.tol_max
                if ind.any():
                    array[ind] = ma.masked
                    self.stats['oob_max'] = ind.nonzero()[0].size


if __name__ == "__main__":
    import doctest

    _module_tests = """
   >>> test_values = [-9999.0, -10.0, -0.01, -0.005, 0.0, 50.0, 100.0, 100.005, 100.01, 110.0]
   >>> flist = list(test_values)
   >>> checker = BoundsChecker(fill_value=-9999.0, valid_min=0.0, valid_max=100.0,
   ...              tol_min=-0.01, tol_max=100.01,
   ...              tol_min_action=SET_TO_VALID_VALUE, tol_max_action=SET_TO_VALID_VALUE,
   ...              oob_action=SET_TO_FILL_VALUE)
   >>> checker.check_bounds(flist)
   6
   >>> flist
   [-9999.0, -9999.0, 0.0, 0.0, 0.0, 50.0, 100.0, 100.0, 100.0, -9999.0]
   >>> flist = [UM_MDI, -10.0, 0.0, 50.0, 100.0, 110.0, UM_MDI]
   >>> checker.fill_value = UM_MDI
   >>> checker.check_bounds(flist)
   2
   >>> flist
   [-1073741824.0, -1073741824.0, 0.0, 50.0, 100.0, -1073741824.0, -1073741824.0]
   >>> t = (-9999.0, -10.0, -0.01, -0.005, 0.0)
   >>> checker.check_bounds(t)
   Traceback (most recent call last):
      ...
   AssertionError: ...
   >>> marray = ma.masked_values(test_values, -9999.0)
   >>> ma_checker = MaskedArrayBoundsChecker(fill_value=-9999.0, valid_min=0.0, valid_max=100.0,
   ...              tol_min=-0.01, tol_max=100.01,
   ...              tol_min_action=SET_TO_VALID_VALUE, tol_max_action=SET_TO_VALID_VALUE,
   ...              oob_action=SET_TO_FILL_VALUE)
   >>> ma_checker.check_bounds(marray)
   6
   >>> marray.data.tolist()
   [-9999.0, -10.0, 0.0, 0.0, 0.0, 50.0, 100.0, 100.0, 100.0, 110.0]
   >>> marray.mask.tolist()
   [True, True, False, False, False, False, False, False, False, True]
   >>> marray = ma.masked_values(test_values, -9999.0)
   >>> ma_checker.oob_action = RAISE_EXCEPTION
   >>> ma_checker.check_bounds(marray)
   Traceback (most recent call last):
      ...
   OutOfBoundsError: ...
   """
    __test__ = {'module tests': _module_tests}
    doctest.testmod(optionflags=doctest.IGNORE_EXCEPTION_DETAIL)
