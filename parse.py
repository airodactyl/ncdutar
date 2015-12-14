#!/usr/bin/env python3
"""ncdutar
"""

import argparse
import os
import re
import subprocess
import time
from collections import namedtuple

from pprint import pprint

_version = 0.1

parser = argparse.ArgumentParser()
parser.add_argument('archive_file', help='path to the archive file')

FileAttributes = namedtuple('FileAttributes', ['size', 'is_symlink'])


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
    """Parse a tar-compatible index file, and transform it into a tree-like
    structure, implemented using dicts and a ``FileAttributes`` named tuple.

    The file path ``/usr/bin/python`` with size 66736 bytes will be encoded as
    ``{'usr': {'bin': {'python': <size=66736, is_symlink=False>}}}``, and the
    empty folder path ``/var/log/empty`` will be encoded as ``{'var': {'log':
    {'empty': {}}}}``.

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
            is_symlink = line[0] == 'l'
            leaf = FileAttributes(size=int(size), is_symlink=is_symlink)
            if is_symlink:
                # remove the pointed-to part of the link
                path[-1] = re.findall(r'.* ->', path[-1])[0][:-3]
        else:
            leaf = {}
        insert_into_tree(fs_tree, path, leaf)

    return fs_tree


def flatten_tree(tree):
    """Convert the recursive dict tree structure into a list of filesystem
    objects, one for each node.  The output is a list compatible with the ncdu
    export format.

    :arg tree: a dict of dicts of FileAttributes representing the file system.
    """
    fs_objects = [{"name": "/"}]

    def recurse(node, dir_list):
        """Walk the tree recursively."""
        for key in node:
            if type(node[key]) is FileAttributes:
                dir_list.append({'name': key,
                                 'asize': node[key].size,
                                 'dsize': node[key].size,
                                 'notreg': node[key].is_symlink})
            else:
                dir_list.append([{'name': key}])
                recurse(node[key], dir_list[-1])

    recurse(tree, fs_objects)

    return fs_objects


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
    fs_objects = flatten_tree(tree)

    metadata = {'progname': 'ncdutar',
                'progver': _version,
                'timestamp': int(time.time())}

    pprint([1, 0, metadata, fs_objects])


if __name__ == '__main__':
    main()
