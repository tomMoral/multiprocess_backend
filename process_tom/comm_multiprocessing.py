from multiprocessing import Queue


class CommunicationChannels(object):
    '''Bi directional communication channel
    '''
    def __init__(self):
        self.qin = Queue()
        self.qout = Queue()

    def set_child(self):
        q = self.qin
        self.qin = self.qout
        self.qout = q

    def close(self):
        self.qin.close()
        self.qout.close()

    def dump(self, obj):
        self.qout.put(obj, block=True)
        confirm = self.qin.get()
        assert confirm

    def load(self, conn=None):
        res = self.qin.get()
        self.qout.put(True)
        return res
