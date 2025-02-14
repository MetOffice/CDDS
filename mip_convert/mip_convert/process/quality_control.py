# (C) British Crown Copyright 2010-2025, Met Office.
# Please see LICENSE.md for license details.
"""
Classes and functions for performing quality control operations.
"""
from numpy import ndarray, ma

from mip_convert.common import ObjectWithLogger

__docformat__ = "epytext"

# Constants for various value-adjustment options.
PASS_VALUE = 0
SET_TO_FILL_VALUE = 1
SET_TO_VALID_VALUE = 2
RAISE_EXCEPTION = 3

# Default UM/PP missing data indicator.
UM_MDI = -1073741824.0


class OutOfBoundsError(Exception):
    """Exception class for representing an out-of-bounds error condition."""

    def __init__(self, value, vmin=None, vmax=None):
        super(OutOfBoundsError, self).__init__()
        self.value = value
        self.vmin = vmin
        self.vmax = vmax

    def __str__(self):
        """
        Return a string representation of the exception.
        """
        if self.vmin is not None and self.vmax is not None:
            msg = "%s: Value %f is outside range %f to %f" % (self.__class__.__name__, self.value, self.vmin, self.vmax)
        elif self.vmin is not None:
            msg = "%s: Value %f is less than %f" % (self.__class__.__name__, self.value, self.vmin)
        elif self.vmax is not None:
            msg = "%s: Value %f is greater than %f" % (self.__class__.__name__, self.value, self.vmax)
        else:
            msg = "%s: Value %f is out of bounds" % (self.__class__.__name__, self.value)
        return msg


class BoundsChecker(ObjectWithLogger):
    """
    Class for checking and, if required, adjusting arrays of values. Bounds-checking typically
    will be performed against arrays (e.g. lists) of Python floats.

    Objects of this class may be reused in different contexts by assigning suitable values to the
    min/max bounds and actions attributes, as defined in the __init__ method.

    The default actions are intentionally set so as to raise exceptions. This is to avoid silent
    pass-through of out-of-bounds values. Acceptance of such values thus requires an explicit choice
    on the part of the calling program.
    """

    def __init__(self, fill_value=UM_MDI, valid_min=None, valid_max=None, tol_min=None, tol_max=None,
                 tol_min_action=RAISE_EXCEPTION, tol_max_action=RAISE_EXCEPTION, oob_action=RAISE_EXCEPTION):
        """
        Creates a BoundsChecker instance object.

        @param fill_value: Fill value (aka missing data indicator)
        @type  fill_value: float
        @param valid_min: Minimum valid value
        @type  valid_min: float
        @param valid_max: Maximum valid value
        @type  valid_max: float
        @param tol_min: Minimum tolerable value
        @type  tol_min: float
        @param tol_max: Maximum tolerable value
        @type  tol_max: float
        @param tol_min_action: Action to take if a value falls within the lower tolerance band.
           One of the constants: [ PASS_VALUE, SET_TO_FILL_VALUE, SET_TO_VALID_VALUE, RAISE_EXCEPTION ]
        @type  tol_min_action: int
        @param tol_max_action: Action to take if a value falls within the upper tolerance band.
           One of the constants: [ PASS_VALUE, SET_TO_FILL_VALUE, SET_TO_VALID_VALUE, RAISE_EXCEPTION ]
        @type  tol_max_action: int
        @param oob_action: Action to take if a value is completely out of bounds.
           One of the constants: [ PASS_VALUE, SET_TO_FILL_VALUE, RAISE_EXCEPTION ]
        @type  oob_action: int
        """
        super(BoundsChecker, self).__init__()

        # check input parameters
        assert fill_value is not None, "A fill value must be specified."
        if tol_min is not None and valid_min is not None:
            assert tol_min <= valid_min, "Tolerable minimum is > valid minimum value."
        if tol_max is not None and valid_max is not None:
            assert tol_max >= valid_max, "Tolerable maximum is < valid maximum value."

        self.fill_value = fill_value  # fill value (aka missing value)
        self.valid_min = valid_min  # min valid value
        self.valid_max = valid_max  # max valid value
        # lower tolerance limit (must be <= valid_min)
        self.tol_min = tol_min
        # upper tolerance limit (must be >= valid_max)
        self.tol_max = tol_max
        # action to take if value is less than tol_min
        self.tol_min_action = tol_min_action
        # action to take if value in greater than tol_max
        self.tol_max_action = tol_max_action
        # action to take if value is out of bounds
        self.oob_action = oob_action
        self.stats = dict(total=0, tol_min=0, tol_max=0, oob_min=0, oob_max=0)

    def check_bounds(self, array):
        """
        Check the array of data values against both min and max bounds, adjusting elements in situ if
        appropriate. If required, the scope of the bounds checks can be constrained, from one
        invocation to another, by modifying the values of the instance attributes tol_min_action,
        tol_max_action and oob_action.

        On returning from this method the type and number of reset values can be queried from the
        instance attribute named stats. This is a dictionary whose keys are as follows::

           total   : total # of values reset
           tol_min : # of values reset within the lower tolerance zone
           tol_max : # of values reset within the upper tolerance zone
           oob_min : # of values reset within the lower out-of-bounds zone
           oob_max : # of values reset within the upper out-of-bounds zone

        @param array: A mutable sequence containing the array of values to check. Remember: tuples are
           immutable so don't pass in one of those!
        @type  array: mutable sequence object
        @return: The total number of reset values, which may be 0.
        @raise OutOfBoundsError: Raised if an array value is out of bounds and oob_action is set to
           the constant RAISE_EXCEPTION.
        """
        assert array is not None, "Input array is empty."
        assert isinstance(array, (list, ndarray)), "Input array type is not supported: %s" % type(array)

        self.stats = dict(total=0, tol_min=0, tol_max=0, oob_min=0, oob_max=0)
        if self.tol_min_action == PASS_VALUE and (self.tol_max_action == PASS_VALUE and self.oob_action == PASS_VALUE):
            return 0

        # loop over all array values
        try:
            for i in range(self._get_len(array)):
                if self._is_fill_value(array, i):
                    continue
                x = self._check_value(self._get_value(array, i))
                if x is None:
                    continue
                elif x == self.fill_value:  # float comparison not ideal
                    self._set_to_fill_value(array, i)
                else:
                    self._set_value(array, i, x)
        except OutOfBoundsError:
            raise
        except Exception:
            self.logger.error("Bounds-checking failed at array index position %d" % i)
            raise

        # compute total number of reset values
        total = self.stats['tol_min'] + self.stats['tol_max'] + self.stats['oob_min'] + self.stats['oob_max']
        self.stats['total'] = total
        self.logger.debug("Results of bounds-check: %s" % self.stats)
        return self.stats['total']

    def _check_value(self, value):
        """
        Check the specified input value against min and max bounds, returning an adjusted value if
        appropriate. Otherwise return None.
        """
        adjusted_value = None
        # value is less than valid minimum - do further checks
        if self.valid_min is not None and value < self.valid_min:
            adjusted_value = self._check_min(value)

        # value is greater than valid maximum - do further checks
        elif self.valid_max is not None and value > self.valid_max:
            adjusted_value = self._check_max(value)

        return adjusted_value

    def _check_min(self, value):
        """
        Check the specified input value against the minimum bounds, returning an adjusted value or
        raising an exception as appropriate.
        """
        adjusted_value = None
        # value is within the lower tolerance band
        if self.tol_min is not None and value >= self.tol_min:
            if self.tol_min_action == SET_TO_VALID_VALUE:
                self.stats['tol_min'] += 1
                adjusted_value = self.valid_min
            elif self.tol_min_action == SET_TO_FILL_VALUE:
                self.stats['tol_min'] += 1
                adjusted_value = self.fill_value
            elif self.tol_min_action == RAISE_EXCEPTION:
                raise OutOfBoundsError(value, vmin=self.valid_min)

        # value is less than valid_min and no tolerance band is defined, therefore out-of-bounds
        else:
            if self.oob_action == SET_TO_FILL_VALUE:
                self.stats['oob_min'] += 1
                adjusted_value = self.fill_value
            elif self.oob_action == RAISE_EXCEPTION:
                raise OutOfBoundsError(value, vmin=self.valid_min)
        return adjusted_value

    def _check_max(self, value):
        """
        Check the specified input value against the maximum bounds, returning an adjusted value or
        raising an exception as appropriate.
        """
        adjusted_value = None
        # value is within the upper tolerance band
        if self.tol_max is not None and value <= self.tol_max:
            if self.tol_max_action == SET_TO_VALID_VALUE:
                self.stats['tol_max'] += 1
                adjusted_value = self.valid_max
            elif self.tol_max_action == SET_TO_FILL_VALUE:
                self.stats['tol_max'] += 1
                adjusted_value = self.fill_value
            elif self.tol_max_action == RAISE_EXCEPTION:
                raise OutOfBoundsError(value, vmax=self.valid_max)

        # value is greater than valid_max and no tolerance band is defined, therefore out-of-bounds
        else:
            if self.oob_action == SET_TO_FILL_VALUE:
                self.stats['oob_max'] += 1
                adjusted_value = self.fill_value
            elif self.oob_action == RAISE_EXCEPTION:
                raise OutOfBoundsError(value, vmax=self.valid_max)

        return adjusted_value

    def _get_len(self, array):
        """Return the total number of data values in array."""
        return len(array)

    def _get_value(self, array, i):
        """Get array value at position i"""
        return array[i]

    def _set_value(self, array, i, value):
        """Set array value at position i"""
        array[i] = value

    def _is_fill_value(self, array, i):
        """
        Default method for determining if value is a fill value. Override with a custom method if
        required (e.g. for numpy masked arrays).
        """
        return (array[i] == self.fill_value)

    def _set_to_fill_value(self, array, i):
        """
        Default method for setting array value at index i to the current fill value. Override with a
        custom method if required (e.g. for numpy masked arrays).
        """
        array[i] = self.fill_value

    # deprecated
    def _get_array(self):
        """
        Return the data object attribute containing the array of values to be checked.
        Classes which derive from the current class should override this method if necessary.
        """
        if '_data' in vars(self):
            return self._data
        else:
            return None


class MaskedArrayBoundsChecker0(BoundsChecker):
    """
    Class for checking and, if required, adjusting numpy MaskedArrays.

    NOTE: bounds-checking a numpy MaskedArray object is roughly three times SLOWER (at best) than
    checking an equivalent Python list object. Modifying the loop in the check_bounds method to use
    numpy's ndenumerate() function delivered slightly worse performance.
    """

    def __init__(self, fill_value=UM_MDI, valid_min=None, valid_max=None, tol_min=None, tol_max=None,
                 tol_min_action=RAISE_EXCEPTION, tol_max_action=RAISE_EXCEPTION, oob_action=RAISE_EXCEPTION):

        super(MaskedArrayBoundsChecker0, self).__init__(fill_value, valid_min, valid_max, tol_min, tol_max,
                                                        tol_min_action, tol_max_action, oob_action)

    def _get_len(self, array):
        """
        Return the total number of data values in array.
        """
        return array.size

    def _get_value(self, array, i):
        """
        Get array value at index i.
        """
        return array.data.flat[i]

    def _set_value(self, array, i, value):
        """
        Set array value at index i.
        """
        # automatically turns off mask flag if array[i] == fill_value
        array.flat[i] = value

    def _is_fill_value(self, array, i):
        """
        Return true if array value at index i is equal to the fill value.
        """
        if array.mask is ma.nomask:
            return False
        else:
            return array.mask.flat[i]

    def _set_to_fill_value(self, array, i):
        """
        Set array value at index i to the fill value.
        """
        if array.mask is ma.nomask:
            array.mask = False  # sets entire mask to false
        array.mask.flat[i] = True
        # uncomment the next line to set the actual data value to the fill value as well
        # array.data.flat[i] = self.fill_value


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
