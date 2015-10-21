
import os
import sys
import dill as pickle

args = sys.argv
assert "--pipe" in sys.argv
argidx = sys.argv.index("--pipe")
w = int(args[argidx+1])
r = int(args[argidx+2])
child_write = os.fdopen(w, 'wb')
child_read = os.fdopen(r, 'rb')
queue_out = pickle.Pickler(child_write)
queue_in = pickle.Unpickler(child_read)
f = queue_in.load()
args = queue_in.load()
res = f(*args)
print("Child writing", res)
queue_out.dump("Text written by child...")
queue_out.dump(res)
child_write.flush()

# Clean up
child_read.close()
child_write.close()
print("Child closing")
sys.exit(0)
