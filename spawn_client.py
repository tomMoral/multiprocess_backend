
import os
import sys
import dill as pickle
from communication_channel import CommunicationChannel

args = sys.argv
if "--pipe" in sys.argv:
    argidx = sys.argv.index("--pipe")
    w = int(args[argidx+1])
    r = int(args[argidx+2])
    if sys.platform == 'win32':
        import msvcrt
        w = msvcrt.open_osfhandle(w, os.O_WRONLY)
        r = msvcrt.open_osfhandle(r, os.O_RDONLY)
    chan = CommunicationChannel(w, r)
else:
    argidx = sys.argv.index("--port")
    port = int(args[argidx+1])
    address_in = ('localhost', port)
    address_out = ('localhost', port+1)
    from multiprocessing.connection import Listener, Client
    listener = Listener(address_out, authkey=b'testingToms')
    conn_in = Client(address_in, authkey=b'testingToms')
    conn_out = listener.accept()
    chan = CommunicationChannel(conn_out, conn_in)


f = chan.load()
args = chan.load()
res = f(*args)
print("Child writing", res)
chan.dump("Text written by child...")
chan.dump(res)
#child_write.flush()

# Clean up
chan.close()
print("Child closing")
sys.exit(0)
