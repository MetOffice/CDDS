import argparse
import json
import os

DEFAULT_INSTALLATION = '/home/h03/cdds/software/miniconda3/envs/cdds-2.4.0/lib/python3.8/site-packages/cdds/common/plugins/cmip6/data/streams/streams_config.json'


def read_variables_file(filepath):
    """
    Reads variables file

    Parameters
    ----------
    filepath : str
        Path to the file

    Returns
    -------
    : dict
        Variables dictionary {(mip_table, var): stream}
    """
    variables = {}
    with open(filepath) as fp:
        for line in fp:
            if ':' in line:
                mip_table_var, stream = line.strip().split(':')
            else:
                mip_table_var = line.strip()
                stream = None
            mip_table, var = mip_table_var.split('/')
            variables[(mip_table, var)] = stream
    return variables


def check_mappings(filepath, variables):
    """
    Parses stream configuration file and updates the variables dictionary

    Parameters
    ----------
    filepath : str
        Path to the streams configuration file
    variables : dict
        Variable dictionary

    Returns
    -------
    : dict
        Variables dictionary {(mip_table, var): stream}
    """
    with open(filepath) as fp:
        stream_mappings = json.load(fp)
        # print(stream_mappings['overrides'])
        for key, stream in variables.items():
            if stream is None:
                try:
                    stream = stream_mappings['overrides'][key[0]][key[1]]
                except KeyError:
                    stream = stream_mappings['default'][key[0]]
                variables[key] = stream
    return variables


def save_mappings(filepath, variables):
    """
    Writes updated variables to a file

    Parameters
    ----------
    filepath : str
        Location where the updated variables file will be written to
    variables : dict
        Variables dictionary {(mip_table, var): stream}
    """
    with open(filepath, 'w') as fp:
        for key, val in variables.items():
            fp.write('{}/{}:{}\n'.format(key[0], key[1], val))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--varfile', help='Path to file with variables to be produced')
    parser.add_argument('--stream_mappings', default=DEFAULT_INSTALLATION)
    parser.add_argument('--outfile', help='New filename. If not provided will replace the --varfile')
    args = parser.parse_args()
    variables = read_variables_file(args.varfile)
    updated_variables = check_mappings(args.stream_mappings, variables)
    if not args.outfile:
        outfile = args.varfile
    else:
        outfile = args.outfile
    save_mappings(outfile, updated_variables)

