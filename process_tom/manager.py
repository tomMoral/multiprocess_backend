
from .process_popen import ExecProcess


class Manager(ExecProcess):
    """Manager for a Pool"""
    def __init__(self, name='Manager', **kwargs):
        assert 'func' not in kwargs.keys(), 'Manager doesn\'t take func args'
        super(Manager, self).__init__(
            Manager.run_manager, name=name, idx=0, **kwargs)

    @staticmethod
    def run_manager(chan, infos):
        man = _Manager(chan, infos)
        man.start()

    def create_subprocess(self):
        self.chan.dump(('ADD', None))

    def stop(self):
        self.chan.dump(('STOP', None))


class _Manager(object):
    def __init__(self, chan, infos):
        self.procs = []
        self.chan = chan
        self.backend = infos['backend']
        self.strat = infos['strat']
        self.idx = 0
        self.name = infos['name']

    def start(self):
        print('Hello form Manager {}'.format(self.name))
        out = False
        import signal
        signal.signal(signal.SIGALRM, self.pass_read)
        while not out:
            signal.alarm(1)
            msg = None
            try:
                msg, arg = self.chan.load()
            except Exception:
                pass
            if msg is None:
                print('\n\n\nPass the load??\n\n\n')
            out = msg == 'STOP'
            if msg == 'ADD':
                self.addSupProcess()
        self.end()

    def pass_read(self):
        raise Exception()

    def end(self):
        for p in self.procs:
            p.close()

    def addSupProcess(self):
        name = self.name + '.' + str(self.idx)
        self.idx += 1
        proc = ExecProcess(say_hello, backend=self.backend,
                           strat=self.strat, name=name)
        self.procs += [proc]


def say_hello(chan, infos):
    from time import sleep
    print('Hello from {}'.format(infos['name']))
    sleep(1)
    print('By from {}'.format(infos['name']))
