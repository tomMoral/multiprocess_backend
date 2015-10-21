#!/usr/bin/python

import os
import sys
import dill as pickle
from subprocess import Popen
from communication_channel import CommunicationChannel

print("The child will write text to a pipe and ")
print("the parent will read the text written by child...")


def test(x, y):
    return x + y

version = sys.version_info[:2]

# Create the subprocess
# and manage the pipes
if ('MP_COMM_CHANNEL' in os.environ.keys() and
        os.environ['MP_COMM_CHANNEL'] == 'pipe'):
    parent_r, child_w = os.pipe()
    child_r, parent_w = os.pipe()

    python_bin = '/usr/bin/python' + str(version[0])
    f_desc = [str(child_w), str(child_r)]
    if version >= (3, 3):
        if sys.platform == 'win32':
            # Change to Windwos file handle
            import msvcrt
            child_wh = msvcrt.get_osfhandle(child_w)
            child_rh = msvcrt.get_osfhandle(child_r)
            os.set_handle_inheritable(child_wh, True)
            os.set_handle_inheritable(child_rh, True)
            python_bin = 'c:/python{}{}/python'.format(*version)
            f_desc = [str(child_wh), str(child_rh)]
        else:
            os.set_inheritable(child_w, True)
            os.set_inheritable(child_r, True)
            f_desc = [str(child_w), str(child_r)]
    elif sys.platform == 'win32':
        import msvcrt
        child_wh = msvcrt.get_osfhandle(child_w)
        child_rh = msvcrt.get_osfhandle(child_r)
        python_bin = 'c:/python{}{}/python'.format(*version)
        f_desc = [str(child_wh), str(child_rh)]

    proc = Popen([python_bin, 'spawn_client.py', '--pipe'] +
                 f_desc, close_fds=False)
    os.close(child_w)
    os.close(child_r)
    chan = CommunicationChannel(parent_w, parent_r)
elif ('MP_COMM_CHANNEL' in os.environ.keys() and
        os.environ['MP_COMM_CHANNEL'] == 'conn'):
    from multiprocessing.connection import Listener, Client

    python_bin = '/usr/bin/python' + str(version[0])
    port = 42027
    address_out = ('localhost', port)
    address_in = ('localhost', port+1)
    proc = Popen([python_bin, 'spawn_client.py', '--port'] +
                 [str(port)], close_fds=False)
    listener = Listener(address_out, authkey=b'testingToms')
    conn_out = listener.accept()
    print('Connection accepted from', listener.last_accepted)
    conn_in = Client(address_in, authkey=b'testingToms')

    chan = CommunicationChannel(conn_out, conn_in)
else:
    raise NotImplementedError('No such connector')

# This is the parent process
chan.dump(test)
chan.dump((27, 42))
#parent_w.flush()
print("Parent sleeping or doing stuff")
#time.sleep(.5)
msg = chan.load()
res = chan.load()
print(msg)
print("Result =", res)
sys.exit(0)
