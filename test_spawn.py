#!/usr/bin/python

import os, sys
import time

print("The child will write text to a pipe and ")
print("the parent will read the text written by child...")

# file descriptors r, w for reading and writing
r, w = os.pipe()
os.set_inheritable(w, True)

processid = os.fork()
if processid:
    # This is the parent process
    # Closes file descriptor w
    os.close(w)
    r = os.fdopen(r)
    print("Parent reading")
    time.sleep(.5)
    str = r.read()
    print("text =", str)
    sys.exit(0)
else:
    # This is the child process
    os.close(r)
    print('W: ', w)
    os.execv('/usr/bin/python', ['/usr/bin/python', 'spawn_client.py', str(w)])
    print('No go')
    sys.exit(0)
