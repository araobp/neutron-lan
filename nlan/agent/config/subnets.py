# 2014/3/17
# 2014/4/14  Service Chaining ('dvr', 'hub' and 'spoke_dvr' mode)
# 2014/4/28  delete, update
# subnets.py
#

import cmdutil
import re
from ovsdb import Row, OvsdbRow, search, get_vxlan_ports 
from errors import ModelError


nw_dst10 = '10.0.0.0/8'
nw_dst172 = '172.16.0.0/12'
nw_dst192 = '192.168.0.0/16'

# Example:
# If address='10.0.1.1' and mask='24', then
# the function returns '10.0.1.0'.
def network_address(address, mask):

    address = address.split('.')
    shift = 32 - int(mask)
    net = (int(address[0])*256**3+int(address[1])*256**2+int(address[2])*256+int(address[3]))>>shift<<shift
    a = str(net>>24)
    b1 = net>>16
    b2 = net>>24<<8
    b = str(b1 - b2)
    c1 = net>>8
    c2 = net>>16<<8
    c = str(c1 - c2)
    d1 = net
    d2 = net>>8<<8
    d = str(d1 - d2)
    return '.'.join([a,b,c,d])


def _dnsmasq(ifname, enable, ipaddr, mask, start='100', limit='150', leasetime='12h'):
   
    if __n__['platform'] == 'openwrt':

        cmd = cmdutil.check_cmd
        network_dvr = 'network.' + ifname
        mask = network_address('255.255.255.255', 24)

        if enable:
           
           # Modifies /etc/config/network by using uci
            cmd('uci set', network_dvr+'=interface')
            cmd('uci set', network_dvr+'.ifname='+ifname)
            cmd('uci set', network_dvr+'.proto=static')
            cmd('uci set', network_dvr+'.ipaddr='+ipaddr)
            cmd('uci set', network_dvr+'.netmask='+mask)
            
            # Modifies /etc/config/dhcp by using uci
            cmd('uci set', 'dhcp.'+ifname+'=dhcp')
            cmd('uci set', 'dhcp.'+ifname+'.interface='+ifname)
            cmd('uci set', 'dhcp.'+ifname+'.start='+start)
            cmd('uci set', 'dhcp.'+ifname+'.limit='+limit)
            cmd('uci set', 'dhcp.'+ifname+'.leasetime='+leasetime)

            # Commits the changes
            cmd('uci commit')
          
            # Restart network
            cmd('/etc/init.d/network restart')

            # Restarts dnsmasq
            cmd('/etc/init.d/dnsmasq restart')
        else:
            # Modifies /etc/config/network by using uci
            cmd('uci delete', network_dvr)
            
            # Modifies /etc/config/dhcp by using uci
            cmd('uci delete', 'dhcp.'+ifname)

            # Commits the changes
            cmd('uci commit')
           
            # Restart network
            cmd('/etc/init.d/network restart')

            # Restarts dnsmasq
            cmd('/etc/init.d/dnsmasq restart')


    else:
        raise ModelError("ip_dvr DHCP server option is supported by 'openwrt' platform only")

    

# Add subnet
def _add_subnets():
	
    cmd = cmdutil.check_cmd
    output_cmd = cmdutil.output_cmd
    cmdp = cmdutil.check_cmdp

    svni = str(_vni_)
    svid = str(_vid)
    ns = "ns"+svni
    br = "br"+svni
    veth_ns = "veth-ns"+svni
    temp_ns = "temp-ns"+svni
    int_br = "int_br"+svni
    int_dvr = "int_dvr"+svni

    #>>> Adding VLAN and a linux bridge
    if _vid:
        cmd('brctl addbr', br)
        cmdp('ovs-vsctl add-port br-int', int_br, 'tag='+svid, '-- set interface', int_br, 'type=internal')
        cmdp('ovs-vsctl add-port br-int', int_dvr, 'tag='+svid, '-- set interface', int_dvr, 'type=internal')
        cmd('brctl addif', br, int_br)
        cmd('ip link set dev', int_br, 'promisc on')
        cmd('ip link set dev', int_br, 'up')
        if _ip_dvr and 'dhcp' in _ip_dvr and __n__['init'] == 'start':
            pass # OpenWrt's /etc/config/network has int_dvr entry
        else:
            cmd('ip link set dev', int_dvr, 'up')
        cmd('ip link set dev', br, 'up')

    #>>> Adding vHost
    if _ip_vhost:
        cmd('ip netns add' , ns)
        cmd('ip link add', veth_ns, 'type veth peer name', temp_ns)
        cmd('ip link set dev', temp_ns, 'netns', ns)
        cmd('ip netns exec', ns, 'ip link set dev', temp_ns, 'name eth0')
        cmd('brctl addif', br, veth_ns)
        cmd('ip link set dev', veth_ns, 'promisc on')
        cmd('ip link set dev', veth_ns, 'up')
        cmd('ip netns exec', ns, 'ip link set dev eth0 up')
        cmd('ip netns exec', ns, 'ip addr add dev eth0', _ip_vhost)
        if _ip_dvr_:
            # Distributed Virtual Router
            cmd('ip netns exec', ns, 'ip route add default via', _ip_dvr_['addr'].split('/')[0], 'dev eth0')

    #>>> Adding DVR gateway address
    if _ip_dvr:
        if 'dhcp' in _ip_dvr and __n__['init'] == 'start':
            pass # OpenWrt's /etc/config/network has int_dvr entry
        elif _ip_dvr['mode'] == 'spoke':
            pass # In this case, the hub's ip_dvr['addr'] is a default gw for hosts
        else:
            cmd('ip addr add dev', int_dvr, _ip_dvr['addr'])
        if 'dhcp' in _ip_dvr and __n__['init'] != 'start':
            addr = _ip_dvr['addr'].split('/')
            ipaddr = addr[0]
            mask = addr[1]
            _dnsmasq(int_dvr, True, ipaddr, mask)
        if ip_vhost_:
            # Distributed Virtual Router
            cmd('ip netns exec', ns, 'ip route add default via', _ip_dvr['addr'].split('/')[0], 'dev eth0')

    #>>> Adding physical ports to the Linux bridge
    if _ports:
        for port in _ports:
            cmd('brctl addif', br, port)

    #>>> Default GW for the subnet
    if _default_gw:
        o = output_cmd('route').splitlines()
        for l in o:
            if l.startswith('default'):
                cmd('ip route del default')
        cmd('ip route add default via', _default_gw)
	

# Delete subnet
def _delete_subnets():
	
    cmd = cmdutil.check_cmd
    output_cmd = cmdutil.output_cmd

    svni = str(vni_)
    ns = "ns"+svni
    br = "br"+svni
    veth_ns = "veth-ns"+svni
    temp_ns = "temp-ns"+svni
    int_br = "int_br"+svni
    int_dvr = "int_dvr"+svni

    #>>> Default GW for the subnet
    if _default_gw:
        o = output_cmd('route').splitlines()
        for l in o:
            if l.startswith('default'):
                cmd('ip route del default')

    #>>> Deleting physical ports to the Linux bridge
    if _ports:
        for port in ports_:
            cmd('brctl delif', br, port)

    #>>> Deleting DVR gateway address
    if _ip_dvr:
        if 'dhcp' in ip_dvr_:
            addr = ip_dvr_['addr'].split('/')
            ipaddr = addr[0]
            mask = addr[1]
            _dnsmasq(int_dvr, False, ipaddr, mask)
        if ip_vhost_:
            cmd('ip netns exec', ns, 'ip route delete default via', ip_dvr_['addr'].split('/')[0], 'dev eth0')
        if 'dhcp' not in ip_dvr_ and ip_dvr_['mode'] != 'spoke':
            cmd('ip addr delete dev', int_dvr, ip_dvr_['addr'])
    
    #>>> Deleting vHost
    if _ip_vhost:
        if _ip_dvr_:
            cmd('ip netns exec', ns, 'ip route delete default via', ip_dvr_['addr'].split('/')[0], 'dev eth0')
        cmd('ip netns exec', ns, 'ip addr delete dev eth0', ip_vhost_)
        cmd('ip netns exec', ns, 'ip link set dev eth0 down')
        cmd('ip link set dev', veth_ns, 'down')
        cmd('brctl delif', br, veth_ns)
        cmd('ip netns delete', ns)

    #>>> Deleting VLAN and a linux bridge
    if _vid:
        cmd('ip link set dev', int_dvr, 'down')
        cmd('ip link set dev', int_br, 'down')
        cmd('brctl delif', br, int_br)
        cmd('ovs-vsctl del-port br-int', int_dvr)
        cmd('ovs-vsctl del-port br-int', int_br)
        cmd('ip link set dev', br, 'down')
        cmd('brctl delbr', br)


# Adds flow entries 
# 1) mode == 'dvr' or default
#  Remote node
#     ^
#     | Dropped (one way)
#     |
#  ARP w/ TPA = ip_dvr
# [br-tun]
#
# 2) mode == 'spoke_dvr'
# [br-int]
#     ^ Dropped (one way)
#     | 
#     | int_dvr
#  ARP (opcode=2) w/ SPA = ip_dvr
#  opcode 1: ARP Request
#  opcode 2: ARP Reply
# 
#  In this mode, all the packets pertaining to the other subnets (excluding
#  global IP addresses) are also redirected to the 'local' ip_dvr for
#  distributed virtual routing.
#
# 3) mode == 'hub' or 'spoke'
# No flow entries added
#
def _flow_entries(ope):
    
    # serarch Open_vSwitch table
    if not search('Controller', ['target']): # no OpenFlow Controller

        params = {}

        if ope == 'add':
            params['svni'] = str(_vni_)
            params['svid'] = str(_vid_)
            if _ip_dvr:
                params['defaultgw'] = _ip_dvr['addr'].split('/')[0]
        else: # 'delete'
            params['svni'] = str(vni_)
            params['svid'] = str(vid_)
            if _ip_dvr:
                params['defaultgw'] = ip_dvr_['addr'].split('/')[0]

        int_dvr = "int_dvr" + params['svni']
        int_br = "int_br" + params['svni']

        cmd = cmdutil.check_cmd

        if _vid:
            if ope:
                cmd('ovs-ofctl add-flow br-tun table=2,priority=1,tun_id={svni},actions=mod_vlan_vid:{svid},resubmit(,10)'.format(**params))
            else:
                cmd('ovs-ofctl del-flows br-tun table=2,tun_id={svni}'.format(**params))
        
        if _ip_dvr and 'mode' not in _ip_dvr:
            raise ModelError('requires "mode"')

        if _ip_dvr and _ip_dvr['mode'] == 'dvr':
            if ope:
                cmd('ovs-ofctl add-flow br-tun', 'table=19,priority=1,dl_type=0x0806,dl_vlan={svid},nw_dst={defaultgw},actions=drop'.format(**params))
            else:
                cmd('ovs-ofctl del-flows br-tun', 'table=19,dl_type=0x0806,dl_vlan={svid},nw_dst={defaultgw}'.format(**params))

        # Redirects a packet to int_dvr port if nw_dst is a private ip address
        elif _ip_dvr and _ip_dvr['mode'] == 'spoke_dvr':
           
            mask = _ip_dvr['addr'].split('/')[1]
            #address = params['defaultgw'].split('.')
            nw_dst = network_address(params['defaultgw'], mask)+'/'+mask
            
            output = cmdutil.output_cmd('ip link show dev', int_dvr).split('\n')[1]
            dl_dst = output.split()[1]
            
            r = OvsdbRow('Interface', ('name', int_dvr))
            outport = str(r['ofport'])
            r = OvsdbRow('Interface', ('name', int_br))
            inport = str(r['ofport'])

            params['inport'] = inport
            params['outport'] = outport
            params['dl_type'] = '0x0800' 
            params['dl_dst'] = dl_dst 
            params['nw_dst'] = nw_dst
            params['nw_dst10'] = nw_dst10
            params['nw_dst172'] = nw_dst172
            params['nw_dst192'] = nw_dst192
            params['cmdadd'] = 'ovs-ofctl add-flow br-int'
            params['cmddel'] = 'ovs-ofctl del-flows br-int'

            if ope:
                cmd('{cmdadd} table=0,priority=2,in_port={inport},dl_type={dl_type},nw_dst={nw_dst},actions=normal'.format(**params))
                cmd('{cmdadd} table=0,priority=1,in_port={inport},dl_type={dl_type},nw_dst={nw_dst10},actions=resubmit(,1)'.format(**params))
                cmd('{cmdadd} table=0,priority=1,in_port={inport},dl_type={dl_type},nw_dst={nw_dst172},actions=resubmit(,1)'.format(**params))
                cmd('{cmdadd} table=0,priority=1,in_port={inport},dl_type={dl_type},nw_dst={nw_dst192},actions=resubmit(,1)'.format(**params))
                # ARP, opcode = 2, TPA = defaultgw
                cmd('{cmdadd} table=0,priority=1,in_port={outport},dl_type=0x0806,nw_src={defaultgw},nw_proto=2,actions=drop'.format(**params))
                cmd('{cmdadd} table=1,priority=0,in_port={inport},actions=set_field:{dl_dst}->dl_dst,output:{outport}'.format(**params))
            else:
                cmd('{cmddel} table=0,in_port={inport},dl_type={dl_type},nw_dst={nw_dst}'.format(**params))
                cmd('{cmddel} table=0,in_port={inport},dl_type={dl_type},nw_dst={nw_dst10}'.format(**params))
                cmd('{cmddel} table=0,in_port={inport},dl_type={dl_type},nw_dst={nw_dst172}'.format(**params))
                cmd('{cmddel} table=0,in_port={inport},dl_type={dl_type},nw_dst={nw_dst192}'.format(**params))
                # ARP, opcode = 2, TPA = defaultgw
                cmd('{cmddel} table=0,in_port={outport},dl_type=0x0806,nw_src={defaultgw},nw_proto=2'.format(**params))
                cmd('{cmddel} table=1,in_port={inport}'.format(**params))

        elif _ip_dvr and _ip_dvr['mode'] == 'hub' or 'spoke':
            pass
        else:
            pass 

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
        __n__['logger'].info('Adding a subnet(vlan): ' + str(_vid))
        _add_subnets()
        _flow_entries('add')
    else:
        raise ModelError("requires at least _vni and _vid")

def delete():
    if _vni and _vid_:
        raise ModelError("vid still exists")
    if _vid and (_ip_dvr_ or _ip_vhost_ or _peers_ or _ports_ or _default_gw_):
            raise ModelError("the other params still exits")
    __n__['logger'].info('Deleting a subnet(vlan): ' + str(_vid))
    _flow_entries('delete')
    _delete_subnets()

def update():
    if _vni or _vid:
        raise ModelError('update not allowed for vni and vid')
    __n__['logger'].info('Updating a subnet(vlan): ' + str(_vid))
    _flow_entries('delete')
    _delete_subnets()
    _add_subnets()
    _flow_entries('add')
