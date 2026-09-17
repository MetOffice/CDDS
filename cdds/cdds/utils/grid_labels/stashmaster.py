# (C) British Crown Copyright 2026, Met Office.
# Please see LICENSE.md for license details.
import re
from configparser import ConfigParser
from dataclasses import dataclass


@dataclass
class StashMasterRecord:
    Model: str
    Sectn: str
    Item: str
    Name: str
    Space: str
    Point: str
    Time: str
    Grid: str
    LevelT: str
    LevelF: str
    LevelL: str
    PseudT: str
    PseudF: str
    PseudL: str
    LevCom: str
    Option_Codes: str
    Version_Mask: str
    Halo: str
    DataT: str
    DumpP: str
    PC: str
    Rotate: str
    PPF: str
    USER: str
    LBVC: str
    BLEV: str
    TLEV: str
    RBLEVV: str
    CFLL: str
    CFFF: str


def extract_stash_codes(expression):
    regex = r"m\d*s\d*i\d*"
    return re.findall(regex, expression)


def parse_stashmaster(stashmaster: str) -> list[str]:
    """
    #|Model |Sectn | Item |Name                                |
    #|Space |Point | Time | Grid |LevelT|LevelF|LevelL|PseudT|PseudF|PseudL|LevCom|
    #| Option Codes                   | Version Mask         | Halo |
    #|DataT |DumpP | PC1  PC2  PC3  PC4  PC5  PC6  PC7  PC8  PC9  PCA |
    #|Rotate| PPF  | USER | LBVC | BLEV | TLEV |RBLEVV| CFLL | CFFF |
    """

    regex = r"^1\|(.*)\n^2\|(.*)\n^3\|(.*)\n^4\|(.*)\n^5\|(.*)"

    with open(stashmaster, "r") as fh:
        data = fh.read()

    result = re.findall(regex, data, re.MULTILINE)
    processed_result = []

    for x in result:
        x = "".join(x).split("|")
        x = [x.strip() for x in x]
        processed_result.append(x)

    return processed_result


def parse_stashmaster_meta(section):
    section_name = f"{section}="

    config = ConfigParser()
    config.read("STASHmaster-meta.conf")
    grids = {}
    for section in config.sections():
        if section_name in section:
            print(section)
            print(config.get(section, "help"))
            grids[section.split(section_name)[1]] = config.get(section, "help")
    return grids


def parse_stashmaster_meta_stash(section: str):
    config = ConfigParser()
    config.read("STASHmaster-meta.conf")
    grids = {}

    for section in config.sections():
        if "grid=" in section:
            print(section)
            print(config.get(section, "help"))
            grids[section.split("grid=")[1]] = config.get(section, "help")
    return grids


def to_formatted_stash_code(record: StashMasterRecord) -> str:
    stash = "".join([
        f"m{int(record.Model):02d}",
        f"s{int(record.Sectn):02d}",
        f"i{int(record.Item):03d}",
    ])
    return stash


def stash_records(stashmaster_file) -> dict[str, StashMasterRecord]:
    stash_records = {}
    for x in parse_stashmaster(stashmaster_file):
        if len(x) == 31:
            stash_record = StashMasterRecord(*x[:-1])
            stash_code = to_formatted_stash_code(stash_record)
            stash_records[stash_code] = stash_record
        else:
            print(f"Unexpected number of fields: {len(x)} in record: {x[3]}")
    return stash_records
