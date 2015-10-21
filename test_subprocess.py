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
print(sys.version_info[:2])
if version >= (3, 3):
    if sys.platform == 'win32':
        child_w = os.fdopen(child_w)
        child_r = os.fdopen(child_r)
        os.set_handle_inheritable(child_w, True)
        os.set_handle_inheritable(child_r, True)
    else:
        os.set_inheritable(child_w, True)
        os.set_inheritable(child_r, True)
elif sys.platform == 'win':
    import _subprocess
    import msvcrt

    def duplicate(handle, target_process=None, inheritable=False):
        if target_process is None:
            target_process = _subprocess.GetCurrentProcess()
        return _subprocess.DuplicateHandle(
            _subprocess.GetCurrentProcess(), handle, target_process,
            0, inheritable, _subprocess.DUPLICATE_SAME_ACCESS
        ).Detach()
    child_w1 = duplicate(msvcrt.get_osfhandle(child_w), inheritable=True)
    os.close(child_w)
    child_w = child_w1
    child_r1 = duplicate(msvcrt.get_osfhandle(child_r), inheritable=True)
    os.close(child_r)
    child_r = child_r1


python_bin = '/usr/bin/python' + str(version[0])
proc = Popen([python_bin, 'spawn_client.py', '--pipe',
              str(child_w), str(child_r)],
             close_fds=False)
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
