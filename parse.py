#!/usr/bin/env python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('file', help='path to the archive file', required=True)

if __name__ == '__main__':
    parser.parse_args()
