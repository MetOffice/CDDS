# (C) British Crown Copyright 2009-2022, Met Office.
# Please see LICENSE.rst for license details.
"""
Module containing classes related to production of variables
by combining stash codes.  The classes responsible for producing
a variable from an input source is called a processor.
"""
import os
import regex as re
import shutil
import tempfile

from mip_convert.common import ObjectWithLogger


class MappingError(Exception):
    pass


class ProcessorError(Exception):
    pass


# TODO: there is an (I think) unecessary 2 way link between Mappings and Processors would be best to remove this.


class Mapping(object):
    """
    Object to represent a mapping and provide a processor for the mapping
    """
    TIMESTEP_UNITS = 's'
    STASH = r"(m\d{2}s\d{2}i\d{3})"
    stash_regex = re.compile(STASH)  # this logic is used elsewhere!

    UNSUPPORTED = (re.compile(r"(\w+)\[level=(\d+)\.?\]"),
                   re.compile(r"(\w+)\[level=sumall\]"),
                   re.compile(r"\(m01s01i235-m01s01i201\)/m01s01i23$"),
                   )

    ALLOWED_POSITIVE = ['up', 'down', '']
    """
    recognised values for positive
    """

    def __init__(self, expression, units, positive, comment=''):
        """
        return a Mapping

        @param expression: expression read from the mapping table
        @param units: units read from the mapping table

        @raises: NotImplementedError if the mapping represented by
                 expression is not supported
        @raises: MappingError if the positive direction is not recognised
        """
        self.expression = expression
        self.units = units
        self.positive = positive.lower()
        self._comment = comment

        self._check_positive()
        self._check_supported()

    def __repr__(self):
        return '%s(%s, %s, %s, %s)' % (self.__class__, self.expression, self.units, self.positive, self._comment)

    def _check_positive(self):
        if self.positive not in self.ALLOWED_POSITIVE:
            raise MappingError('postive %s not recognised' % self.positive)

    def _check_supported(self):
        for regex in self.UNSUPPORTED:
            if regex.match(self.expression):
                raise NotImplementedError('mapping to be implemented: %s' % self.expression)

    def addMetaData(self, var, timestep):
        if self._has_timestep():
            self.stash_history = '%s (TIMESTEP = %f%s)' % (self.expression, timestep, self.TIMESTEP_UNITS)
        else:
            self.stash_history = self.expression
        if not (self._comment == '' or self._comment.isspace()):
            self.comment = self._comment

        var.meta_data(self)

    def variables(self):
        """
        return the list of variables in this mapping
        """
        return self.stash_regex.findall(self.expression)

    def getProcessor(self):
        """
        return the processor for this mapping

        return an EvalProcessor, where calculations are done in memory.
        """
        return EvalProcessor(self)

    def _has_timestep(self):
        return re.search('TIMESTEP', self.expression)

    def __eq__(self, other):  # used in testing
        result = False
        if isinstance(other, self.__class__):
            result = self.expression == other.expression
            result = result and self.units == other.units
            result = result and self.positive == other.positive
            result = result and self._comment == other._comment
        return result


class AbstractProcessor(ObjectWithLogger):
    """
    base class for processors
    """

    def __init__(self, mapping):
        ObjectWithLogger.__init__(self)
        self._mapping = mapping

    def getVariable(self, request, afile):
        """
        return the variable for this processor

        This is a template method sub classes should provide a _process(selected)
        method to be called from here.
        """
        var = self._process(request, afile)
        self._add_meta_data(var, afile)
        return var

    def _add_meta_data(self, var, afile):
        self._mapping.addMetaData(var, afile.timestep)


class EvalProcessor(AbstractProcessor):
    """
    Variable processor that acts as simple wrapper to eval.
    """

    def __init__(self, mapping):
        super(EvalProcessor, self).__init__(mapping)
        if len(self._variables()) == 0:
            raise ProcessorError('no stash in expression "%s"' % mapping.expression)

    def _process(self, request, input_file):
        """
        evaluate the expression on the variables
        """
        arg_dict = self._setupArgs(request, input_file)

        # I think, because of scoping issues, have to do execs in one place
        exec("TIMESTEP = %f" % input_file.timestep)
        for item in arg_dict:
            exec("%s = arg_dict['%s']" % (item, item))
        self.logger.debug("evaluating: '%s'" % self._mapping.expression)
        return eval(self._mapping.expression)

    def _setupArgs(self, request, input_file):
        """
        read the variables into memory and set up argument dictionary
        """
        input_var_dict = {}
        for stashcode in self._variables():
            input_var_dict[stashcode] = input_file.read_selection(stashcode, **request.match_keys())
        return input_var_dict

    def _variables(self):
        return self._mapping.variables()


class NoPathError(Exception):
    pass


class TmpDir(object):
    """
    A temporary directory.  In most cases expect python clean
    up to call the __del__ method and so empty
    """

    def __init__(self):
        self.name = tempfile.mkdtemp()
        self.temp_dir = EmptyableDir(self.name)

    def __del__(self):
        # Started seeing:
        #   Exception exceptions.TypeError: "'NoneType' object is not callable" in
        #   <bound method TmpDir.__del__ of <mip_convert.process.process.TmpDir object at <pointer>>>
        #   ignored after moving convert to mip_convert, so silencing the message.
        if self and self.temp_dir.rmdir:
            try:
                self.temp_dir.rmdir()
            except TypeError:
                pass

    def rmdir(self):
        """
        Explicitly remove the directory and its contents
        """
        self.temp_dir.rmdir()
        self.temp_dir = EmptiedDir()

    def pathname(self, filename):
        """
        return a path in this directory
        """
        return self.temp_dir.pathname(filename)


class EmptyableDir(object):
    def __init__(self, name):
        self._name = name

    def rmdir(self):
        shutil.rmtree(self._name)

    def pathname(self, filename):
        return os.path.join(self._name, filename)


class EmptiedDir(object):
    def rmdir(self):
        pass

    def pathname(self, filename):
        raise NoPathError('directory no longer exists - will not return path in this dir')
