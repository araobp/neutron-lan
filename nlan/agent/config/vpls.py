# 2014/07/06 
# vpls.py
# Note: this module creates "VXLAN-based" virtual private lan service.
#

import cmdutil
import re
from ovsdb import Row, OvsdbRow, search, get_vxlan_ports 
from errors import ModelError


# Add vpls 
def _add_vpls():
	
    cmd = cmdutil.check_cmd
    output_cmd = cmdutil.output_cmd
    cmdp = cmdutil.check_cmdp

    svni = str(_vni_)
    svid = str(_vid)
    br = "br"+svni
    int_br = "int_br"+svni

    if _vid:
        cmdp('ovs-vsctl add-port br-int', int_br, 'tag='+svid, '-- set interface', int_br, 'type=internal')
        cmd('ip link set dev', int_br, 'up')
    if _ip:
        cmd('ip addr add dev', int_br, _ip)

# Delete vpls 
def _delete_vpls():
	
    cmd = cmdutil.check_cmd
    output_cmd = cmdutil.output_cmd

    svni = str(vni_)
    br = "br"+svni
    int_br = "int_br"+svni

    #>>> Deleting VLAN and a linux bridge
    if ip_:
        cmd('ip addr del dev', int_br, ip_)
    if _vid:
        cmd('ip link set dev', int_br, 'down')
        cmd('ovs-vsctl del-port br-int', int_br)


def _flow_entries(ope):
    
        params = {}

        if ope == 'add':
            params['svni'] = str(_vni_)
            params['svid'] = str(_vid_)
        else: # 'delete'
            params['svni'] = str(vni_)
            params['svid'] = str(vid_)

        int_br = "int_br" + params['svni']

        cmd = cmdutil.check_cmd

        if _vid:
            if ope:
                cmd('ovs-ofctl add-flow br-tun table=2,priority=1,tun_id={svni},actions=mod_vlan_vid:{svid},resubmit(,10)'.format(**params))
            else:
                cmd('ovs-ofctl del-flows br-tun table=2,tun_id={svni}'.format(**params))

        if _peers:
            # Broadcast tree for each vni
            output_ports = ''
            vxlan_ports = get_vxlan_ports(_peers)
            for vxlan_port in vxlan_ports:
                output_ports = output_ports+',output:'+vxlan_port
            if ope:
                cmd('ovs-ofctl add-flow br-tun table=21,priority=1,dl_vlan={svid},actions=strip_vlan,set_tunnel:{svni}'.format(**params)+output_ports)
            else:
                cmd('ovs-ofctl del-flow br-tun table=21,dl_vlan={svid}'.format(**params))

### CRUD operations ###
def add():
    if _vni_ and _vid_:
        __n__['logger'].info('Adding a vpls(vlan): ' + str(_vid))
        _add_vpls()
        _flow_entries('add')
    else:
        raise ModelError("requires at least _vni and _vid")

def delete():
    if _vni and _vid_:
        raise ModelError("vid still exists")
    __n__['logger'].info('Deleting a subnet(vlan): ' + str(_vid))
    _flow_entries('delete')
    _delete_vpls()

def update():
    raise ModelError('update not allowed for vni and vid')
