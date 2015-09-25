# Jul 2014 
# ptn_links.py
#

import cmdutil
from ovsdb import Row, get_vxlan_ports
from errors import ModelError
import ptn_nodes 

cmd = cmdutil.check_cmd	
cmdp = cmdutil.check_cmdp	

def add():

    nodes = ptn_nodes.get_nodes(_id)
    br_tun = nodes['ptn']
    br_int = nodes['l2sw']

    if not _local_ip_:
        raise ModelError('"_local_ip_" is mandatory')
    if _remote_ips:
        for remote_ip in _remote_ips:
            inf = ''.join([num.zfill(3) for num in remote_ip.split('.')])
            __n__['logger'].info('Adding a VXLAN tunnel: ' + inf)
            cmdp('ovs-vsctl add-port', br_tun, inf, '-- set interface', inf, 'type=vxlan options:in_key=flow', 'options:local_ip='+_local_ip, 'options:out_key=flow', 'options:remote_ip='+remote_ip)

        vxlan_ports = get_vxlan_ports()
        for vxlan_port in vxlan_ports:
            cmd('ovs-ofctl add-flow', br_tun, 'table=0,priority=1,in_port='+vxlan_port+',actions=resubmit(,2)')


def delete():
    
    nodes = ptn_nodes.get_nodes(_id)
    br_tun = nodes['ptn']
    br_int = nodes['l2sw']

    if _remote_ips:
        vxlan_ports = get_vxlan_ports()
        for vxlan_port in vxlan_ports:
            cmd('ovs-ofctl del-flows', br_tun, 'table=0,in_port={vxlan_port}'.format(vxlan_port=vxlan_port))
        
        for remote_ip in _remote_ips:
            inf = ''.join([num.zfill(3) for num in remote_ip.split('.')])
            __n__['logger'].info('Deleting a VXLAN tunnel: ' + inf)
            cmd('ovs-vsctl del-port', br_tun, inf)
    
    if _local_ip:
        # All remote IPs must be deleted before deleting local IP
        if remote_ips_:
            if not (set(_remote_ips) == set(remote_ips_)):
                raise ModelError('"local_ip" cannot be deleted') 


def update():

    nodes = ptn_nodes.get_nodes(_id)
    br_tun = nodes['ptn']
    br_int = nodes['l2sw']

    if _local_ip or _remote_ips:
        # Delete all interfaces and flows 
        vxlan_ports = get_vxlan_ports()
        for vxlan_port in vxlan_ports:
            cmd('ovs-ofctl del-flows', br_tun, 'table=0,in_port={vxlan_port}'.format(vxlan_port=vxlan_port))
        
        for remote_ip in remote_ips_:
            #inf = 'vxlan_' + remote_ip
            inf = ''.join([num.zfill(3) for num in remote_ip.split('.')])
            __n__['logger'].info('Adding a VXLAN tunnel: ' + inf)
            cmd('ovs-vsctl del-port', br_tun, inf)
       
        # Add those interfaces and flows again to change the local IP address
        for remote_ip in _remote_ips_:
            #inf = 'vxlan_' + remote_ip
            inf = ''.join([num.zfill(3) for num in remote_ip.split('.')])
            __n__['logger'].info('Deleting a VXLAN tunnel: ' + inf)
            cmdp('ovs-vsctl add-port', br_tun, inf, '-- set interface', inf, 'type=vxlan options:in_key=flow', 'options:local_ip='+_local_ip_, 'options:out_key=flow', 'options:remote_ip='+remote_ip)

        vxlan_ports = get_vxlan_ports()
        for vxlan_port in vxlan_ports:
            cmd('ovs-ofctl add-flow', br_tun, 'table=0,priority=1,in_port='+vxlan_port+',actions=resubmit(,2)')
         
