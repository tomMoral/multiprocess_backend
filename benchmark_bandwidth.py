#!/usr/bin/python
import sys
import numpy as np
import os
from time import time

from benchmark_functions import bench_parent

if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser('Benchmark for the subprocess pipe')
    parser.add_argument('--size', type=int, default=500,
                        help='Size of the transfert array in MB')
    parser.add_argument('--backend', type=str, default=None,
                        help='Select the backend')
    parser.add_argument('--strat', type=str, default='string',
                        help='Select the backend')
    parser.add_argument('--start', type=str, default='forkserver',
                        help='Set the start method for multiprocessing')
    args = parser.parse_args()
    # Create the subprocess

    version = sys.version_info[:2]
    if version >= (3, 0):
        import multiprocessing
        multiprocessing.set_start_method(args.start)

    bench_parent(size=args.size, backend=args.backend,
                 strat=args.strat)
    sys.exit(0)
