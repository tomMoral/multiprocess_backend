#!/usr/bin/python
import sys
import numpy as np
from time import time
from process_tom.process_popen import ExecProcess
from multiprocessing import Queue, Pipe

STOP = 27042


def bench_client(chan, info):
    out = False
    STOP = chan.load()
    qout = chan.load()
    while not out:
        msg = qout.recv()
        out = msg == STOP
        print('{} have msg: '.format(info['idx']), msg,
              'I will go now' if out else '')
    chan.close()
    print("Child closing")
    sys.exit(0)


def bench_parent(backend=None, strat='string'):

    # Launch a child process
    proc1 = ExecProcess(func=bench_client, backend=backend)
    proc2 = ExecProcess(func=bench_client, backend=backend)
    proc1.dump(STOP)
    proc2.dump(STOP)

    cout, cin = Pipe()
    proc1.dump(cout)
    proc2.dump(cout)

    print("Parent start")

    cout.send('hello')
    for i in range(10):
        cout.send('world')

    cout.send(STOP)
    cout.send(STOP)
    proc1.close()
    proc2.close()

if __name__ == '__main__':
    import multiprocessing

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
    multiprocessing.set_start_method(args.start)

    try:
        bench_parent(args.backend, args.strat)
    except Exception as e:
        print('\n\n'+'-'*80)
        print('Process 0 failed with trace: ')
        print('-'*80)
        import traceback
        print(traceback.format_exc())
        print('\n'+'-'*80)
    sys.exit(0)
