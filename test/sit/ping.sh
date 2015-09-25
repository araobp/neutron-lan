#!/bin/bash
export PATH=$PATH:../nlan
nlan.py test.echo 'Hello World!'
nlan.py -t openwrt1 --raw 'ip netns exec ns1001 ping -c 1 10.0.1.102'
nlan.py -t openwrt1 --raw 'ip netns exec ns1001 ping -c 1 10.0.1.102'
nlan.py -t openwrt1 --raw 'ip netns exec ns103 ping -c 1 10.0.3.103'
nlan.py -t openwrt3 --raw 'ip netns exec ns103 ping -c 1 10.0.1.101'
nlan.py -t openwrt2 --raw 'ip netns exec ns101 ping -c 1 192.168.100.1'
nlan.py -t openwrt3 --raw 'ip netns exec ns101 ping -c 1 192.168.100.1'
nlan.py -t openwrt2 --raw 'ip netns exec ns103 ping -c 1 192.168.100.1'
nlan.py -t openwrt2 --raw 'ping -c 1 192.168.100.1'
nlan.py -t openwrt3 --raw 'ip netns exec ns103 ping -c 1 10.0.1.102'
nlan.py -t openwrt3 --raw 'ip netns exec ns103 ping -c 1 10.0.1.1'
nlan.py -t openwrt2 --raw 'ip netns exec ns103 ping -c 1 10.0.1.1'
nlan.py -t openwrt2 --raw 'ip netns exec ns101 ping -c 1 8.8.8.8'
nlan.py -t openwrt2 --raw 'ip netns exec ns103 ping -c 1 8.8.8.8'
nlan.py -t openwrt3 --raw 'ip netns exec ns101 ping -c 1 8.8.8.8'
nlan.py -t openwrt3 --raw 'ip netns exec ns103 ping -c 1 8.8.8.8'

