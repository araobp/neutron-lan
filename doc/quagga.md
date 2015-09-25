Working with Quagga
===================

My Netgear router (WGU624) as Internet GW seems to support RIPv1 and RIPv2 for the LAN ports, 
so I have installed Quagga on OpenWRT1 to make it exchange routing info with the Netgear.

        The Internet
             |
             |
      [Netgear router] as Internet GW
             ^
             |
            RIPv2 to advertise routing info
             |
      [ OpenWRT1     ]

<pre>
root@OpenWrt:/etc# opkg install quagga-ripd
Installing quagga-ripd (0.99.22.3-1) to root...
Downloading http://downloads.openwrt.org/snapshots/trunk/ar71xx/packages/quagga-ripd_0.99.22.3-1_ar71xx.ipk.
Installing quagga (0.99.22.3-1) to root...
Downloading http://downloads.openwrt.org/snapshots/trunk/ar71xx/packages/quagga_0.99.22.3-1_ar71xx.ipk.
Installing quagga-libzebra (0.99.22.3-1) to root...
Downloading http://downloads.openwrt.org/snapshots/trunk/ar71xx/packages/quagga-libzebra_0.99.22.3-1_ar71xx.ipk.
Configuring quagga.
Configuring quagga-libzebra.
Configuring quagga-ripd.

root@OpenWrt:~# opkg install quagga-zebra
Installing quagga-zebra (0.99.22.3-1) to root...
Downloading http://downloads.openwrt.org/snapshots/trunk/ar71xx/packages/quagga-zebra_0.99.22.3-1_ar71xx.ipk.
Configuring quagga-zebra.

root@OpenWrt:/etc# opkg install quagga-vtysh
Installing quagga-vtysh (0.99.22.3-1) to root...
Downloading http://downloads.openwrt.org/snapshots/trunk/ar71xx/packages/quagga-vtysh_0.99.22.3-1_ar71xx.ipk.
Installing libreadline (6.2-1) to root...
Downloading http://downloads.openwrt.org/snapshots/trunk/ar71xx/packages/libreadline_6.2-1_ar71xx.ipk.
Installing libncurses (5.9-1) to root...
Downloading http://downloads.openwrt.org/snapshots/trunk/ar71xx/packages/libncurses_5.9-1_ar71xx.ipk.
Installing terminfo (5.9-1) to root...
Downloading http://downloads.openwrt.org/snapshots/trunk/ar71xx/packages/terminfo_5.9-1_ar71xx.ipk.
Configuring terminfo.
Configuring libreadline.
Configuring libncurses.
Configuring quagga-vtysh.
</pre>

I have intalled the quagga-ripd, quagga-zebra and quagga-btysh packages on OpenWRT1. Then I try to use vtysh:

<pre>
root@OpenWrt:~# /etc/init.d/quagga start
quagga.init: Starting zebra ... done.
quagga.init: Starting ripd ... done.
root@OpenWrt:~# vtysh

Hello, this is Quagga (version 0.99.22.3).
Copyright 1996-2005 Kunihiro Ishiguro, et al.

OpenWrt# configure terminal
OpenWrt(config)# interface eth0.2
OpenWrt(config-if)# link-detect
OpenWrt(config-if)# exit
OpenWrt(config)# router rip
OpenWrt(config-router)# redistribute connected
OpenWrt(config-router)# network eth0.2
OpenWrt(config-router)# exit
OpenWrt(config)# exit
OpenWrt# write
Building Configuration...
Configuration saved to /etc/quagga/zebra.conf
Configuration saved to /etc/quagga/ripd.conf
[OK]
OpenWrt# exit

root@OpenWrt:~# route
Kernel IP routing table
Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
default         192.168.1.1     0.0.0.0         UG    0      0        0 eth0.2
10.0.1.0        *               255.255.255.0   U     0      0        0 int-dvr1
10.0.3.0        *               255.255.255.0   U     0      0        0 int-dvr3
192.168.1.0     *               255.255.255.0   U     0      0        0 eth0.2

root@OpenWrt:~# ping 8.8.8.8 -c 3
PING 8.8.8.8 (8.8.8.8): 56 data bytes
64 bytes from 8.8.8.8: seq=0 ttl=44 time=44.520 ms
64 bytes from 8.8.8.8: seq=1 ttl=44 time=47.470 ms
64 bytes from 8.8.8.8: seq=2 ttl=44 time=44.491 ms

--- 8.8.8.8 ping statistics ---
3 packets transmitted, 3 packets received, 0% packet loss
round-trip min/avg/max = 44.491/45.493/47.470 ms

root@OpenWrt:~# ip netns exec ns1 ping 8.8.8.8
PING 8.8.8.8 (8.8.8.8): 56 data bytes
^C
--- 8.8.8.8 ping statistics ---
8 packets transmitted, 0 packets received, 100% packet loss

root@OpenWrt:~# /etc/init.d/quagga restart
quagga.init: Starting zebra ... done.
quagga.init: Starting ripd ... done.

root@OpenWrt:~# ip netns exec ns1 ping 8.8.8.8
PING 8.8.8.8 (8.8.8.8): 56 data bytes
64 bytes from 8.8.8.8: seq=0 ttl=43 time=54.986 ms
64 bytes from 8.8.8.8: seq=1 ttl=43 time=48.509 ms
64 bytes from 8.8.8.8: seq=2 ttl=43 time=44.515 ms
64 bytes from 8.8.8.8: seq=3 ttl=43 time=44.844 ms
64 bytes from 8.8.8.8: seq=4 ttl=43 time=44.853 ms
^C
--- 8.8.8.8 ping statistics ---
5 packets transmitted, 5 packets received, 0% packet loss
round-trip min/avg/max = 44.515/47.541/54.986 ms
</pre>
