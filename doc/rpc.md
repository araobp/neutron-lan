RPC
===
2014/5/23

NLAN supports RPC with limited capabilites: input arguments and returend data are limited to python basic types and OrderedDict.

<pre>
import rpc

f = rpc.RPC(module='test', func='echo', target='openwrt1')
r = f('Hello World!')
print r
</pre>

