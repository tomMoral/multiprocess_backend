from multiprocessing import Process
from .comm_multiprocessing import CommunicationChannels


class ExecProcess(Process):
    '''Process using a communicator based on posix pipe
    '''
    idx = 1

    def __init__(self, func, **kwargs):
        super(ExecProcess, self).__init__(name='test', **kwargs)
        self.chan = CommunicationChannels()
        self.start()
        self.chan.dump(ExecProcess.idx)
        self.chan.dump(func)
        ExecProcess.idx += 1

    def run(self):
        self.chan.set_child()
        idx = self.chan.load()
        print('Started process idx:', idx)
        func = self.chan.load()
        func(self.chan, idx)

    def dump(self, obj):
        self.chan.dump(obj)

    def close(self):
        self.chan.close()

    def load(self):
        return self.chan.load()
