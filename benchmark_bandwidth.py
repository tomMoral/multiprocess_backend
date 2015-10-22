#!/usr/bin/python
import sys
import numpy as np
from time import time
from process_tom.process_popen import Process


def bench_client(chan):
    size = chan.load()
    t_start = time()
    test = chan.load()
    t_down = time()-t_start
    MB = test.nbytes / 1e6
    print('T_read_up: {:.2f}MB/s'.format(MB/t_down))

    test = None
    test = np.random.randn(size)

    chan.dump(size)
    t_start = time()
    chan.dump(test)
    t_down = time()-t_start
    MB = test.nbytes / 1e6
    print('T_download: {:.2f}MB/s'.format(MB/t_down))

    chan.close()
    print("Child closing")
    sys.exit(0)


def bench_parent(proc, size=500):
    print("Parent sleeping or doing stuff")
    size = size*1e6/8
    test = np.random.randn(size)

    MB = test.nbytes/1e6

    proc.dump(size)
    t_start = time()
    proc.dump(test)
    t_up = time() - t_start
    print('T_upload: {:.2f}MB/s'.format(MB/t_up))
    test = None

    size = proc.load()
    t_start = time()
    test = proc.load()
    t_down = time()-t_start
    MB = test.nbytes / 1e6
    print('T_read_down: {:.2f}MB/s'.format(MB/t_down))

if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser('Benchmark for the subprocess pipe')
    parser.add_argument('--size', type=int, default=500,
                        help='Size of the transfert array in MB')
    args = parser.parse_args()
    # Create the subprocess
    proc = Process(func=bench_client)

    bench_parent(proc, size=args.size)
    proc.close()
    sys.exit(0)
