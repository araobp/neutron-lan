#!/bin/bash
# 2014/5/20

url=http://192.168.56.101:8080

unset http_proxy

request () {

    echo "/////" $1 $2 $3 "/////"
    echo curl -s -H Content-Type:application/json -X $1 $url$2?$3
    curl -s -H Content-Type:application/json -X $1 $url$2?$3 | json_pp 
    #curl -s -H Content-Type:application/json -X $1 $url$2?$3 

}

request POST /_ALL/rpc/test/echo params=Hello!
request OPTIONS "" params=subnets
request POST /openwrt1/rpc/init/run
request POST /openwrt1/config/bridges ovs_bridges=enabled
request POST /openwrt1/config/vxlan local_ip=192.168.1.101\&remote_ips=192.168.1.102,192.168.56.103
request GET /openwrt1/config/vxlan
request PUT /openwrt1/config/vxlan remote_ips=192.168.1.102,192.168.56.104
request GET /openwrt1/config/vxlan params=remote_ips
request DELETE /openwrt1/config/vxlan params=remote_ips
request POST /openwrt1/rpc/db/state 

