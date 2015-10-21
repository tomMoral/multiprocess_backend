import os
import sys
from subprocess import Popen
from multiprocessing.connection import Listener, Client

from . import MP_COMM_CHANNEL
from .communication_channel import CommunicationChannel


version = sys.version_info[:2]
python_bin = '/usr/bin/python' + str(version[0])
if sys.platform == 'win32':
    python_bin = 'c:/python{}{}/python'.format(*version)

if MP_COMM_CHANNEL == 'pipe':

    class Process(object):
        '''Process using a communicator based on posix pipe
        '''
        def __init__(self):
            parent_r, child_w = os.pipe()
            child_r, parent_w = os.pipe()

            f_desc = [str(child_w), str(child_r)]
            if version >= (3, 3):
                if sys.platform == 'win32':
                    # Change to Windwos file handle
                    import msvcrt
                    child_wh = msvcrt.get_osfhandle(child_w)
                    child_rh = msvcrt.get_osfhandle(child_r)
                    os.set_handle_inheritable(child_wh, True)
                    os.set_handle_inheritable(child_rh, True)
                    f_desc = [str(child_wh), str(child_rh)]
                else:
                    os.set_inheritable(child_w, True)
                    os.set_inheritable(child_r, True)
                    f_desc = [str(child_w), str(child_r)]
            elif sys.platform == 'win32':
                # TODO: find a hack??
                # Not yet working
                import msvcrt
                child_wh = msvcrt.get_osfhandle(child_w)
                child_rh = msvcrt.get_osfhandle(child_r)
                f_desc = [str(child_wh), str(child_rh)]

            self.proc = Popen([python_bin, 'spawn_client.py', '--pipe'] +
                              f_desc, close_fds=False)
            self.chan = CommunicationChannel(parent_w, parent_r)
            os.close(child_w)
            os.close(child_r)

        def dump(self, obj):
            self.chan.dump(obj)

        def close(self):
            self.chan.close()

        def load(self):
            return self.chan.load()

elif MP_COMM_CHANNEL == 'conn':
    class Process(object):
        """Procecss with communication based on Listener/Client
        protocol from multiprocessing
        """
        def __init__(self):

            port = 42027
            address_out = ('localhost', port)
            address_in = ('localhost', port+1)
            self.proc = Popen([python_bin, 'spawn_client.py', '--port',
                               str(port)], close_fds=False)

            # Establish connection
            listener = Listener(address_out, authkey=b'testingToms')
            conn_out = listener.accept()
            print('Connection accepted from', listener.last_accepted)
            conn_in = Client(address_in, authkey=b'testingToms')

            self.chan = CommunicationChannel(conn_out, conn_in)

        def dump(self, obj):
            self.chan.dump(obj)

        def close(self):
            self.chan.close()

        def load(self):
            return self.chan.load()
