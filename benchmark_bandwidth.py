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


def bench_parent(proc):
    print("Parent sleeping or doing stuff")
    N = 1e9/16 # 500MB
    test = np.random.randn(N)

    MB = test.nbytes/1e6

    proc.dump(N)
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

    # Create the subprocess
    proc = Process(func=bench_client)

    bench_parent(proc)
    proc.close()
    sys.exit(0)