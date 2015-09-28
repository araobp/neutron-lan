Use of OVSDB in NLAN 
--------------------

OVSDB is used for storing local config parameters, so that the NLAN-related config survives after rebooting the system.


NLAN tables in OVSDB
--------------------

<pre>
NLAN
  | 
  +-- bridges -- NLAN_Bridges
  |   
  +-- services* -- NLAN_Service
  |
  +-- gateway -- NLAN_Gateway
  |
  +-- vxlan -- NLAN_VXLAN
  |
  +-- subnets* -- NLAN_Subnet
</pre>

Note that "NLAN" is a root-set table, so "isRoot" in the schema definion is set to "true".

OVSDB NLAN schema in YAML
-------------------------

The original OVSDB schema(JSON) can be converted into YAML using some python libraries or vise versa.

**NLAN schema is written in YAML format.** The schema is merged with the original OVSDB schema(JSON) by using "nlan_schema.py" utility, and NLAN Agent uses the schema(JSON) for storing/fetching NLAN state to/from OVSDB.

	     ______________
	    /             /
	   / NLAN schema / --------------+
	  / in YAML     /                |
	 --------------          Merge   +--------> New OVSDB schema that Open vSwitch and NLAN Agent use
	     ______________              |
	    /             /              |
	   /OVSDB schema /---------------+
	  / in JSON     /
	 --------------

* [Original OVSDB schema converted into YAML](https://github.com/araobp/neutron-lan/blob/master/ovsdb/vswitch.schema_2.0.0.yaml)
* [NLAN schema in YAML](https://github.com/araobp/neutron-lan/blob/master/nlan/agent/share/nlan.schema_0.0.6.yaml)
* [O/R mapper for OVSSB](https://github.com/araobp/neutron-lan/blob/master/nlan/agent/ovsdb.py)


NLAN state file in YAML
-----------------------

Actual NLAN state parameters are written in the following file:

* [state.yaml](https://github.com/araobp/neutron-lan/blob/master/etc/state.yaml)

NLAN state file can work with a custom-made template engine as is indicated at the top line in the file: "#!template.dvsdvr"


OVSDB test client
-----------------

I have already written a [OVSDB O/R mapper](https://github.com/araobp/neutron-lan/blob/master/nlan/agent/ovsdb.py) exclusively for neutron-lan.

Before that, I wrote a python script [ovsdb-test-script.py](https://github.com/araobp/neutron-lan/blob/master/ovsdb/ovsdb-test-client.py) to test the new OVSDB schema.


id=0, insert rows into "NLAN" table:
<pre>
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
</pre> 

id = 1, insert "NLAN_Subnet" rows:
<pre>
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
</pre>

id=2, select rows where "vni=1001" in "NLAN_Subnet" table:
<pre>
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
</pre>

id=3, update "ip_dvr" where "vni=1001" in "NLAN_Subnet" table：
<pre>
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
</pre>

id=4, select rows where "vni=1001" in "NLAN_Subnet" table：
<pre>
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
</pre>

id=5, delete rows in "NLAN_Subnet" table(the value of "uuid_subnet" is from the result of id=4 transaction)：
<pre>
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
</pre>

Transaction sequence chart:

    OVSDB              JSON-RPC client
       |                      |
       | id=0, insert         |
       |<---------------------|
       | result               |
       |--------------------->|
       | id=1, insert/mutate  |
       |<---------------------|
       | result               |
       |--------------------->|
       | id=2, select         |
       |<---------------------|
       | result               |
       |--------------------->|
       | id=3, update         |
       |<---------------------|
       | result               |
       |--------------------->|
       | id=4, select         | 
       |<---------------------|
       | result               |
       |--------------------->|
       | id=5, mutate         | 
       |<---------------------|
       | result               |
       |--------------------->|
       |                      |
       

Then I have executed the test script "ovsdb-test-client.py"：
<pre>
root@debian:~/neutron-lan/ovsdb# python ovsdb-test-client.py
{"id":0,"error":null,"result":[{"uuid":["uuid","57b0cdc6-c6bf-4899-8676-b529ce79a334"]}]}
{"id":1,"error":null,"result":[{"uuid":["uuid","5b87e1c6-64cf-49ff-93e1-9c41e9c08014"]},{"count":1}]}
{"id":2,"error":null,"result":[{"rows":[{"_uuid":["uuid","5b87e1c6-64cf-49ff-93e1-9c41e9c08014"],"ip_vhost":"","ports":["set",["eth0","veth-test"]],"ip_dvr":"10.0.0.1/24","vid":101,"_version":["uuid","5012ff9e-6aa5-4019-a15f-5e85add28b7b"],"vni":1001}]}]}
{"id":3,"error":null,"result":[{"count":1}]}
{"id":4,"error":null,"result":[{"rows":[{"_uuid":["uuid","5b87e1c6-64cf-49ff-93e1-9c41e9c08014"],"ip_vhost":"","ports":["set",["eth0","veth-test"]],"ip_dvr":"10.0.1.2/24","vid":101,"_version":["uuid","4b5ae6e8-f57c-4914-bdcc-7ee0ea894f57"],"vni":1001}]}]}
{"id":5,"error":null,"result":[{"count":1}]}
</pre>
