# 2014/3/17
# bridges.py
#

import cmdutil
from ovsdb import Row, OvsdbRow
from errors import ModelError

cmd = cmdutil.check_cmd	
cmdp = cmdutil.check_cmdp

def _add_flow_entries():

    # Flow entries
    r = OvsdbRow('Interface', ('name', 'patch-tun'))
    patch_tun = str(r['ofport'])
    #cmd('ovs-ofctl del-flows br-tun')
    cmd('ovs-ofctl add-flow br-tun', 'table=0,priority=1,in_port='+patch_tun+',actions=resubmit(,1)')
    cmd('ovs-ofctl add-flow br-tun', 'table=0,priority=0,actions=drop')
    cmd('ovs-ofctl add-flow br-tun', 'table=1,priority=0,dl_dst=01:00:00:00:00:00/01:00:00:00:00:00,actions=resubmit(,19)')
    cmd('ovs-ofctl add-flow br-tun', 'table=1,priority=0,dl_dst=00:00:00:00:00:00/01:00:00:00:00:00,actions=resubmit(,20)')
    # Obtains ofport for 'patch-tun' port
    cmd('ovs-ofctl add-flow br-tun', 'table=2,priority=0,actions=drop')
    cmd('ovs-ofctl add-flow br-tun', 'table=3,priority=0,actions=drop')
    cmd('ovs-ofctl add-flow br-tun', 'table=10,priority=1,actions=learn(table=20,hard_timeout=300,priority=1,NXM_OF_VLAN_TCI[0..11],NXM_OF_ETH_DST[]=NXM_OF_ETH_SRC[],load:0->NXM_OF_VLAN_TCI[],load:NXM_NX_TUN_ID[]->NXM_NX_TUN_ID[],output:NXM_OF_IN_PORT[]),output:'+patch_tun)
    cmd('ovs-ofctl add-flow br-tun', 'table=19,priority=0,actions=resubmit(,21)')
    cmd('ovs-ofctl add-flow br-tun', 'table=20,priority=0,actions=resubmit(,21)')
    cmd('ovs-ofctl add-flow br-tun', 'table=21,priority=0,actions=drop')

def add():

    __n__['logger'].info('Adding bridges: br-int and br-tun')

    if _ovs_bridges:
        cmdp('ovs-vsctl add-br br-int')
        cmdp('ovs-vsctl add-br br-tun')
        # Default flows must be cleared.
        cmd('ovs-ofctl del-flows br-tun')
        cmdp('ovs-vsctl add-port br-int patch-int -- set interface patch-int type=patch options:peer=patch-tun')
        cmdp('ovs-vsctl add-port br-tun patch-tun -- set interface patch-tun type=patch options:peer=patch-int')

    if _ovs_bridges and not _controller:
        _add_flow_entries()
    elif _controller and _ovs_bridges_:
        # OpenFlow Controller
        cmd('ovs-ofctl del-flows br-tun')
        cmdp('ovs-vsctl set-controller br-tun '+ _controller)
    elif _controller and not _ovs_bridges_:
        raise ModelError(message='cannot add _controller w/o _ovs_bridges_')


def delete():

    __n__['logger'].info('Deleting bridges: br-int and br-tun')

    if _controller:
        # OpenFlow Controller
        cmd('ovs-vsctl del-controller br-tun')
    if _controller and not _ovs_bridges:
        _add_flow_entries()
    if _ovs_bridges:
        cmd('ovs-ofctl del-flows br-tun')
        cmd('ovs-vsctl del-port br-tun patch-tun')
        cmd('ovs-vsctl del-port br-int patch-int')
        cmd('ovs-vsctl del-br br-tun')
        cmd('ovs-vsctl del-br br-int')

