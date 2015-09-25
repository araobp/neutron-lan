# 2014/3/27
# test.py
#

import cmdutil
import os, sys


# Returns a ping result
def ping(host):
    
    return cmdutil.output_cmd('ping -c4', host)

# Returns args
def echo(*args):
    
    return ' '.join(list(args))

# kwargs test 
def kwargs_test(a=None,b=None,c=None,d=None):

    return (type(a), str(a), type(b), str(b), type(c), str(c), type(d), str(d))
    
# Print to default stdout
def testprint_stdout():
    print >>sys.stdout, "TEST PRINT"

# Print to default stderr
def testprint_stderr():
    print >>sys.stderr, "TEST PRINT"

# Execute a shell command 
def exec_shell(*args):
    os.system(' '.join(list(args))) 
