
import os
import sys
from time import time
import numpy as np
from process_tom.communication_channel import CommunicationChannel

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


func = chan.load()
func(chan)
print("Should not arrive here")
sys.exit(0)
