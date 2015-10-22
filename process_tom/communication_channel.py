import os
import dill as pickle
from . import MP_COMM_CHANNEL


class CommunicationChannel(object):
    '''Bi directional communication channel
    '''
    if MP_COMM_CHANNEL == 'conn':
        def __init__(self, conn_out, conn_in):
            self.conn_out = conn_out
            self.conn_in = conn_in

        def close(self):
            self.conn_in.close()
            self.conn_out.close()

        def dump(self, obj):
            self.conn_out.send_bytes(pickle.dumps(obj))

        def load(self):
            return pickle.loads(self.conn_in.recv_bytes())
    elif MP_COMM_CHANNEL == 'pipe':
        def __init__(self, fdw, fdr):
            self.fdw = os.fdopen(fdw, 'wb')
            self.fdr = os.fdopen(fdr, 'rb')
            self.queue_out = pickle.Pickler(self.fdw)
            self.queue_in = pickle.Unpickler(self.fdr)

        def close(self):
            self.fdr.close()
            self.fdw.close()

        def dump(self, obj):
            self.queue_out.dump(obj)
            self.fdw.flush()

        def load(self):
            return self.queue_in.load()
    else:
        raise NotImplementedError('Wrong backend')
