#!/usr/bin/env python
import argparse
import os
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('archive_file', help='path to the archive file')


def parse_tar_index(index_file):
    pass


def main():
    args = parser.parse_args()
    index_filename = os.path.abspath(args.archive_file + '.index')

    if not os.path.isfile(index_filename):
        with open(index_filename, 'w') as index_file:
            tar_args = ['tar', '--index-file', index_filename, '-tvf',
                        args.archive_file]
            subprocess.call(tar_args)

    with open(index_filename) as index_file:
        tree = parse_tar_index(index_file)


if __name__ == '__main__':
    main()
