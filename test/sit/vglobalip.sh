#!/bin/bash
#
# This script creates a virtual global IP address space "ns-global"
# with one virtual host having an IP address 8.8.8.8/24.
# 
export PATH=$PATH:../nlan
nlan.py -t openwrt1 --raw 'ip netns add ns-global'
nlan.py -t openwrt1 --raw 'ip link add veth-global type veth peer name temp'
nlan.py -t openwrt1 --raw 'ip link set dev temp netns ns-global'
nlan.py -t openwrt1 --raw 'ip netns exec ns-global ip link set dev temp name eth0'
nlan.py -t openwrt1 --raw 'ip netns exec ns-global ip addr add dev eth0 8.8.8.8/24'
nlan.py -t openwrt1 --raw 'ip link set dev veth-global up'
nlan.py -t openwrt1 --raw 'ip addr add dev veth-global 8.8.8.1/24'
nlan.py -t openwrt1 --raw 'ip netns exec ns-global ip link set dev eth0 up'
nlan.py -t openwrt1 --raw 'ip netns exec ns-global ip route add default via  8.8.8.1'

