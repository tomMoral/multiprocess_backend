import sys
import numpy as np
import os
from time import time


def bench_child(chan, info):
    from time import time
    import numpy as np
    size = chan.load()
    print('Size: ', size*8/1e6)
    t_start = time()
    test = chan.load()
    t_down = time()-t_start
    MB = test.nbytes / 1e6
    print('T_read_up: {:.2f}MB/s'.format(MB/t_down))

    test = None
    test = np.random.randn(size)

    print('Child Dump!')
    chan.dump(size)
    t_start = time()
    chan.dump(test)
    t_down = time()-t_start
    MB = test.nbytes / 1e6
    print('T_download: {:.2f}MB/s'.format(MB/t_down))


def bench_manager(chan, info):
    from time import time
    from benchmark_functions import bench_child

    # Launch a child process
    if type(info) == dict and info['backend'] in ['pipe', 'conn', 'sock']:
        from process_tom.process_popen import ExecProcess
        info.update(dict(idx=1.1, port=6969))
        proc = ExecProcess(func=bench_child, **info)
    else:
        from process_tom.process_multiprocessing import ExecProcess
        proc = ExecProcess(func=bench_child)

    size = chan.load()
    proc.dump(size)
    print('Size: ', size*8/1e6)
    t_start = time()
    test = chan.load()
    proc.dump(test)
    t_down = time()-t_start
    MB = test.nbytes / 1e6
    print('T_read_up: {:.2f}MB/s'.format(MB/t_down))

    size = proc.load()
    chan.dump(size)

    t_start = time()
    print('Manager transfert Get!')
    test = proc.load()
    print('Manager transfert Dump!')
    chan.dump(test)
    t_down = time()-t_start
    MB = test.nbytes / 1e6
    print('T_download: {:.2f}MB/s'.format(MB/t_down))


def bench_parent(size=500, backend='pipe', **kwargs):

    # Launch a child process
    if backend in ['pipe', 'conn', 'sock']:
        from process_tom.process_popen import ExecProcess
        proc = ExecProcess(func=bench_manager, backend=backend,
                           **kwargs)
    elif backend == 'multi':
        from process_tom.process_multiprocessing import ExecProcess
        proc = ExecProcess(func=bench_manager)
    else:
        raise NotImplemented()

    print("Parent started subprocess with backend {}".format(backend))
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
    print('Parent got size')
    t_start = time()
    test = proc.load()
    t_down = time()-t_start
    MB = test.nbytes / 1e6
    print('T_read_down: {:.2f}MB/s'.format(MB/t_down))
