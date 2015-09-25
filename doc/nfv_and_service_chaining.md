Service Chaining Architecture
-----------------------------

At first, I have tried this configuration:

<pre>

               The Internet
                    |
                   ISP
                    |
                  [BRAS]
                    |
                    | PPPoE (over NTT East's FTTH network)
                    |
              [Home | GW  ] PPPoE pass through
                    |
                    | PPPoE
                    |
              [Internet GW]  NAPT, Firewall, DHCP, 802.11a/b/g
                    |  ^
                    |  |
                    | RIPv2 advertising 10.0.1.0/24
   [S F ]           |  |
    |  |   1001     |  |
 [RPI1    ]----[OpenWRT1]
     |\            /|
     | 101      103 |     VLAN 1 -- VNI 101
     |    \    /    |     VLAN 3 -- VNI 103
   101      \/     103    VNI 1 is a "default GW service path" among internal routers.
     |     /  \     |     VNI 101 as a service path between SF and OpenWRT2 and 3.
     |   /      \   1     VNI 1001 as a service path between SF and OpenWRT1.
     | /   101    \ | 
 [OpenWRT2]----[OpenWRT3]
  | |  | | 103  | |  | |
 Port  Port    Port  Port
 VLAN1 VLAN3   VLAN1 VLAN3

                                       [Service Function] L2 bump in the wire
                                           eth0 eth1
                                            . | | .
                                     VLAN 1 . | | . VLAN 111 
                                          [  br-int  ]
                                             . | .
                                      VLAN 1 . | . VLAN 111 
                                     . . . . . | . . . . . .                
[Host]-- VLAN 1 --[OpenWRT2]-- VNI 101- --[  br-tun  ]-- VNI 1001 --[OpenWRT1]---[Internet GW]

</pre>

In the ETSI NFV terminology, SF (Service Function) corresponds to VNF(Virtual Network Function).

OpenWRT1 works as a gateway between the Internet and neutron-lan. 
OpenWRT1 uses RIP to advertise networks 10.0.1.0/24 and 10.0.3.0/24 to the Internet GW.

A service function such as firewall or IPS is inserted between the Internet and VLAN 1 (but not VLAN 3) in the L2-bump-in-the-wire mode.

In my experimental setup, any service functions run in Linux Containers (LXC) on either Debian Linux machine or Raspberry Pi Type B machine:

<pre>

          Raspberry Pi
          . . . . . . . . . . . 
          .  [Liux Container] .
          .    |          |   .
          .   veth       veth .
          .    |          |   .
          .  [    br-int    ] .
          .         |         .
          .     VLAN trunk    .
          .         |         . 
          . .[    br-tun    ] .
            (                )
           (    V X L A N     )
            (                )
            

</pre>


Since [NSH](www.ietf.org/id/draft-quinn-nsh) is not available yet on openvswitch 2.0.0, it assigns seperate VNIs (as labels) for each service pathes.

Connecting LXC to openvsitch
----------------------------

[This blog page](http://blog.scottlowe.org/2014/01/23/automatically-connecting-lxc-to-open-vswitch/) tought me how to connect LXC to openvswitch. However, my implementation has not used the technique.

Here was my experiment before the implementation:

Service Functions such as IDS/IPS typically uses mutliple network interfaces. I let them have two interfaces:

/var/lib/lxc/vm1

<pre>
# networking
lxc.network.type = veth
lxc.network.flags = up
lxc.network.veth.pair = 1001
lxc.network.ipv4 = 0.0.0.0
lxc.network.script.up = /etc/lxc/ovsconf
lxc.network.type = veth
lxc.network.flags = up
lxc.network.veth.pair = 1002
lxc.network.ipv4 = 0.0.0.0
lxc.network.script.up = /etc/lxc/ovsconf
</pre>

"lxc-start" command calls ovsconf script when starting up the network.

/etc/lxc/ovsconf

<pre>
#!/bin/bash

BRIDGE="br-int"
PORT=int-sf$5

if [ $3 == "up" ]
then
   ovs-vsctl -- --may-exist add-br $BRIDGE
   ovs-vsctl -- --if-exists del-port $BRIDGE $PORT
   ovs-vsctl -- --may-exist add-port $BRIDGE $PORT tag=$5
else
   ovs-vsctl -- --if-exists del-port $BRIDGE $PORT
fi
</pre>

