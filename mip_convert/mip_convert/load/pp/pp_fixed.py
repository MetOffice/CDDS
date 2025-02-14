# (C) British Crown Copyright 2009-2025, Met Office.
# Please see LICENSE.md for license details.
"""
Some pp header elements are incomplete.  Even if we fix this in the UM, there
is legacy data to deal with.  This module support classes to correct any
pp header elements that are know to have problems.
"""
from mip_convert.common import ObjectWithLogger

ATM_MODEL = 1
OCN_MODEL = 2

PP_CODE_UNSPECIFIED = 0
PP_CODE_HEIGHT = 1
PP_CODE_DEPTH = 2
PP_CODE_SOIL = 6
PP_CODE_SURFACE = 129
PP_CODE_HYBRID_PRESSURE = 9
PP_CODE_HYBRID_HEIGHT = 65
PP_CODE_CANOPY_HEIGHT = 275
PP_CODE_UPPER_PRESSURE_LEVEL = 137
PP_CODE_LOWER_PRESSURE_LEVEL = 138


class NullFixer(object):
    def fix(self, header):
        return header


class HeaderFixer(object):
    """
    Overwrite the attributes in a pp header
    """

    def __init__(self, out_atts):
        """
        @param out_atts: dictionary of attributes to overwrite,
                         keys of the dict are the pp header element names,
                         values are the new values to overwrite
        """
        self.outatts = out_atts

    def fix(self, header):
        new_header = PpCopyHeader(header)
        for (attr, value) in list(self.outatts.items()):
            if attr == 'lbvc':
                if not self.soil_level_metres(new_header.lbvc, new_header.lbsrce):
                    setattr(new_header, attr, value)
            else:
                setattr(new_header, attr, value)
        return new_header

    def soil_level_metres(self, lbvc, lbsrce):
        """
        Versions before 9.3 do not report soil levels in metres

        Examples
        --------
        >>> obj = HeaderFixer(None)
        >>> lbvc = 6
        >>> lbsrce = '09031111'
        >>> obj.soil_level_metres(lbvc, lbsrce)
        True

        >>> lbvc = 6
        >>> lbsrce = '09011111'
        >>> obj.soil_level_metres(lbvc, lbsrce)
        False
        """
        return lbvc == 6 and int(lbsrce) >= 9031111


class RadiationBottomMatcher(object):
    """
    Use this to fix the lower levels for radiation diagnostics.  This
    is needed because the radiation `half level` diagnostics look
    like they are on HadGEM2-ES rho levels, but they are not, they are
    really on their own levels.  The radiation half levels coincide with
    the rho levels, except at the ground.
    """

    def __init__(self, match_val, tol, sections):
        self._match_val = match_val
        self._tol = tol
        self._sects = sections
        # not great hard coded... but done in rush
        self._lbvc = PP_CODE_HYBRID_HEIGHT

    def match(self, header):
        result = True
        result = result and self._match_hybrid_height(header)
        result = result and self._match_real(header)
        result = result and self._match_on_section(header)
        return result

    def _match_hybrid_height(self, header):
        return header.lbvc == self._lbvc

    def _match_real(self, header):
        return abs(self._match_val - header.blev) < self._tol

    def _match_on_section(self, header):
        return header.lbuser4 // 1000 in self._sects


# isn't similar logic used in pp match? elimate duplicates
class Matcher(object):
    """
    Match Header based on selected attributes
    """

    def __init__(self, match_atts):
        """
        @param match_atts: dictionary of attributes to match
                           keys of the dict are the pp header element names,
                           values are the values to match
        """
        self.match_atts = match_atts

    def match(self, header):
        result = True
        for attr, value in list(self.match_atts.items()):
            if getattr(header, attr) != value:
                result = False
                break
        return result


class CompositeFixer(object):
    """
    Simple factory of header fixers

    Header fixers will fix (in this implementation) the
    vertical levels in the pp headers - e.g to add physically
    dimensioned levels where the UM has been unable to.
    """

    def __init__(self):
        self.matchers = list()

    def _get_fixer(self, header):
        result = NullFixer()
        for (fixer, matcher) in self.matchers:
            if matcher.match(header):
                result = fixer
                break
        return result

    def fix(self, header):
        """
        returns a fixed version of the header
        """
        fixer = self._get_fixer(header)
        return fixer.fix(header)

    def addStashCodes(self, lbuser4s, match_atts, fix_atts):
        """
        add a list of stash codes that share the same fix
          lbuser4s - the stash codes to fix
          lbvc     - the vertical coordinate type in the input header
          fixer    - an object with a fix method to fix the header
        """
        for lbuser4 in lbuser4s:
            self._addAtmosFixer(lbuser4, match_atts, fix_atts)

    def addModelStashCodes(self, lbuser7, lbuser4s, match_atts, fix_atts):
        for lbuser4 in lbuser4s:
            self.addModelStashCode(lbuser7, lbuser4, match_atts, fix_atts)

    def addModelStashCode(self, lbuser7, lbuser4, match_atts, fix_atts):
        rmatch_atts = self._set_atts(match_atts, lbuser4, lbuser7)
        self.add(HeaderFixer(fix_atts), Matcher(rmatch_atts))

    def _set_atts(self, match_atts, lbuser4, lbuser7):
        import copy
        rmatch_atts = copy.copy(match_atts)
        rmatch_atts['lbuser7'] = lbuser7
        rmatch_atts['lbuser4'] = lbuser4
        return rmatch_atts

    def _addAtmosFixer(self, lbuser4, match_atts, fix_atts):
        """
        adds an atmospheric stash code to the known fixable headers
        """
        rmatch_atts = self._set_atts(match_atts, lbuser4, ATM_MODEL)
        self.add(HeaderFixer(fix_atts), Matcher(rmatch_atts))

    def add(self, fix, match):
        self.matchers.append((fix, match))


# build the in memory FixerFactory
premade_fixer = CompositeFixer()

premade_fixer.addStashCodes((3225, 3226, 3227, 3249, 3463),
                            {'lbvc': PP_CODE_HEIGHT, 'blev': -1},
                            {'blev': 10})

premade_fixer.addStashCodes((3236, 3237, 3245),
                            {'lbvc': PP_CODE_HEIGHT, 'blev': -1},
                            {'blev': 1.5})

# radiation diagnostics on rho-look a like
premade_fixer.add(HeaderFixer(
    {'blev': 0., 'bhlev': 1}), RadiationBottomMatcher(10., 0.01, (1, 2)))

# TODO: this should be simplifiable - there is a method to
# add stashcodes over a number of levels.
premade_fixer.addStashCodes((8223, 8225, 8230),
                            {'lbvc': PP_CODE_SOIL, 'blev': 1.},
                            {'lbvc': PP_CODE_DEPTH,
                             'blev': 0.05, 'brsvd1': 0, 'brlev': 0.1})

premade_fixer.addStashCodes((8223, 8225, 8230),
                            {'lbvc': PP_CODE_SOIL, 'blev': 2.},
                            {'lbvc': PP_CODE_DEPTH,
                             'blev': 0.225, 'brsvd1': 0.1, 'brlev': 0.35})

premade_fixer.addStashCodes((8223, 8225, 8230),
                            {'lbvc': PP_CODE_SOIL, 'blev': 3.},
                            {'lbvc': PP_CODE_DEPTH,
                             'blev': 0.675, 'brsvd1': 0.35, 'brlev': 1.0})

premade_fixer.addStashCodes((8223, 8225, 8230),
                            {'lbvc': PP_CODE_SOIL, 'blev': 4.},
                            {'lbvc': PP_CODE_DEPTH,
                             'blev': 2.0, 'brsvd1': 1.0, 'brlev': 3.0})

premade_fixer.addStashCodes((3309, 3310),
                            {'lbvc': PP_CODE_SURFACE, 'blev': 0},
                            {'lbvc': PP_CODE_UNSPECIFIED, 'blev': -1})

premade_fixer.addStashCodes((2261,),
                            {'lbvc': PP_CODE_HYBRID_PRESSURE},
                            {'lbvc': PP_CODE_HYBRID_HEIGHT})

# for mappings prveg, evspblveg.  This was the easiest thing to do at time
#  as it means do not have to worry about subtraction rules and allowed
#  level type subtractions.
premade_fixer.addStashCodes((5216,),
                            {'lbvc': PP_CODE_SURFACE, 'blev': 0},
                            {'lbvc': PP_CODE_UNSPECIFIED, 'blev': -1})

premade_fixer.addStashCodes((3297, 8233),
                            {'lbvc': PP_CODE_CANOPY_HEIGHT, 'blev': -1},
                            {'lbvc': PP_CODE_UNSPECIFIED, 'blev': -1})

premade_fixer.addModelStashCodes(OCN_MODEL, (30253, 30406),
                                 {'lbvc': PP_CODE_DEPTH,
                                  'blev': 5.0},
                                 {'brlev': 10.0}
                                 )
premade_fixer.addModelStashCodes(OCN_MODEL, (30208,),
                                 {'lbvc': PP_CODE_UNSPECIFIED, 'blev': -1.0},
                                 {'lbvc': PP_CODE_DEPTH,
                                  'blev': 5., 'brsvd1': 0., 'brlev': 10.}
                                 )

# Reset LBVC for 5,208 from 137 to 0.
premade_fixer.addStashCodes((5208,),
                            {'lbvc': PP_CODE_UPPER_PRESSURE_LEVEL},
                            {'lbvc': PP_CODE_UNSPECIFIED})

# Reset LBVC for 5,222 from 138 to 0.
premade_fixer.addStashCodes((5222,),
                            {'lbvc': PP_CODE_LOWER_PRESSURE_LEVEL},
                            {'lbvc': PP_CODE_UNSPECIFIED})

# Fix BLEV for convection indicator mask (5,269).
premade_fixer.addStashCodes((5269,),
                            {'lbvc': PP_CODE_UNSPECIFIED, 'blev': -1.0},
                            {'blev': 0.0})

# this one isn't really a fix, it puts in the logic that the bottom hybrid
# sigma pressure level is the surface
premade_fixer.addStashCodes((3217, 3219, 3220, 3223),
                            {'lbvc': PP_CODE_HYBRID_PRESSURE, 'blev': 1.0},
                            {'lbvc': PP_CODE_HEIGHT, 'blev': 0.0},
                            )


class PpCopyHeader(object):
    """
    very lightweight class that acts as a copy of a pp_header
    this allows the pp_header to have read only attributes, but allow
    the fixers to act in place.
    """

    def __init__(self, to_copy):
        for att in to_copy.getAttNames():
            setattr(self, att, getattr(to_copy, att))


class PpFixedFile(ObjectWithLogger):
    """
    class to do some munging of pp-headers to fix any quirks that
    may be strays from a 'standard'.
    """

    def __init__(self, pp_base_file):
        """
        the pp_base_file is the input file to be fixed
        """
        super(self.__class__, self).__init__()
        self.base_file = pp_base_file
        self.fixer = premade_fixer
        self.headers = []
        self._make_headers()

    def _make_headers(self):
        """
        fix all the headers in the pp_base_file
        """
        for header in self.base_file.headers:
            self.headers.append(self.fixer.fix(header))

    @property
    def pathname(self):
        """
        return the path name of the base file
        """
        return self.base_file.filename

    def loadField(self, pos):
        """
        return data for field at pos in the base file
        """
        # should I hide this interface?
        return self.base_file.loadField(pos)

    def unloadField(self, pos):
        """
        unload data for field at pos in the base file
        """
        self.base_file.unloadField(pos)

    def getExtraDataVectors(self, pos):
        """
        return the extra data vectors as a dictionary
        """
        return self.base_file.getExtraDataVectors(pos)

    def close(self):
        """
        close the pp file
        """
        self.logger.debug('closing')
        self.base_file.close()
        self.headers = []
