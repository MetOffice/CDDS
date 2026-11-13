#!/usr/bin/env python3
# (C) British Crown Copyright 2026, Met Office.
# Please see LICENSE.md for license details.

import argparse
import os
import struct
import numpy as np

# PP lookup headers store their integer and real words as big-endian 32-bit values.
DTYPE_INT = ">i4"
DTYPE_REAL = ">f4"
NUM_LOOKUP_INTS = 45
NUM_LOOKUP_REALS = 19
PP_WORD_BYTES = 4
# The header record marker stores its size in bytes: 64 words * 4 bytes = 256 bytes.
HEADER_MARKER_BYTES = (NUM_LOOKUP_INTS + NUM_LOOKUP_REALS) * PP_WORD_BYTES
# Zero-based positions of the integer lookup-header fields used by the repair logic.
PP_INDEX = {
    "LBLREC": 14,  # Payload length (normal data + extra data)
    "LBROW": 17,
    "LBNPT": 18,
    "LBEXT": 19,  # Length of extra data within the payload
    "LBPACK": 20,
}


def arg_parser() -> argparse.Namespace:
    """Parse the directory argument supplied on the command line.

    Returns
    -------
    argparse.Namespace
        Parsed command-line arguments; ``directory`` is the directory to scan.
    """
    parser = argparse.ArgumentParser(description=("A description"))
    parser.add_argument("directory", help="The directory containing the pp files to fix.")

    return parser.parse_args()


def get_files_to_fix(path: str) -> list[str]:
    """Return paths for the immediate entries in ``path``.

    This is a one-level listing: it does not recurse into subdirectories or filter by extension. The caller selects PP
    files before processing them.

    Parameters
    ----------
    path: str
        Directory to list.

    Returns
    -------
    list[str]
        Paths of entries in the directory.
    """
    files = [f"{path}/{file}" for file in os.listdir(path)]

    return files


def repair_pp(input_filename: str, output_filename: str) -> None:
    """Recognise and repair malformed lookup LBLREC/LBEXT headers.

    Fields are read one at a time as sequential records. Their payload bytes are copied unchanged; only ``LBLREC`` and
    ``LBEXT`` may be rewritten, and only when the header matches the specific unpacked-field pattern below.

    Parameters
    ----------
    input_filename: str
        Path to the input PP file.
    output_filename: str
        Path to write the repaired PP file.
    """
    with open(input_filename, "rb") as input_pp, open(output_filename, "wb") as output_pp:
        print(f"Processing {input_filename}")
        field_number = 0
        while True:

            # Each field starts with a 4-byte marker giving the byte size of the following fixed-length lookup header.
            raw_leading_header_marker = input_pp.read(PP_WORD_BYTES)
            if not raw_leading_header_marker:  # If we reach EOF, break
                break
            header_marker_1 = struct.unpack(">L", raw_leading_header_marker)[0]
            if header_marker_1 != HEADER_MARKER_BYTES:
                err_msg = f"Field {field_number}: leading header marker {header_marker_1} != {HEADER_MARKER_BYTES}"
                raise ValueError(err_msg)

            # The 256-byte header consists of 45 int words followed by 19 real words.
            # fromfile advances the input stream as it reads.
            int_headers = np.fromfile(input_pp, dtype=DTYPE_INT, count=NUM_LOOKUP_INTS)
            real_headers = np.fromfile(input_pp, dtype=DTYPE_REAL, count=NUM_LOOKUP_REALS)

            # Fortran-style sequential records repeat the header byte count at the end of the header record.
            raw_trailing_header_marker = input_pp.read(PP_WORD_BYTES)
            header_marker_2 = struct.unpack(">L", raw_trailing_header_marker)[0]
            if header_marker_2 != HEADER_MARKER_BYTES:
                err_msg = f"Field {field_number}: trailing header marker {header_marker_2} != {HEADER_MARKER_BYTES}"
                raise ValueError(err_msg)

            # The next record marker gives the payload size in bytes.
            # PP lookup length fields below are measured in 4-byte words instead.
            raw_data_marker = input_pp.read(PP_WORD_BYTES)
            data_marker = struct.unpack(">L", raw_data_marker)[0]
            data_marker_words = data_marker // 4

            lbrow = int(int_headers[PP_INDEX.get("LBROW")])
            lbnpt = int(int_headers[PP_INDEX.get("LBNPT")])
            lbpack = int(int_headers[PP_INDEX.get("LBPACK")])
            lblrec = int(int_headers[PP_INDEX.get("LBLREC")])
            lbext = int(int_headers[PP_INDEX.get("LBEXT")])

            # Compute the expected number of grid-data words and the known malformed extra-data length for an
            # unpacked field (LBPACK == 0).
            exp_data_words = lbrow * lbnpt
            exp_lbext = 6 * (lbnpt + 1)

            # Use the payload marker to determine whether extra data is actually present, rather than assuming it from
            # the header.
            if lbpack == 0 and lblrec == exp_data_words and lbext == exp_lbext:
                # The payload byte count must convert exactly to PP words to compare with word counts in the header.
                if data_marker % PP_WORD_BYTES:
                    raise ValueError(f"Field {field_number}: data payload length is not word-aligned")

                actual_lbext = data_marker_words - exp_data_words
                # Accept either grid data only or grid data plus the expected extra data
                if actual_lbext not in (0, exp_lbext):
                    raise ValueError(
                        f"Field {field_number}: payload implies LBEXT {actual_lbext}, "
                        f"expected 0 or {exp_lbext}"
                    )

                int_headers[PP_INDEX.get("LBLREC")] = data_marker_words
                int_headers[PP_INDEX.get("LBEXT")] = actual_lbext

            # Re-emit the header record. If the repair condition matched, the integer array now contains corrected
            # LBLREC and LBEXT values. All other header values remain unchanged.
            output_pp.write(struct.pack(">L", header_marker_1))
            int_headers.tofile(output_pp)
            real_headers.tofile(output_pp)
            output_pp.write(raw_trailing_header_marker)
            # Preserve the data record marker and copy exactly that many payload bytes.
            output_pp.write(raw_data_marker)
            # Copy payload unchanged
            payload = input_pp.read(data_marker)
            if len(payload) != data_marker:
                raise ValueError(f"Field {field_number}: incomplete data payload")
            output_pp.write(payload)

            # The data record ends with a marker that must repeat its leading payload byte count.
            # Preserve it after confirming the pair agrees.
            raw_trailing_marker = input_pp.read(PP_WORD_BYTES)
            trailing_marker = struct.unpack(">L", raw_trailing_marker)[0]
            if trailing_marker != data_marker:
                raise ValueError(f"Field {field_number}: data markers disagree: {data_marker} != {trailing_marker}")

            output_pp.write(raw_trailing_marker)
            field_number += 1

    print(f"Wrote {field_number} fields")


def main():
    """Repair each immediate ``.pp`` file in the requested directory."""
    files_to_fix = get_files_to_fix(arg_parser().directory)

    for file in files_to_fix:
        if file.endswith(".pp"):
            # Keep the source intact and place the rewritten copy beside it.
            repair_pp(file, f"{file}.repaired")


if __name__ == "__main__":
    main()
