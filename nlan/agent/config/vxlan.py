# 2014/3/17
# vxlan.py
#

import cmdutil
from ovsdb import Row, get_vxlan_ports
from errors import ModelError

cmd = cmdutil.check_cmd	
cmdp = cmdutil.check_cmdp	

def add():
    
    if not _local_ip_:
        raise ModelError('"_local_ip_" is mandatory')
    if _remote_ips:
        for remote_ip in _remote_ips:
            #inf = 'vxlan_' + remote_ip
            inf = ''.join([num.zfill(3) for num in remote_ip.split('.')])
            __n__['logger'].info('Adding a VXLAN tunnel: ' + inf)
            cmdp('ovs-vsctl add-port br-tun', inf, '-- set interface', inf, 'type=vxlan options:in_key=flow', 'options:local_ip='+_local_ip, 'options:out_key=flow', 'options:remote_ip='+remote_ip)

        # vxlan_ports = get_vxlan_ports(_remote_ips) 
        # TODO: yamldiff.py does not work on list parameters very well.
        vxlan_ports = get_vxlan_ports()
        for vxlan_port in vxlan_ports:
            cmd('ovs-ofctl add-flow br-tun', 'table=0,priority=1,in_port='+vxlan_port+',actions=resubmit(,2)')


def delete():
    
    if _remote_ips:
        # vxlan_ports = get_vxlan_ports(_remote_ips) 
        # TODO: yamldiff.py does not work on list parameters very well.
        vxlan_ports = get_vxlan_ports()
        for vxlan_port in vxlan_ports:
            cmd('ovs-ofctl del-flows br-tun table=0,in_port={vxlan_port}'.format(vxlan_port=vxlan_port))
        
        for remote_ip in _remote_ips:
            #inf = 'vxlan_' + remote_ip
            inf = ''.join([num.zfill(3) for num in remote_ip.split('.')])
            __n__['logger'].info('Deleting a VXLAN tunnel: ' + inf)
            cmd('ovs-vsctl del-port br-tun', inf)
    
    if _local_ip:
        # All remote IPs must be deleted before deleting local IP
        if remote_ips_:
            if not (set(_remote_ips) == set(remote_ips_)):
                raise ModelError('"local_ip" cannot be deleted') 


def update():

    # if_local_ip:
    # TODO: yamldiff.py must not generate update on list parameters.
    if _local_ip or _remote_ips:
        # Delete all interfaces and flows 
        vxlan_ports = get_vxlan_ports()
        for vxlan_port in vxlan_ports:
            cmd('ovs-ofctl del-flows br-tun table=0,in_port={vxlan_port}'.format(vxlan_port=vxlan_port))
        
        for remote_ip in remote_ips_:
            #inf = 'vxlan_' + remote_ip
            inf = ''.join([num.zfill(3) for num in remote_ip.split('.')])
            __n__['logger'].info('Adding a VXLAN tunnel: ' + inf)
            cmd('ovs-vsctl del-port br-tun', inf)
       
        # Add those interfaces and flows again to change the local IP address
        for remote_ip in _remote_ips_:
            #inf = 'vxlan_' + remote_ip
            inf = ''.join([num.zfill(3) for num in remote_ip.split('.')])
            __n__['logger'].info('Deleting a VXLAN tunnel: ' + inf)
            cmdp('ovs-vsctl add-port br-tun', inf, '-- set interface', inf, 'type=vxlan options:in_key=flow', 'options:local_ip='+_local_ip_, 'options:out_key=flow', 'options:remote_ip='+remote_ip)

        vxlan_ports = get_vxlan_ports()
        for vxlan_port in vxlan_ports:
            cmd('ovs-ofctl add-flow br-tun', 'table=0,priority=1,in_port='+vxlan_port+',actions=resubmit(,2)')
         
