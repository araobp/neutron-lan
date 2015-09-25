Raspberry Pi is used as Service Function serving DHCP server and IDS/IPS capabilities for neutron-lan.

I. DHCP Server 
--------------
<pre>
                 +----------------+
                 |Service Function| DHCP Server 
                 +----------------+                   
                 int-sf1    int-sf3
                    |          |
                  [GW]       [GW]
Location A          |          |              Location C
                    |          |
VLAN 1 --+---[GW]--++- VNI 100 -----[GW]---+-- VLAN 23
         |         |           |           |
       [IR]        |           |         [IR]
         |         |           |           |
VLAN 3 --+---[GW]--- VNI 103 -++----[GW]---+-- VLAN 27
                   |          |
                   |          |
                 [GW]       [GW]
                   |          |
                   +---[IR]-+
                   |          |
                 VLAN 14    VLAN 15

                    Location B
</pre>

For the time being, DVR A, B and C have direct access too Internet GW (in my case, home gateway).


II. Internet GW
---------------
In this configuration, DVR feature is disabled and Raspberry Pi works as a Internet GW.
<pre>
                     Internet
                         |
                 +----------------+
                 |Service Function| Internet GW 
                 +----------------+ NAPT, dnsmasq(DHCP), Snort(IPS inline-mode)
                 int-sf1    int-sf3
                    |          |
                  [GW]       [GW]
Location A          |          |              Location C
                    |          |
VLAN 1 --+---[GW]--++- VNI 100 -----[GW]---+-- VLAN 23
         |         |           |           |
       [*** *]     |           |         [*** *]
         |         |           |           |
VLAN 3 --+---[GW]--- VNI 103 -++----[GW]---+-- VLAN 27
                   |          |
                   |          |
                 [GW]       [GW]
                   |          |
                   +--[*** *]-+
                   |          |
                 VLAN 14    VLAN 15

                    Location B 
</pre>


III. Firewall/IDS/IPS
---------------------
<pre>
                 +----------------+
                 |Service Function| Snort(IDS or inline IPS mode)
                 +----------------+
                 mz.101     dmz.1001 
                    |          |
                  [GW]       [GW]
                    |          |
                 VNI 101     VNI 1001
                    |          |
Location A     +----+--+       +-----+   Location C
               |       |             |
VLAN 1 --+---[GW]--+   l            [GW]---+-- VLAN 23
         |         |   |                   |  RIPv2
       [IR]        |   |                 [IR]--------[Internet GW]
         |         |   |                   |     
VLAN 3 --+---[GW]------|--VNI 103---[GW]---+-- VLAN 27
                   |   |      |
                   |   |      |
                  [GW]-+     [GW]
                   |          |
                   +---[IR]---+
                   |          |
                 VLAN 14    VLAN 15

                    Location B
</pre>
