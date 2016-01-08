import os
import sys
import dill as pickle

from process_tom.communication_channel import CommunicationChannels

args = sys.argv
strat = None
info = dict()
if '--strat' in sys.argv:
    stratidx = sys.argv.index("--strat")
    strat = sys.argv[stratidx+1]
info['strat'] = strat
name = 'Process'
if '--name' in sys.argv:
    nameidx = sys.argv.index("--name")
    name = sys.argv[nameidx+1]
info['name'] = name
if "--pipe" in sys.argv:
    argidx = sys.argv.index("--pipe")
    w = int(args[argidx+1])
    r = int(args[argidx+2])
    if sys.platform == 'win32':
        import msvcrt
        w = msvcrt.open_osfhandle(w, os.O_WRONLY)
        r = msvcrt.open_osfhandle(r, os.O_RDONLY)
    chan = CommunicationChannels(w, r, backend='pipe',
                                 strat=strat)
    info['backend'] = 'pipe'
elif '--port' in sys.argv:
    argidx = sys.argv.index("--port")
    port = int(args[argidx+1])
    address_in = ('localhost', port)
    address_out = ('localhost', port+1)
    from multiprocessing.connection import Listener, Client
    listener = Listener(address_out, authkey=b'testingToms')
    conn_in = Client(address_in, authkey=b'testingToms')
    conn_out = listener.accept()
    chan = CommunicationChannels(conn_out, conn_in, backend='conn',
                                 strat=strat)
    info['backend'] = 'conn'

elif '--sport' in sys.argv:
    argidx = sys.argv.index("--sport")
    port = int(args[argidx+1])
    address_in = ('localhost', port)
    address_out = ('localhost', port+1)
    import socket
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    # Establish connection

    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect(address_in)
    conn_in = s
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.bind(address_out)
    s.listen(1)
    conn_out, a = s.accept()

    chan = CommunicationChannels(conn_out, conn_in,
                                 backend='sock', strat=strat)

try:
    idx = chan.load()
    info['idx'] = idx
    info['name'] += str(idx)
    print('Started process idx:', idx)
    func = chan.load()
    print('Start the function')
    func(chan, info)
except Exception as e:
    print('\n\n'+'-'*80)
    print('Process {} failed with trace: '.format(idx))
    print('-'*80)
    import traceback
    print(traceback.format_exc())
    print('\n'+'-'*80)
finally:
    print('Proper close')
    chan.close()
    sys.exit(0)
