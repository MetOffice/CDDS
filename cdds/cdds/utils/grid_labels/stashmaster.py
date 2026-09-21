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


def parse_stashmaster(stashmaster: str) -> list[list[str]]:
    """ Parse a STASHmaster_A file returning a list of lists, where each inner list represents a STASH record.

    STASH entries are stored as blocks of five lines.

    #|Model |Sectn | Item |Name                                |
    #|Space |Point | Time | Grid |LevelT|LevelF|LevelL|PseudT|PseudF|PseudL|LevCom|
    #| Option Codes                   | Version Mask         | Halo |
    #|DataT |DumpP | PC1  PC2  PC3  PC4  PC5  PC6  PC7  PC8  PC9  PCA |
    #|Rotate| PPF  | USER | LBVC | BLEV | TLEV |RBLEVV| CFLL | CFFF |

    Parameters
    ----------
    stashmaster : str
        Path to a STASHmaster_A file.
    Returns
    -------
    list[list[str]]
        A list of lists, where each inner list represents a STASH record.
    """
    with open(stashmaster, "r") as fh:
        data = fh.read()

    regex = r"^1\|(.*)\n^2\|(.*)\n^3\|(.*)\n^4\|(.*)\n^5\|(.*)"

    matches = re.findall(regex, data, re.MULTILINE)

    stash_records = []

    for match in matches:
        match = "".join(match).split("|")
        match = [x.strip() for x in match]
        stash_records.append(match)

    return stash_records


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


def stash_records(stashmaster_file: str) -> dict[str, StashMasterRecord]:
    stash_records = {}
    for raw_record in parse_stashmaster(stashmaster_file):
        if len(raw_record) == 31:
            stash_record = StashMasterRecord(*raw_record[:-1])
            stash_code = to_formatted_stash_code(stash_record)
            stash_records[stash_code] = stash_record
        else:
            print(f"Unexpected number of fields: {len(raw_record)} in stash record: {raw_record[3]}")
    return stash_records
