import os
import sys
from subprocess import Popen
from multiprocessing.connection import Listener, Client

from . import MP_COMM_CHANNEL, VALID_BACKEND
from .communication_channel import CommunicationChannels


version = sys.version_info[:2]
python_bin = '/usr/bin/python' + str(version[0])
if sys.platform == 'win32':
    python_bin = 'c:/python{}{}/python'.format(*version)


class ExecProcess(object):
    '''Process using a communicator based on posix pipe
    '''
    idx = 0
    port = 42027

    def __init__(self, func, backend=None, port=None,
                 name=None, idx=None, **kwargs):
        self.communication_backend = backend
        if self.communication_backend is None:
            self.communication_backend = MP_COMM_CHANNEL
        assert self.communication_backend in VALID_BACKEND,\
            "You are not using a valid backend for MP"

        cmd_python = [python_bin, 'spawn_client.py']
        cmd_python += ['--name', name]
        for k, v in kwargs.items():
            cmd_python += ['--'+k, str(v)]

        if self.communication_backend == 'pipe':
            parent_r, child_w = os.pipe()
            child_r, parent_w = os.pipe()

            f_desc = [str(ExecProcess._mk_inheritable(child_w)),
                      str(ExecProcess._mk_inheritable(child_r))]

            self.proc = Popen(cmd_python + ['--pipe'] +
                              f_desc, close_fds=False)
            self.chan = CommunicationChannels(parent_w, parent_r,
                                              backend,  **kwargs)
            os.close(child_w)
            os.close(child_r)
        elif self.communication_backend == 'conn':
            port = port or ExecProcess.port+2
            ExecProcess.port = port
            address_out = ('localhost', port)
            address_in = ('localhost', port+1)
            self.proc = Popen(cmd_python + ['--port', str(port)],
                              close_fds=False)

            # Establish connection
            listener = Listener(address_out, authkey=b'testingToms')
            conn_out = listener.accept()
            print('Connection accepted from', listener.last_accepted)
            conn_in = Client(address_in, authkey=b'testingToms')

            self.chan = CommunicationChannels(conn_out, conn_in,
                                              backend, **kwargs)
        elif self.communication_backend == 'sock':
            import socket
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

            port = port or ExecProcess.port+2
            ExecProcess.port = port
            address_out = ('localhost', 42027)
            address_in = ('localhost', port+1)
            self.proc = Popen(cmd_python + ['--sport', str(port)],
                              close_fds=False)

            # Establish connection

            s.bind(('localhost', port))
            s.listen(1)
            conn_out, a = s.accept()
            print('Connection accepted from', a)
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.connect(('localhost', port+1))
            conn_in = s

            self.chan = CommunicationChannels(conn_out, conn_in,
                                              backend, **kwargs)

        idx = idx if idx is not None else ExecProcess.idx+1
        ExecProcess.idx = idx
        self.chan.dump(int(ExecProcess.idx))
        self.chan.dump(func)
        ExecProcess.idx += 1

    def dump(self, obj):
        self.chan.dump(obj)

    def close(self):
        self.chan.close()
        self.proc.wait()
        print('Good close')

    def load(self):
        return self.chan.load()

    @staticmethod
    def _mk_inheritable(fd):
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
            import _subprocess

            curproc = _subprocess.GetCurrentProcess()
            fdh = msvcrt.get_osfhandle(fd)
            fdh = _subprocess.DuplicateHandle(
                curproc, fdh, curproc, 0,
                True,  # set inheritable FLAG
                _subprocess.DUPLICATE_SAME_ACCESS)
            return fdh
        else:
            return fd
