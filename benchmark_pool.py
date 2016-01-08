#!/usr/bin/python
import sys
import numpy as np
from time import time
from process_tom.process_popen import ExecProcess

STOP = 27042


def bench_client(chan, info):
    from time import sleep
    out = False
    STOP = chan.load()
    from process_tom.queue import JobQueueOut
    qout = JobQueueOut(chan, info['backend'], info['strat'])
    while not out:
        sleep(.2*idx)
        msg = qout.get()
        out = msg == STOP
        print('{} have msg: '.format(info['idx']), msg,
              'I will go now' if out else '')
    qout.close()


def bench_parent(backend=None, strat='string'):

    # Launch a child process
    proc1 = ExecProcess(func=bench_client, backend=backend,
                        strat=strat)
    proc2 = ExecProcess(func=bench_client, backend=backend,
                        strat=strat)
    proc1.dump(STOP)
    proc2.dump(STOP)

    from process_tom.queue import JobQueueIn
    queue = JobQueueIn([proc2, proc1], backend, strat)

    print("Parent start")

    queue.put('hello')
    for i in range(10):
        queue.put('world')

    queue.put(STOP)
    queue.put(STOP)
    proc1.close()
    proc2.close()
    from time import sleep
    sleep(3)
    print('Parent finished')

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
        bench_parent(backend=args.backend, strat=args.strat)
    except Exception as e:
        print('\n\n'+'-'*80)
        print('Process 0 failed with trace: ')
        print('-'*80)
        import traceback
        print(traceback.format_exc())
        print('\n'+'-'*80)
    sys.exit(0)
