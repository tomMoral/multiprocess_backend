#!/usr/bin/python

import os
import sys
import dill as pickle
from subprocess import Popen

print("The child will write text to a pipe and ")
print("the parent will read the text written by child...")


def test(x, y):
    return x + y

version = sys.version_info[:2]

# Create the subprocess
# and manage the pipes
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
parent_w = os.fdopen(parent_w, 'wb')
queue_out = pickle.Pickler(parent_w)
parent_r = os.fdopen(parent_r, 'rb')
queue_in = pickle.Unpickler(parent_r)
os.close(child_w)
os.close(child_r)

# This is the parent process
queue_out.dump(test)
queue_out.dump((27, 42))
parent_w.flush()
print("Parent sleeping or doing stuff")
#time.sleep(.5)
msg = queue_in.load()
res = queue_in.load()
print(msg)
print("Result =", res)
sys.exit(0)
