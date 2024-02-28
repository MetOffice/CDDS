# (C) British Crown Copyright 2022-2023, Met Office.
# Please see LICENSE.rst for license details.
from cdds.common.plugins.attributes import GlobalAttributes
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cdds.common.request.request import Request


class Cmip6GlobalAttributes(GlobalAttributes):
    """
    Class to store and manage global attributes for CMIP6

    The request given in the init method will be validated if it contains
    all expected information that is need to handle the global attributes.
    """

    def __init__(self, request: 'Request') -> None:
        AttributesValidator.validate_request(request)
        super(Cmip6GlobalAttributes, self).__init__(request)
        self._mip_era = 'CMIP6'

    def further_info_url(self) -> str:
        """
        Returns the further info url according the global attributes values.

        :return: The further info url for CMIP6
        :rtype: str
        """
        root_url = 'https://furtherinfo.es-doc.org'
        further_info_url = '{}/{}.{}.{}.{}.{}.{}'.format(root_url,
                                                         self._mip_era,
                                                         self._request.metadata.institution_id,
                                                         self._request.metadata.model_id,
                                                         self._request.metadata.experiment_id,
                                                         self._request.metadata.sub_experiment_id,
                                                         self._request.metadata.variant_label)
        return further_info_url


class AttributesValidator:
    """
    Class that provides validations for objects relating to CMIP6 attributes
    """

    @classmethod
    def validate_request(cls, request: 'Request') -> None:
        """
        Validates given request. It checks if the request contains all entries
        that are expected. If request is invalid, a ValueError is raised.

        :param request: Request to be validated
        :type request: 'Request'
        :raises ValueError: If request is invalid
        """
        if not request.metadata.institution_id:
            raise ValueError('Request must contain an institution ID')
        if not request.metadata.model_id:
            raise ValueError('Request must contain a model ID')
        if not request.metadata.experiment_id:
            raise ValueError('Request must contain an experiment ID')
        if not request.metadata.sub_experiment_id:
            raise ValueError('Request must contain a sub experiment ID')
        if not request.metadata.variant_label:
            raise ValueError('Request must contain a variant label')
