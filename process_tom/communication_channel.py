import os
import dill as pickle
from io import BytesIO
from . import MP_COMM_CHANNEL, VALID_BACKEND


class CommunicationChannels(object):
    '''Bi directional communication channel
    '''
    def __init__(self, conn_out, conn_in, backend=None,
                 strat='string'):
        self.communication_backend = backend
        if self.communication_backend is None:
            self.communication_backend = MP_COMM_CHANNEL
        assert self.communication_backend in VALID_BACKEND,\
            "You are not using a valid backend for MP"
        self.strat = strat
        if self.communication_backend in ['conn', 'sock']:
            self.conn_out = conn_out
            self.conn_in = conn_in

            # Permits to get a single close call
            self.pipe_fdw = self.conn_in
            self.pipe_fdr = self.conn_out
        elif self.communication_backend == 'pipe':
            self.pipe_fdw = os.fdopen(conn_out, 'wb')
            self.pipe_fdr = os.fdopen(conn_in, 'rb')
            self.conn_out = pickle.Pickler(self.pipe_fdw)
            self.conn_in = pickle.Unpickler(self.pipe_fdr)

    def close(self):
        self.pipe_fdw = self._close(self.pipe_fdw)
        self.pipe_fdr = self._close(self.pipe_fdr)

    def _close(self, fh):
        if fh is not None:
            fh.close()
            return None

    def dump(self, obj, conn=None, pipe=None):
        conn_out = conn or self.conn_out
        pipe_fdw = pipe or self.pipe_fdw
        if self.strat == 'string':
            text = pickle.dumps(obj)
            self._dump(text, conn_out, pipe_fdw)
        elif self.strat == 'buff':
            buf = BytesIO()
            pickle.Pickler(buf).dump(obj)
            method = 'getbuffer'
            if not hasattr(buf, method):
                method = 'getvalue'
            self._dump(getattr(buf, method)(),
                       conn_out, pipe_fdw)
        elif self.strat == 'pipe':
            if self.communication_backend == 'pipe':
                conn_out.dump(obj)
                pipe_fdw.flush()
            else:
                conn_out.send(obj)

        else:
            raise NotImplementedError('Wrong dump strategy')

    def _dump(self, obj, conn, pipe):
        if self.communication_backend in ['conn', 'sock']:
            conn.send_bytes(obj)
        elif self.communication_backend == 'pipe':
            pipe.write(obj)
            pipe.flush()

    def load(self, conn=None):
        conn_in = conn or self.conn_in
        if self.communication_backend == 'conn':
            if self.strat == 'pipe':
                return conn_in.recv()
            buf = BytesIO(conn_in.recv_bytes())
            return pickle.load(buf)
        elif self.communication_backend == 'pipe':
            return conn_in.load()
