# (C) British Crown Copyright 2009-2021, Met Office.
# Please see LICENSE.rst for license details.

from mip_convert.config_manager import AbstractConfig

import mip_convert.save.cmor.cmor_lite


# Test changes -- TODO: kerstin remove this comment!!!
class GeneralProject(AbstractConfig):

    # TODO: make the attributes more explicitly public
    GENERAL = 'general'
    OUTDIR = 'outdir'
    OROG_PATH = 'orography_path'
    TABLE_PATH = 'inpath'
    MAPPING_PATH = 'mappings'
    BASE_DATE = 'base_date'

    def __init__(self, config, date_generator):
        super(GeneralProject, self).__init__(date_generator, config=config)

    def _getProperty(self, aproperty):
        """
        read a property from the configuration file
        """
        return self._project_config.get(self.GENERAL, aproperty)

    @property
    def _basetime(self):
        return self._getProperty(self.BASE_DATE)

    @property
    def _baseTime(self):
        return self._getTime(self._basetime)

    @property
    def _outpath(self):
        """
        the output path for this run
        """
        return self._getProperty(self.OUTDIR)

    @property
    def _tablepath(self):
        """
        the location of the MIP tables for this run
        """
        return self._getProperty(self.TABLE_PATH)

    @property
    def _timestep(self):
        return float(self._project_config.get('data_source', 'atm_timestep_in_seconds'))

    @property
    def _orogpath(self):
        """
        the location of the orography file
        """
        return self._getProperty(self.OROG_PATH)

    @property
    def _mappingpath(self):
        """
        the location of the orography file
        """
        return self._getProperty(self.MAPPING_PATH)


class StoppableRequest(object):
    """
    Responsible for supporting turning off of variables if there is a problem
    """
    MESSAGE_FMT = '%s: "%s" for "%s"'
    REQUEST = 'Request'
    FAIL = 'Failed to process'
    SKIP = 'Skip after previous fail'

    writer = None

    def __init__(self, request):
        """
        @param request: the user request to be processed
        @param output: the outputter to use
        """
        self.request = request
        self._active = True

    def has_error(self):
        return not self._active

    def process(self, select_file):
        """
        process the request from selectable file

        the selectable file should have been opened
        """
        if self._active:
            self._do_process(select_file)
        else:
            self._skip_process(select_file)

    def _do_process(self, select_file):
        self.writer.write(self._message_string(self.REQUEST, select_file))

        try:
            self.request.read_and_write(select_file)
        except:
            self._make_inactive(select_file)

    def _make_inactive(self, select_file):
        self._active = False
        self.writer.severe(self._message_string(self.FAIL, select_file))

    def _skip_process(self, select_file):
        self.writer.write(self._message_string(self.SKIP, select_file))

    def _message_string(self, pre_message, select_file):
        return self.MESSAGE_FMT % (pre_message, self.request.output_name(), select_file.pathname)


class StoppableRequestList(object):

    def __init__(self, requests):
        self.orequests = list()
        self._addRequests(requests)

    def process(self, source):
        afile = source.open()
        self._process_file(afile)
        afile.close()

    def has_error(self):
        result = False
        for orequest in self.orequests:
            result = result or orequest.has_error()
        return result

    def _process_file(self, afile):
        for orequest in self.orequests:
            orequest.process(afile)

    def _addRequests(self, requests):
        for request in requests:
            self._addRequest(request)

    def _addRequest(self, request):
        self.orequests.append(StoppableRequest(request))


class StreamRequestProvider(object):
    """
    Provides a list of StoppableRequest for a stream
    """

    def __init__(self, request_provider):
        self.request_provider = request_provider

    def _getRequestsFor(self, stream):
        """
        returns a list of the user requests for a stream
        """
        all_requests = self.request_provider.var_seq()  # multiple calls?
        requests = list()
        for request in all_requests:
            if request.stream == stream:
                requests.append(request)
        return requests

    def forStreamName(self, stream):
        """
        find the requests for the stream
        """
        stream_requests = self._getRequestsFor(stream)
        requests = StoppableRequestList(stream_requests)
        return requests

    def endRequests(self):
        """
        close any resources associated with the requests
        """
        mip_convert.save.cmor.cmor_lite.close()


class LineMessageWriter(object):
    """
    Decorator class to a stream and a logger.

    """

    def __init__(self, stream, logger):
        """
        stream - stream to decorate
        """
        self._stream = stream
        self._logger = logger

    def write(self, message):
        """
        write the message to the stream, appending a new line
        """
        self._stream.write('%s\n' % message)

    def severe(self, message):
        """
        handle a severe message by writing message (with appended new line)
        to a stream and calling logger.error with the message.
        """
        self._logger.error(message, exc_info=True)
        self.write(message)
