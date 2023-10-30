# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`cmip6_plus_attributes` module contains the code required to
handle global attributes for CMIP6Plus.
"""
from cdds.common.plugins.attributes import GlobalAttributes
from typing import Dict, Any, Set


class Cmip6PlusGlobalAttributes(GlobalAttributes):
    """
    Class to store and manage global attributes for CMIP6Plus

    The request given in the init method will be validated if it contains
    all expected information that is need to handle the global attributes.
    """

    def __init__(self, request: Dict[str, Any]):
        AttributeValidator.validate_request_keys(request)
        super(Cmip6PlusGlobalAttributes, self).__init__(request)
        self._mip_era = 'CMIP6Plus'

    def further_info_url(self) -> str:
        root_url = 'https://furtherinfo.es-doc.org'
        further_info_url = '{}/{}.{}.{}.{}.{}.{}'.format(root_url,
                                                         self._mip_era,
                                                         self._request["institution_id"],
                                                         self._request["model_id"],
                                                         self._request["experiment_id"],
                                                         self._request["sub_experiment_id"],
                                                         self._request["variant_label"])
        return further_info_url


class AttributeValidator:
    EXPECTED_REQUEST_KEYS: Set[str] = {
        'institution_id', 'model_id', 'experiment_id', 'sub_experiment_id', 'variant_label'
    }

    @classmethod
    def validate_request_keys(cls, request: Dict[str, Any]):
        keys = set(request.keys())
        difference = cls.EXPECTED_REQUEST_KEYS.difference(keys)
        if difference:
            raise ValueError('Request must contain entries for: {}', difference)
