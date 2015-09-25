"""
2014/3/17

"""

import os, socket, json

DIST = 'debian'

dumps = None
loads = None
sock = None

if DIST == 'debian':
    dumps = json.dumps
    loads = json.loads
    sock = '/var/run/openvswitch/db.sock'
elif DIST == 'openwrt':
    dumps = json.JsonWriter().write  
    loads = json.JsonReader().read
    sock = '/var/run/db.sock'

s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.connect(sock)

rpc = {
"method":"transact", 
"params":[
    "Open_vSwitch",
    {
        "op": "insert",
        "table": "NLAN",
        "row":  {
            }
    }
    ],
"id": 0
}

s.send(dumps(rpc))
print s.recv(4096)

rpc = {
"method":"transact", 
"params":[
    "Open_vSwitch",
    {
        "op": "insert",
        "table": "NLAN_Subnet",
        "row":  {
            "vid": 101,
            "vni": 1001,
            "ip_dvr": "10.0.0.1/24",
            "ports": ["set", ["eth0", "veth-test"]]
                },
        "uuid-name": "vni1001"
    },{
        "op": "mutate",
        "table": "NLAN",
        "where": [],
        "mutations": [
            [
                "subnets",
                "insert",
                [
                    "set",
                    [
                        [
                            "named-uuid",
                            "vni1001"
                        ]
                    ]
                ]
            ]
        ]
    }
    ],
"id": 1
}

s.send(dumps(rpc))
print s.recv(4096)

rpc = {
"method":"transact", 
"params":[
    "Open_vSwitch",
    {
        "op": "select",
        "table": "NLAN_Subnet",
        "where": [["vni", "==", 1001]]
    }
    ],
"id": 2
}

s.send(dumps(rpc))
print s.recv(4096)

rpc = { 
"method":"transact", 
"params":[
    "Open_vSwitch",
    {
        "op": "update",
        "table": "NLAN_Subnet",
        "where": [["vni", "==", 1001]],
        "row": {"ip_dvr": "10.0.1.2/24"}
    }
    ],
"id": 3
}

s.send(dumps(rpc))
print s.recv(4096)

rpc = {
"method":"transact", 
"params":[
    "Open_vSwitch",
    {
        "op": "select",
        "table": "NLAN_Subnet",
        "where": [["vni", "==", 1001]]
    }
    ],
"id": 4
}

s.send(dumps(rpc))
result = s.recv(4096)
print result
result = loads(result)
uuid_subnet = result["result"][0]["rows"][0]["_uuid"][1]
#print uuid_subnet

rpc = {
"method": "transact",
"params": [
    "Open_vSwitch",
    {
        "op": "mutate",
        "table": "NLAN",
        "where": [],
        "mutations": [
            [
                "subnets",
                "delete",
                [
                    "set",
                    [
                        [
                            "uuid",
                            uuid_subnet
                        ]
                    ]
                ]
            ]
        ]
    }
],
"id": 5
}


#print rpc
s.send(dumps(rpc))
print s.recv(4096)

