#!/usr/bin/env python3
# (C) British Crown Copyright 2026, Met Office.
# Please see LICENSE.md for license details.

import argparse
import os
import struct
import numpy as np

DTYPE_INT = ">i4"  # Extracted directly from mule
DTYPE_REAL = ">f4"  # Extracted directly from mule
NUM_LOOKUP_INTS = 45  # Extracted directly from mule
NUM_LOOKUP_REALS = 19  # Extracted directly from mule
PP_WORD_BYTES = 4  # Extracted directly from mule
HEADER_MARKER_BYTES = (NUM_LOOKUP_INTS + NUM_LOOKUP_REALS) * PP_WORD_BYTES  # 256
PP_INDEX = {
    "LBLREC": 14,  # Payload length (normal data + extra data)
    "LBROW": 17,
    "LBNPT": 18,
    "LBEXT": 19,  # Length of extra data within the payload
    "LBPACK": 20,
}


def arg_parser() -> argparse.Namespace:
    """Creates an argument parser to take user inputs from the command line.

    Returns
    -------
    argparse.Namespace
        The argument parser to handle source file paths.
    """
    parser = argparse.ArgumentParser(description=("A description"))
    parser.add_argument("directory", help="The directory containing the pp files to fix.")

    return parser.parse_args()


def get_files_to_fix(path):
    files = [f"{path}/{file}" for file in os.listdir(path)]

    return files


def repair_pp(input_filename, output_filename):

    with open(input_filename, "rb") as input_pp, open(output_filename, "wb") as output_pp:
        print(f"Processing {input_filename}")
        field_number = 0
        while True:

            # Read leading header marker
            raw_leading_header_marker = input_pp.read(PP_WORD_BYTES)
            if not raw_leading_header_marker:  # This will have no value at EOF, if we reach EOF, break
                break
            header_marker_1 = struct.unpack(">L", raw_leading_header_marker)[0]
            if header_marker_1 != HEADER_MARKER_BYTES:
                err_msg = f"Field {field_number}: leading header marker {header_marker_1} != {HEADER_MARKER_BYTES}"
                raise ValueError(err_msg)

            # Read PP header
            int_headers = np.fromfile(input_pp, dtype=DTYPE_INT, count=NUM_LOOKUP_INTS)
            real_headers = np.fromfile(input_pp, dtype=DTYPE_REAL, count=NUM_LOOKUP_REALS)

            # Read trailing header marker
            raw_trailing_header_marker = input_pp.read(PP_WORD_BYTES)
            header_marker_2 = struct.unpack(">L", raw_trailing_header_marker)[0]
            if header_marker_2 != HEADER_MARKER_BYTES:
                err_msg = f"Field {field_number}: trailing header marker {header_marker_2} != {HEADER_MARKER_BYTES}"
                raise ValueError(err_msg)

            # Read leading data marker
            raw_data_marker = input_pp.read(PP_WORD_BYTES)
            data_marker = struct.unpack(">L", raw_data_marker)[0]
            data_marker_words = data_marker // 4

            lbrow = int(int_headers[PP_INDEX.get("LBROW")])
            lbnpt = int(int_headers[PP_INDEX.get("LBNPT")])
            lbpack = int(int_headers[PP_INDEX.get("LBPACK")])
            lblrec = int(int_headers[PP_INDEX.get("LBLREC")])
            lbext = int(int_headers[PP_INDEX.get("LBEXT")])

            # Identify broken broken fields
            exp_data_words = lbrow * lbnpt
            exp_lbext = 6 * (lbnpt + 1)

            # Correct the known malformed LBEXT pattern from the payload length.
            if lbpack == 0 and lblrec == exp_data_words and lbext == exp_lbext:
                if data_marker % PP_WORD_BYTES:
                    raise ValueError(f"Field {field_number}: data payload length is not word-aligned")

                actual_lbext = data_marker_words - exp_data_words
                if actual_lbext not in (0, exp_lbext):
                    raise ValueError(
                        f"Field {field_number}: payload implies LBEXT {actual_lbext}, "
                        f"expected 0 or {exp_lbext}"
                    )

                int_headers[PP_INDEX.get("LBLREC")] = data_marker_words
                int_headers[PP_INDEX.get("LBEXT")] = actual_lbext

            # Write header to new file
            output_pp.write(struct.pack(">L", header_marker_1))
            int_headers.tofile(output_pp)
            real_headers.tofile(output_pp)
            output_pp.write(raw_trailing_header_marker)
            # Write data marker
            output_pp.write(raw_data_marker)
            # Copy payload unchanged
            payload = input_pp.read(data_marker)
            if len(payload) != data_marker:
                raise ValueError(f"Field {field_number}: incomplete data payload")
            output_pp.write(payload)

            # Copy trailing data marker across to output
            raw_trailing_marker = input_pp.read(PP_WORD_BYTES)
            trailing_marker = struct.unpack(">L", raw_trailing_marker)[0]
            if trailing_marker != data_marker:
                raise ValueError(f"Field {field_number}: data markers disagree: {data_marker} != {trailing_marker}")

            output_pp.write(raw_trailing_marker)
            field_number += 1

    print(f"Wrote {field_number} fields")


def main():
    files_to_fix = get_files_to_fix(arg_parser().directory)

    for file in files_to_fix:
        if file.endswith(".pp"):
            repair_pp(file, f"{file}.repaired")


if __name__ == "__main__":
    main()
