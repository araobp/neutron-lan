# Jul 2014 
# ptn_nodes.py
#

import cmdutil
from ovsdb import Row, OvsdbRow, nlan_search
from errors import ModelError

cmd = cmdutil.check_cmd	
cmdp = cmdutil.check_cmdp

def _add_flow_entries(br_tun, patch_tun):

    # Flow entries
    r = OvsdbRow('Interface', ('name', patch_tun))
    patch_tun_num = str(r['ofport'])
    cmd('ovs-ofctl add-flow', br_tun, 'table=0,priority=1,in_port='+patch_tun_num+',actions=resubmit(,1)')
    cmd('ovs-ofctl add-flow', br_tun, 'table=0,priority=0,actions=drop')
    cmd('ovs-ofctl add-flow', br_tun, 'table=1,priority=0,dl_dst=01:00:00:00:00:00/01:00:00:00:00:00,actions=resubmit(,19)')
    cmd('ovs-ofctl add-flow', br_tun, 'table=1,priority=0,dl_dst=00:00:00:00:00:00/01:00:00:00:00:00,actions=resubmit(,20)')
    # Obtains ofport for 'patch-tun' port
    cmd('ovs-ofctl add-flow', br_tun, 'table=2,priority=0,actions=drop')
    cmd('ovs-ofctl add-flow', br_tun, 'table=3,priority=0,actions=drop')
    cmd('ovs-ofctl add-flow', br_tun, 'table=10,priority=1,actions=learn(table=20,hard_timeout=300,priority=1,NXM_OF_VLAN_TCI[0..11],NXM_OF_ETH_DST[]=NXM_OF_ETH_SRC[],load:0->NXM_OF_VLAN_TCI[],load:NXM_NX_TUN_ID[]->NXM_NX_TUN_ID[],output:NXM_OF_IN_PORT[]),output:'+patch_tun_num)
    cmd('ovs-ofctl add-flow', br_tun, 'table=19,priority=0,actions=resubmit(,21)')
    cmd('ovs-ofctl add-flow', br_tun, 'table=20,priority=0,actions=resubmit(,21)')
    cmd('ovs-ofctl add-flow', br_tun, 'table=21,priority=0,actions=drop')

def add():

    br_tun = _nodes['ptn']
    br_int = _nodes['l2sw']
    patch_tun = 'patch-tun_' + br_tun 
    patch_int = 'patch-int_' + br_int 

    __n__['logger'].info('Adding bridges: {} and {}'.format(br_tun, br_int))

    cmdp('ovs-vsctl add-br', br_int)
    cmdp('ovs-vsctl add-br', br_tun)
    # Default flows must be cleared.
    cmd('ovs-ofctl del-flows',  br_tun)
    cmdp('ovs-vsctl add-port {0} {1} -- set interface {1} type=patch options:peer={2}'.format(br_int, patch_int, patch_tun))
    cmdp('ovs-vsctl add-port {0} {1} -- set interface {1} type=patch options:peer={2}'.format(br_tun, patch_tun, patch_int))

    if _controller:  # OpenFlow Controller
        cmd('ovs-ofctl del-flows', br_tun)  # Clears all the existing flows in the bridge
        cmdp('ovs-vsctl set-controller {0} {1}'.format(br_tun, _controller))  # Sets OFC's IP address and port number
        cmdp('ovs-vsctl set bridge {} protocols=OpenFlow10,OpenFlow12,OpenFlow13'.format(br_tun))  # Supports OpenFlow ver 1.0, 1.2 and 1.3
    else: 
        cmdp('ovs-vsctl set-fail-mode {} secure'.format(br_tun))  # Disables self mac learning
        _add_flow_entries(br_tun, patch_tun)

# TODO: delete/update are imcomplete.
def delete():

    br_tun = _nodes['ptn']
    br_int = _nodes['l2sw']
    patch_tun = 'patch-tun_' + br_tun 
    patch_int = 'patch-int_' + br_int 

    __n__['logger'].info('Deleting bridges: {} and {}'.format(br_tun, br_int))

    cmd('ovs-ofctl del-flows', br_tun)
    cmd('ovs-vsctl del-port', br_tun, patch_tun)
    cmd('ovs-vsctl del-port', br_int, patch_int)
    cmd('ovs-vsctl del-br', br_tun)
    cmd('ovs-vsctl del-br', br_int)

# This function is for other modules to obtain 'nodes' 
def get_nodes(_id):

    return nlan_search('ptn_nodes', ['nodes'], 'id', _id)[0]['nodes']

