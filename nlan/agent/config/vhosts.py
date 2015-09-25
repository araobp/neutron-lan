# vhosts.py
#

import cmdutil
import re
from ovsdb import Row, OvsdbRow, search, get_vxlan_ports 
from errors import ModelError


def _add_vhosts():
	
    cmd = cmdutil.check_cmd
    output_cmd = cmdutil.output_cmd
    cmdp = cmdutil.check_cmdp

    abcd = _network.split('/')[0]
    l_abcd = abcd.split('.')
    abc = '.'.join(l_abcd[0:3])
    d = l_abcd[3]
    mask = _network.split('/')[1]
    br = "br_"+ abcd 
    #br_ip = '{}.{}'.format(abc, '1')
    br_ip = '{}.{}'.format(abc, d)
    cmd('brctl addbr', br)
    cmd('ip addr add dev', br, '{}/{}'.format(br_ip, mask))
    cmd('ip link set dev', br, 'up')
    for i in range(_vhosts):
        #id_ = str(2+i)
        id_ = str(int(d)+i+1)
        ip = '{}.{}'.format(abc, id_)
        ns = '{}_{}'.format('ns', ip)
        cmd('ip netns add', ns)
        cmd('ip link add', ns, 'type veth peer name temp')
        cmd('ip link set dev temp netns', ns)
        cmd('ip netns exec', ns, 'ip link set dev temp name eth0')
        cmd('brctl addif', br, ns)
        cmd('ip link set dev', ns, 'promisc on')
        cmd('ip link set dev', ns, 'up')
        cmd('ip netns exec', ns, 'ip link set dev eth0 up')
        cmd('ip netns exec', ns, 'ip addr add dev eth0', '{}/{}'.format(ip, mask))
        if not _connect:
            cmd('ip netns exec', ns, 'ip route add default via', br_ip, 'dev eth0')   
    if _connect:
        port = "port" + abc
        # Adds an internal port to OVS bridge (either br-tun or br-int)
        cmdp('ovs-vsctl add-port', _connect, port, '-- set interface', port, 'type=internal')
        # Adds the port to the Linux bridge
        cmd('brctl addif', br, port)

# TODO: this function is incomplete
def _delete_vhosts():
	
    cmd = cmdutil.check_cmd
    output_cmd = cmdutil.output_cmd
    cmdp = cmdutil.check_cmdp

    abcd = _network.split('/')[0]
    abc = '.'.join(abcd.split('.')[0:3])
    br = "br_"+ abcd 
    br_ip = '{}.{}'.format(abc, '1')
    for i in range(_vhosts):
        id_ = str(2+i)
        ip = '{}.{}'.format(abc, id_)
        ns = '{}_{}'.format('ns', ip)
        cmd('ip link set dev', ns, 'down')
        cmd('ip link delete dev', ns)
        cmd('brctl delif', br, ns)
        cmd('ip netns delete', ns)
    cmd('ip link set dev', br, 'down')
    cmd('brctl delbr', br)

### CRUD operations ###
def add():
    if _network and _vhosts:
        __n__['logger'].info('Adding vhosts: ' + str(_network))
        _add_vhosts()
    else:
        raise ModelError("requires both _network and _vhosts")

def delete():
    if _network and _vhosts:
        __n__['logger'].info('Deleting vhosts: ' + str(_network))
        _delete_vhosts()
    else:
        raise ModelError("requires both _network and _vhosts")

def update():
    raise ModelError('update not allowed for this model')
