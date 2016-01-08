import os
import io
import sys
import dill as pickle
from multiprocessing.connection import Listener, Client


class JobQueueIn(object):
    def __init__(self, procs, backend='pipe', strat='string'):
        self.backend = backend
        self.strat = strat
        print('Start queue IN with info', backend, strat)

        if self.backend == 'pipe':
            _out, _in = os.pipe()
            JobQueueIn._mk_inheritable(_out)
            for p in procs:
                p.dump(_out)
            self.pipe_fd = os.fdopen(_in, 'wb')
            self.conn_out = pickle.Pickler(self.pipe_fd)
            self.put = self._put_pipe

        elif self.backend == 'conn':
            port = 27042
            address_out = ('localhost', port)
            self.listener = Listener(address_out)
            for p in procs:
                p.dump(port)
            self.put = self._put_pipe

    def _put_pipe(self, obj):
        conn_out = self.conn_out
        pipe = self.pipe_fd
        if self.strat == 'string':
            text = pickle.dumps(obj)
            pipe.write(text)
            pipe.flush()
        elif self.strat == 'buff':
            buf = io.BytesIO()
            pickle.Pickler(buf).dump(obj)
            method = 'getbuffer'
            if not hasattr(buf, method):
                method = 'getvalue'
            pipe.write(getattr(buf, method)())
            pipe.flush()
        elif self.strat == 'pipe':
            conn_out.dump(obj)
            pipe.flush()

    def _put_conn(self, obj):
        conn_out = self.listener.accept()
        if self.strat == 'string':
            text = pickle.dumps(obj)
            conn_out.send_bytes(text)
        elif self.strat == 'buff':
            buf = io.BytesIO()
            pickle.Pickler(buf).dump(obj)
            method = 'getbuffer'
            if not hasattr(buf, method):
                method = 'getvalue'
            conn_out.send_bytes(getattr(buf, method)())
        elif self.strat == 'pipe':
            conn_out.send(obj)

    def close(self):
        self.pipe_fd.close()



    @staticmethod
    def _mk_inheritable(fd):
        version = sys.version_info[:2]
        if version >= (3, 3):
            if sys.platform == 'win32':
                # Change to Windwos file handle
                import msvcrt
                fdh = msvcrt.get_osfhandle(fd)
                os.set_handle_inheritable(fdh, True)
                return fdh
            else:
                os.set_inheritable(fd, True)
                return fd
        elif sys.platform == 'win32':
            # TODO: find a hack??
            # Not yet working
            import msvcrt
            fdh = msvcrt.get_osfhandle(fd)
            return fdh
        else:
            return fd


class JobQueueOut(object):
    """Out bound of the job queue"""
    def __init__(self, chan, backend='pipe', strat='string'):
        super(JobQueueOut, self).__init__()
        self.backend = backend
        self.strat = strat

        print('Start queue out with info', backend, strat)

        if self.backend == 'pipe':
            fd = chan.load()
            if sys.platform == 'win32':
                import msvcrt
                fd = msvcrt.open_osfhandle(fd, os.O_WRONLY)
            self.pipe_fd = os.fdopen(fd, 'rb')
            self.conn_in = pickle.Unpickler(self.pipe_fd)
            self.get = self._get_pipe

        elif self.backend == 'conn':
            self.port = chan.load()
            self.address = ('localhost', self.port)
            self.get = self._get_conn

    def _get_conn(self):
        conn_in = Client(self.address, authkey=b'testingToms')
        if self.strat == 'pipe':
            return conn_in.recv()
        buf = io.BytesIO(conn_in.recv_bytes())
        return pickle.load(buf)

    def _get_pipe(self):
        return self.conn_in.load()
