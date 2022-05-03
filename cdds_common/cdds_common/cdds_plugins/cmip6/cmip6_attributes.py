# (C) British Crown Copyright 2022-2022, Met Office.
# Please see LICENSE.rst for license details.
from cdds_common.cdds_plugins.attributes import GlobalAttributes
from typing import Dict, Any, Set


class Cmip6GlobalAttributes(GlobalAttributes):
    """
    Class to store and manage global attributes for CMIP6

    The request given in the init method will be validated if it contains
    all expected information that is need to handle the global attributes.
    """

    def __init__(self, request: Dict[str, Any]) -> None:
        AttributesValidator.validate_request_keys(request)
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
                                                         self._request["institution_id"],
                                                         self._request["model_id"],
                                                         self._request["experiment_id"],
                                                         self._request["sub_experiment_id"],
                                                         self._request["variant_label"])
        return further_info_url


class AttributesValidator:
    """
    Class that provides validations for objects relating to CMIP6 attributes
    """

    EXPECTED_REQUEST_KEYS: Set[str] = {
        'institution_id', 'model_id', 'experiment_id', 'sub_experiment_id', 'variant_label'
    }

    @classmethod
    def validate_request_keys(cls, request: Dict[str, Any]) -> None:
        """
        Validates given request. It checks if the request contains all entries
        that are expected. If request is invalid, a ValueError is raised.

        :param request: Request to be validated
        :type request: Dict[str, Any]
        :raises ValueError: If request is invalid
        """
        keys = set(request.keys())
        difference = cls.EXPECTED_REQUEST_KEYS.difference(keys)
        if difference:
            raise ValueError('Request must contain entries for: {}', difference)
