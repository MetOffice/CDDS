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


def correct_lbext(int_headers, pp_file):
    """This mirrors what happens in the original fix, however this introduces errors in EOF data marker checks."""
    lbext = int_headers[PP_INDEX.get("LBEXT")]
    lblrec = int_headers[PP_INDEX.get("LBLREC")]
    lbnpt = int_headers[PP_INDEX.get("LBNPT")]

    if lbext > 0:
        pp_file.seek((lblrec - lbext) * PP_WORD_BYTES, 1)
        start = pp_file.tell()
        vectors = {}
        ext_consumed = 0
        to_try = [3, 4, 5, 6, 7, 8]
        to_try_count = 0
        while pp_file.tell() - start < lbext * PP_WORD_BYTES:
            vector_code = np.fromfile(pp_file, ">i4", 1)[0]
            if vector_code == 0:
                vector_code = lbnpt * 1000 + to_try[to_try_count]
                to_try_count += 1

            vector_points = vector_code // 1000
            vector_type = vector_code % 1000
            vectors[vector_type] = (np.fromfile(pp_file, ">f4", vector_points))
            ext_consumed += vector_points

        extra_len = (len(vectors.keys()) + sum([len(arr) for arr in vectors.values()]))
        int_headers[PP_INDEX.get("LBEXT")] = extra_len
        int_headers[PP_INDEX.get("LBLREC")] += extra_len

    else:
        int_headers[PP_INDEX.get("LBEXT")] = 0

    return int_headers


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
                raise ValueError(f"Field {field_number}: leading header marker {header_marker_1} != {HEADER_MARKER_BYTES}")

            # Read PP header
            int_headers = np.fromfile(input_pp, dtype=DTYPE_INT, count=NUM_LOOKUP_INTS)
            real_headers = np.fromfile(input_pp, dtype=DTYPE_REAL, count=NUM_LOOKUP_REALS)

            # Read trailing header marker
            raw_trailing_header_marker = input_pp.read(PP_WORD_BYTES)
            header_marker_2 = struct.unpack(">L", raw_trailing_header_marker)[0]
            if header_marker_2 != HEADER_MARKER_BYTES:
                raise ValueError(f"Field {field_number}: trailing header marker {header_marker_2} != {HEADER_MARKER_BYTES}")

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

            # Fix lbext header and payload
            if lbpack == 0 and lblrec == exp_data_words and data_marker_words == lblrec and lbext == exp_lbext:
                print(f"Field {field_number}: LBEXT {lbext} -> 0")
                int_headers[PP_INDEX.get("LBEXT")] = 0  # Set lbext = 0
            #correct_lbext(int_headers, input_pp)

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
