# 2014/5/23
# NLAN RPC utility

from collections import OrderedDict
import nlan

class RPC:

    def __init__(self, module, func, detailed_results=False, target='_ALL'):

        self.target = target
        self.data = OrderedDict()
        self.data['module'] = module
        self.data['func'] = func
        self.detailed_results=False
    
    def __call__(self, *args, **kwargs):

        self.data['args'] = args
        self.data['kwargs'] = kwargs

        results = nlan.main(router=self.target, operation='--rpc', doc=str(self.data), output_stdout=True)
        if self.detailed_results or self.target=='_ALL':
            return results
        elif not self.detailed_results and self.target != '_ALL':
            return results[0]['stdout']

if __name__ == '__main__':

    rpc = RPC(module='test', func='kwargs_test', target='openwrt1')
    result = rpc(1, b='Hello', d='World!')
    print result

    rpc = RPC(module='test', func='echo')
    results = rpc('Hello World!')
    for l in results:
        print l['router'], l['stdout']
    

