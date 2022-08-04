# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
import os.path
from abc import ABC
from dataclasses import dataclass, asdict, field
from typing import Dict, Any


ROOT_TEST_DIR = '/project/cdds'
ROOT_CMIP6_MIP_TABLES_DIR = '/home/h03/cdds'


@dataclass
class AbstractConfigSection(ABC):
    section_name: ''

    def as_dict(self):
        return {
            k: v for k, v in asdict(self).items() if v and k != 'section_name'
        }


@dataclass
class CommonSection:
    root_test_dir: str = ROOT_TEST_DIR
    root_test_location: str = os.path.join(ROOT_TEST_DIR, 'testdata', 'diagnostics')
    root_ancil_dir: str = os.path.join(ROOT_TEST_DIR, 'etc', 'um_ancil')
    test_location: str = None


@dataclass
class AbstractTestData(ABC):
    project: str = ''
    mip_table: str = ''
    variable: str = ''

    common: CommonSection = None  # add default values here!
    cmor_setup: Dict[str, Any] = None
    cmor_dataset: Dict[str, Any] = None
    request: Dict[str, Any] = None
    global_attributes: Dict[str, Any] = None
    stream: Dict[str, Any] = None
    other: Dict[str, Any] = None


@dataclass
class Cmip6TestData(AbstractTestData):
    project: str = 'CMIP6'

    # add project specific settings for sections


@dataclass
class AriseTestData(AbstractTestData):
    project: str = 'ARISE'

    # add project specific settings for sections


@dataclass
class CordexTestData(AbstractTestData):
    project: str = 'CORDEX'

    # add project specific settings for sections
