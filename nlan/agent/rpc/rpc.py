# 2014/4/16
# rpc.py
#

import os

def list():
    d = os.path.join(__n__['agent_dir'], 'rpc')
    l = os.listdir(d)
    result = []
    for f in l:
        if f.endswith('.py'):
            with open(os.path.join(d, f), 'r') as ff:
                source = ff.read().rstrip('\n')
                lines = source.split('\n')
                for line in lines:
                    if line.startswith('def '):
                        line = line.rstrip(':').split(' ',1)[1]
                        func = line.split('(')[0]
                        args = line.split('(')[1].rstrip(')').split(',')
                        args = ' '.join(args)
                        result.append("{}.{} {}".format(f[:-3],func,args))
    return result
