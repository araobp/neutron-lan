#!/bin/bash

export PATH=$PATH:../../nlan

nlan.py init.run
nlan.py -v --add bridges ovs_bridges=enabled
nlan.py -v -t openwrt1 --add gateway rip=enabled network=eth2
nlan.py -v -t openwrt1 --add vxlan local_ip=192.168.1.101 remote_ips=192.168.1.102,192.168.1.103
nlan.py -v -t openwrt1 --add subnets _index=10 vid=1 vni=10
nlan.py -v -t openwrt1 --add subnets _index=10 ip_dvr=addr:10.0.1.9/24,mode:dvr
nlan.py -v -t openwrt1 --update subnets _index=10 ip_dvr=addr:10.0.1.1/24,mode:dvr
nlan.py -v -t openwrt1 --add subnets _index=10 ip_vhost=10.0.1.101/24
nlan.py -v -t openwrt1 --delete subnets _index=10 ip_vhost
nlan.py -v -t openwrt1 --get subnets _index=10 ip_vhost ip_dvr
nlan.py -v -t openwrt1 --get subnets _index=10
nlan.py -v -t openwrt1 --get subnets


