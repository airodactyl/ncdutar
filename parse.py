#!/usr/bin/env python3
"""ncdutar
"""

import argparse
import os
import subprocess
import time

from pprint import pprint

parser = argparse.ArgumentParser()
parser.add_argument('archive_file', help='path to the archive file')

_version = 0.1


def insert_into_tree(tree, branches, value):
    """Given a dict tree with a recursive structure such as ``{'a': {'b':
    {}}}``, insert a value at a specific branch in the tree, creating nodes if
    they do not already exist.

    :arg tree: a dict of dicts representing a tree with arbitrary-valued leaves.

    :arg branches: a list of nodes to take when walking the tree.

    :arg value: the value of the leaf to insert after walking the tree.
    """
    node = tree
    for i in range(len(branches) - 1):
        try:
            node = node[branches[i]]
        except KeyError:
            node[branches[i]] = {}
            node = node[branches[i]]
    node[branches[-1]] = value


def read_index_file(index_file):
    """Parse a tar-compatible index file, and transform it into
    a tree-like structure, implemented using dicts.

    The file path ``/usr/bin/python`` with size 66736 bytes will be encoded as
    ``{'usr': {'bin': {'python': 66736}}}``, and the empty folder path
    ``/var/log/empty`` will be encoded as ``{'var': {'log': {'empty': {}}}}``.

    :arg index_file: a file object that points to the tar-compatible index file
    """
    fs_tree = {}

    for line in index_file:
        if not line:
            continue
        line = line.strip()
        _, _, size, _, _, path = line.split(maxsplit=5)
        size = int(size)
        path = path.split('/')
        if path[-1]:
            # not a directory
            node = {'size': int(size),
                    'is_symlink': line[0] == 'l'}
        else:
            node = {}
        insert_into_tree(fs_tree, path, node)

    return fs_tree


def main():
    """The main entry point of the program.
    """
    args = parser.parse_args()
    index_filename = os.path.abspath(args.archive_file + '.index')

    if not os.path.isfile(index_filename):
        tar_args = ['tar', '--index-file', index_filename, '-tvf',
                    args.archive_file]
        subprocess.call(tar_args)

    with open(index_filename) as index_file:
        tree = read_index_file(index_file)
    pprint(tree)
    fs_objects = []

    metadata = {'progname': 'ncdutar',
                'progver': _version,
                'timestamp': int(time.time())}

    return [1, 0, metadata, fs_objects]


if __name__ == '__main__':
    main()
