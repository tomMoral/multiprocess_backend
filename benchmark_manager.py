#!/usr/bin/python
import sys
from time import sleep
from process_tom.manager import Manager


def start_manager(backend='pipe', **kwargs):

    # Launch a child process
    proc = Manager(backend=backend,
                   **kwargs)
    for i in range(10):
        proc.create_subprocess()

    sleep(3)
    print('STOP')
    proc.stop()

    print("Parent started subprocess with backend {}".format(backend))
    proc.close()

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

    start_manager(backend=args.backend,
                  strat=args.strat)
    sys.exit(0)
