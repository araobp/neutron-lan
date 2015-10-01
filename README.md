#neutron-lan

![neutron-lan testbed](https://raw.github.com/araobp/neutron-lan/master/misc/neutron-lan-testbed.png)
![Raspberry Pi](https://raw.github.com/araobp/neutron-lan/master/misc/rpi.png)

##DevOps tool 'nlan'
* [Slides](doc/NLAN.pdf)
* [Command usage](https://github.com/araobp/neutron-lan/blob/master/doc/command_usage.md)
* [Working with Docker](https://github.com/araobp/neutron-lan/blob/master/SETUP.md)
* [Transport network (PTN) simulation](https://github.com/araobp/neutron-lan/blob/master/doc/ptn_modules.txt)
* [Whitebox optical (just an idea)](doc/whitebox_optical.md)
* [code](https://github.com/araobp/neutron-lan)

##INDEX
* [Software Defined Networking](https://github.com/araobp/neutron-lan/blob/master/doc/software_defined_networking.md)
* [YAML-based network modeling](https://github.com/araobp/neutron-lan/blob/master/doc/modeling.md)
* [OVSDB schema for neutron-lan](https://github.com/araobp/neutron-lan/blob/master/doc/ovsdb-schema.md)
* [Ordering states and template engine](https://github.com/araobp/neutron-lan/blob/master/doc/state_order.md)
* [Service Function](https://github.com/araobp/neutron-lan/blob/master/doc/service_function.md)
* [Virtual Subnet](https://github.com/araobp/neutron-lan/blob/master/doc/virtual_subnet.md)
* [Working with Quagga](https://github.com/araobp/neutron-lan/blob/master/doc/quagga.md)
* [Initial config for Buffalo BHR-4GRV](https://github.com/araobp/neutron-lan/blob/master/doc/initial-config-for-bhr-4grv.md)
* [Initial config for Raspberry Pi](https://github.com/araobp/neutron-lan/blob/master/doc/initial-config-for-rpi.md)
* [Test bed at my home](https://github.com/araobp/neutron-lan/wiki/Testbed)
* [SDN in the past(I used to be a Telephony guy)](https://github.com/araobp/neutron-lan/blob/master/doc/sdn_in_the_past.md)
* [What I have learned from this project](doc/what_I_have_learned.md)


##BACKGROUND AND MOTIVATION

This is my personal project to **study SDN(Software-Defined Networking)** by configuring a openstack-neutron-like network over OpenWRT routers at home (I call it "neturon-lan") and making some SDN-related experiments on the network.

[Neutron](https://wiki.openstack.org/wiki/Neutron) is a software technology for OpenStack networking. However, I think the network architecture (edge-overlay / centralized management and distributed agents) can also be applied to LAN, leveraging edge-overlay technolgies such as [VXLAN](http://datatracker.ietf.org/doc/draft-mahalingam-dutt-dcops-vxlan/), as some start-up companies are actually pursuing that. 

I am also interested in the distributed virtual switch and distributed virtual router concept that has been adopted by a number of IaaS cloud management systems such as OpenStack Neutron.

As for network service abstraction, there are a lot of SDN and DevOps platforms out there. However, I will develop a DevOps-like tool on my own because of the CPU and memory limitaions of OpenWRT routers.

##HOW VXLAN WORKS

**neutron-lan** is partly based on the OpenStack neutron networking architecture.

Neutron configures two kinds of bridges on each compute node and a network node: "br-int" and "br-tun", if you chose GRE or VXLAN as a network virtualization option.

"br-int" is a normal mac-learning vswitch, whereas "br-tun" works as a GRE GW or VXLAN GW.

```
       Port VLANs
          |  |
        [br-int] Integration bridge
           |
           |VLAN trunk
           |
        [br-tun] VLAN <=> VXLAN GW
      (          )
     (  VXLAN     )
      (          )
    [br-tun]  [br-tun]
       |         |
    [br-int]  [br-int]
```

In case of a network like this,

```
      [br-int]
         | vlan trunk
         | port1
      [br-tun]
       |   |
    vxlan vxlan
    port2 port3
```

flow entries on the "br-tun" are as follows(this is an actual dump from an OpenStack compute node):

```
    root@compute1:~# ovs-ofctl dump-flows br-tun
    NXST_FLOW reply (xid=0x4):
     cookie=0x0, duration=9638.539s, table=0, n_packets=0, n_bytes=0, idle_age=9638, priority=1,in_port=3 actions=resubmit(,2)
     cookie=0x0, duration=9642.632s, table=0, n_packets=502, n_bytes=51575, idle_age=1003, priority=1,in_port=1 actions=resubmit(,1)
     cookie=0x0, duration=9628.395s, table=0, n_packets=657, n_bytes=68175, idle_age=1003, priority=1,in_port=2 actions=resubmit(,2)
     cookie=0x0, duration=9642.472s, table=0, n_packets=2, n_bytes=140, idle_age=9635, priority=0 actions=drop
     cookie=0x0, duration=9642.102s, table=1, n_packets=10, n_bytes=1208, idle_age=1700, priority=0,dl_dst=01:00:00:00:00:00/01:00:00:00:00:00 actions=resubmit(,21)
     cookie=0x0, duration=9642.278s, table=1, n_packets=492, n_bytes=50367, idle_age=1003, priority=0,dl_dst=00:00:00:00:00:00/01:00:00:00:00:00 actions=resubmit(,20)
     cookie=0x0, duration=9636.347s, table=2, n_packets=657, n_bytes=68175, idle_age=1003, priority=1,tun_id=0x3 actions=mod_vlan_vid:1,resubmit(,10)
     cookie=0x0, duration=9641.973s, table=2, n_packets=1, n_bytes=94, idle_age=9636, priority=0 actions=drop
     cookie=0x0, duration=9641.823s, table=3, n_packets=0, n_bytes=0, idle_age=9641, priority=0 actions=drop
     cookie=0x0, duration=9641.677s, table=10, n_packets=657, n_bytes=68175, idle_age=1003, priority=1 actions=learn(table=20,hard_timeout=300,priority=1,NXM_OF_VLAN_TCI[0..11],NXM_OF_ETH_DST[]=NXM_OF_ETH_SRC[],load:0->NXM_OF_VLAN_TCI[],load:NXM_NX_TUN_ID[]->NXM_NX_TUN_ID[],output:NXM_OF_IN_PORT[]),output:1
     cookie=0x0, duration=9641.545s, table=20, n_packets=0, n_bytes=0, idle_age=9641, priority=0 actions=resubmit(,21)
     cookie=0x0, duration=9636.651s, table=21, n_packets=10, n_bytes=1208, idle_age=1700, hard_age=9628, priority=1,dl_vlan=1 actions=strip_vlan,set_tunnel:0x3,output:3,output:2
     cookie=0x0, duration=9641.394s, table=21, n_packets=0, n_bytes=0, idle_age=9641, priority=0 actions=drop
```

Note that "tun_id=0x3" matches VXLAN VNI field and "set_tunnel:0x3" sets a value 0x3 to VNI, and "actions=learn(...)" is a openvswitch-specific extension to add flow entries for outgoing packets dynmaically by learning from incoming packets. So the config is rather static.

The following is a tcpdump output. You can recognize that VNI 0x3 in it: find "0800 0000 0000 0300" in it and "0000 03" is VNI.

```
    root@OpenWrt:~/bin# tcpdump -X -i eth2
    tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
    listening on eth2, link-type EN10MB (Ethernet), capture size 65535 bytes
    08:16:49.239471 IP 192.168.57.102.52236 > 192.168.57.103.4789: UDP, length 106
            0x0000:  4500 0086 a9d6 4000 4011 9c72 c0a8 3966  E.....@.@..r..9f
            0x0010:  c0a8 3967 cc0c 12b5 0072 0000 0800 0000  ..9g.....r......
            0x0020:  0000 0300 de66 3126 1dda 663f 26ad ab35  .....f1&..f?&..5
            0x0030:  0800 4500 0054 c5b5 4000 4001 7ed5 c0a8  ..E..T..@.@.~...
            0x0040:  3a66 c0a8 3a67 0800 03ff 9c6e 00a1 48e5  :f..:g.....n..H.
            0x0050:  0e0c 0000 0000 0000 0000 0000 0000 0000  ................
            0x0060:  0000 0000 0000 0000 0000 0000 0000 0000  ................
            0x0070:  0000 0000 0000 0000 0000 0000 0000 0000  ................
            0x0080:  0000 0000 0000                           ......
    08:16:49.239641 IP 192.168.57.103.51952 > 192.168.57.102.4789: UDP, length 106
            0x0000:  4500 0086 15cb 4000 4011 307e c0a8 3967  E.....@.@.0~..9g
            0x0010:  c0a8 3966 caf0 12b5 0072 0000 0800 0000  ..9f.....r......
            0x0020:  0000 0300 663f 26ad ab35 de66 3126 1dda  ....f?&..5.f1&..
            0x0030:  0800 4500 0054 6083 0000 4001 2408 c0a8  ..E..T`...@.$...
            0x0040:  3a67 c0a8 3a66 0000 0bff 9c6e 00a1 48e5  :g..:f.....n..H.
            0x0050:  0e0c 0000 0000 0000 0000 0000 0000 0000  ................
            0x0060:  0000 0000 0000 0000 0000 0000 0000 0000  ................
            0x0070:  0000 0000 0000 0000 0000 0000 0000 0000  ................
            0x0080:  0000 0000 0000                           ......
              
         
                 0                   1                   2                   3
                 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
         
            VXLAN Header:
                +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
                |R|R|R|R|I|R|R|R|            Reserved                           |
                +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
                |                VXLAN Network Identifier (VNI) |   Reserved    |
                +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

You can manually add the entries to br-tun using ovs-ofctl command like this:

```
    port 2: patch-tun, port3: vxlan1, port4:vxlan0
    $ ovs-ofctl del-flows br-tun
    $ ovs-ofctl add-flow br-tun "table=0,priority=1,in_port=4 ,actions=resubmit(,2)"
    $ ovs-ofctl add-flow br-tun "table=0,priority=1,in_port=2,actions=resubmit(,1)"
    $ ovs-ofctl add-flow br-tun "table=0,priority=1,in_port=3,actions=resubmit(,2)"
    $ ovs-ofctl add-flow br-tun "table=0,priority=0,actions=drop"
    $ ovs-ofctl add-flow br-tun "table=1,priority=0,dl_dst=01:00:00:00:00:00/01:00:00:00:00:00 ,actions=resubmit(,21)"
    $ ovs-ofctl add-flow br-tun "table=1,priority=0,dl_dst=00:00:00:00:00:00/01:00:00:00:00:00 ,actions=resubmit(,20)"
    $ ovs-ofctl add-flow br-tun "table=2,priority=1,tun_id=0x3,actions=mod_vlan_vid:1,resubmit(,10)"
    $ ovs-ofctl add-flow br-tun "table=2,priority=0,actions=drop"
    $ ovs-ofctl add-flow br-tun "table=3,priority=0,actions=drop"
    $ ovs-ofctl add-flow br-tun "table=10, priority=1,actions=learn(table=20,hard_timeout=300,priority=1,NXM_OF_VLAN_TCI[0..11],NXM_OF_ETH_DST[]=NXM_OF_ETH_SRC[],load:0->NXM_OF_VLAN_TCI[],load:NXM_NX_TUN_ID[]->NXM_NX_TUN_ID[],output:NXM_OF_IN_PORT[]),output:2"
    $ ovs-ofctl add-flow br-tun "table=20,priority=0,actions=resubmit(,21)"
    $ ovs-ofctl add-flow br-tun "table=21,priority=1,dl_vlan=1,actions=strip_vlan,set_tunnel:0x3,output:4,output:3"
    $ ovs-ofctl add-flow br-tun "table=21,priority=0,actions=drop"
```

##Technology choice

I thought of [OpenDaylight](https://wiki.opendaylight.org/view/Main_Page) as a platform for this project at first, but it's too heavy for such a small network, and the hardest thing for me is to write code in Java for ODL: too complex for me (Eclipse, OSGi, Maven, YANG...). However, it's service abstraction layer [MD-SAL](https://wiki.opendaylight.org/view/OpenDaylight_Controller:MD-SAL:Architecture) is quite interesting. It's sort of a perfect network abstraction mechanism...

Then I saw other messaging protocols such as XMPP(Jabber), AMQP(RabbitMQ) etc. But, because of the memory and storage limitations of OpenWRT routers, I gave up those.

So my conclusion was I just stick to ssh (and a few of other protocols such as OVSDB protocol for openvswitch) to configure and manage those routers remotely, and I will develop a DevOps-like tool on my own.

I installed python-mini package on my router using opkg, and I found the storage/memory consumption was quite low. I will develop DevOps agents written in Python with python-mini and a few other optional python packages.

As a reference, I looked into [SaltStack](http://www.saltstack.com/). Although it seemed quite interesting, OpenWRT does not support salt-minion and it's state management mechanism seems to me a bit strange from a network management standpoint, so I have decided to develop a tool like salt, salt-ssh and salt-minion on my own.

```
      [Tool A]  [Tool B]  [Tool C]...
          |         |        |
    +-----------------------------------------------------+
    |         Simple Service Abstraction Layer            |
    - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    |         neutron-lan modeling with YAML              |
    +-----------------------------------------------------+
                  |
                 ssh
                  |
        [Agents w/ minimal capabilities]]]
    
```

##MTU issue

Since the VXLAN overhead is 50 bytes, you need to adjust path MTU on each end host in some way.

* Using DNS option: Here is [an openstack tech blog](http://techbackground.blogspot.jp/2013/06/dnsmasq-logging-and-options-for-quantum.html) explaining how to do that for OpenStack neutron.
* MSS clamping by iptables: [MSS clamping for OpenWRT](http://wiki.openwrt.org/doc/howto/pseudowire). And [this blog](http://blog.ipspace.net/2013/01/tcp-mss-clamping-what-is-it-and-why-do.html) explains why MSS clamping is necessary.

I would chose the latter option, and that is something hareware-based routing/switching (incl. "physical" OpenFlow switches) is not good at.

Note: these days, small routers also support Jumbo Frame. So I don't need to care this issue any longer...

##Tackling security issues

VXLAN-based network virtualization raises some security issues. For example, an attacker can intrude or hyjack any VXLAN by spoofing VTEP(VXLAN Tunnel End Point). To prevent this kind of attack, some VTEP authentication mechanism will be introduced.

One idea I have devised:
```
      vhosts exchange some auth packets among themselves periodically.

      netns                                                      netns
      . . . . .                                                 . . . . .
      .[vhost].                                                 .[vhost].
      . . | . .                                                 . . | . .
          |                                                         |
        [br]--[br-int]--[br-tun] === VXLAN === [br-tun]--[br-int]--[br]

                                  auth packet
```

Note: this idea has not been implemented yet.

##Why so many bridges inside?

Why are there so many bridges? Linux bridges, br-int and br-tun...
* br-int works as a MAC-learning switch.
* br-tun works as a VXLAN GW with static flows preinstalled. BUM packets are broadcast to all VXLAN ports. Loop can be avoided by installing flows in a split-horizon manner. MAC-learning is also enabled for outgoing unicast packets. This MAC-learning process makes use of openvswitch-specific OF action.
* According to OpenStack neutron documentation, since openvswitch does not seem to work with iptables very well(?), Linux bridges are necessary between LAN ports and br-int. The OpenStack neutron development team seems to be trying to get rid of iptables and add additional flow entries (stateless firewall) to br-tun.
* openvswitch does not support IP multicast for BUM packets over VXLAN, so br-tun needs to replicate a packet for each VXLAN tunnel.

So there will be an impact on the performance, and I am looking forward to see some improvements on OpenStack neutron by the development team.
