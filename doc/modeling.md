YAML-based network modeling
===========================

Model-driven/data-driven approach
---------------------------------

There are several ways for calling a remote python script on the router:
- RPC such as NETCONF or OVSDB (XML-RPC, JSON-RPC etc)
- Mesaging (XMPP, AMQP, 0MP etc)
- SSH
- SIP w/ MIME

Because of the memory/storage limitations of OpenWRT routers, I have adopted SSH (SIP might also be another choice, since several SIP packages for OpenWrt exist).

Then I have considered which one is better, api-driven or model-driven, since I have learned from OpenDaylight about model-driven service abstraction layer (MD-SAL): modeling an inventory of network elements and network topology in YANG data format, and loose coupling between applications and drivers (south-bound APIs).

And I have learned from SaltStack that YAML is a very simple modeling language. Although YANG is the best for modeling network, I would rather take YAML as a neutron-lan modeling language.

YAML for modeling neutron-lan
-----------------------------

Refer to [neutron-lan YAML state file](../etc/state.yaml).

When an administrator has finished modifying the state file, he or she executes a neutron-lan command "nlan.py" to generete CRUD operations (add/delete/set) in the form of Python OrderedDict objects, comparing the file and the one archived in a local git repo.

The OrderedDict objects are serialized into string data and sent to target OpenWRT routers. "nlan_agent.py" deserializes the data, analyzes it and routes the requests to corresponding modules.

               /////////// Global CMDB /////////////                  ////// Local CMDB //////
               Local file             Local git repo                        
               ----------             ----------                            ----------
              /YAML data/ .. diff .. /YAML data/                           / OVSDB   /
             -----------            -----------                           -----------
                              ^                                                 ^
                              |                                                 |
                              |         Serialized into str           (OVSDB protocol)     +--> module A
                              |              ----------                         |          |
                            nlan.py ------ /dict data/ stdin over ssh ---> nlan_agent.py --+--> module B
                              |           -----------                                      |
                              |           CRUD operations                                  +--> module C
                              V       <---- stdout/stderr over ssh -------
                         -----------
                        / Roster   /  
                       ------------
             
Refer to [neutron-lan roster file](../etc/roster.yaml).

"nlan.py" can issue multiple requests to routers in parallel at the same time.

"nlan-agent.py" returns the results to "nlan.py" via stdout/stderr over ssh.

"nlan.py' can also execute raw commands on the routers with '--raw' option, similar to salt-ssh's '-r' option.

The Python dict object will be like this:

<pre>
"OrderedDict([('bridges', {'ovs_bridges': 'enabled'}), ('gateway', {'network': 'eth2', 'rip': 'enabled'}), ('vxlan', {'remote_ips': ['192.168.1.103', '192.168.1.102', '192.168.1.104'], 'local_ip': '192.168.1.101'}), ('subnets', [{'peers': ['192.168.1.102', '192.168.1.103'], 'vid': 2, '_index': ['vni', 1], 'ip_vhost': '192.168.100.101/24', 'vni': 1, 'ip_dvr': OrderedDict([('addr', '192.168.100.1/24'), ('mode', 'dvr')])}, {'peers': ['192.168.1.102', '192.168.1.103'], 'vid': 3, '_index': ['vni', 103], 'ip_vhost': '10.0.3.101/24', 'vni': 103, 'ip_dvr': OrderedDict([('addr', '10.0.3.1/24'), ('mode', 'dvr')])}, {'peers': ['192.168.1.104'], 'vid': 1, '_index': ['vni', 1001], 'ip_vhost': '10.0.1.101/24', 'vni': 1001, 'ip_dvr': OrderedDict([('addr', '10.0.1.1/24'), ('mode', 'hub')])}])])"
</pre>



CRUD operation
--------------
neutron-lan defines the following CRUD operations:
- "add": Create
- "get": Read
- "update": Update
- "delete": Delete

[yamldiff.py](https://github.com/araobp/neutron-lan/blob/master/nlan/yamldiff.py) is responsible for generating CRUD operations.

nlan_ssh.py's "--scpmod" option allows me to copy the nlan modules to the target router's "/opt/nlan" directory.

     Step 1:
     
                         ---------------              Target routers
     [nlan.py] ---------/Python scripts/-----------> "/opt/nlan" directory
                        --------------- /
                        ----------------
                               :
                          
     Step 2:
     
                 stdin  ---------------              Target routers
    [nlan.py] ---------/Python dict   / - - - - - > Agent-scripts under "/opt/nlan" 
                      ---------------
                  < - - - - - - - - - - - - stdout
                  < - - - - - - - - - - - - stderr



rpc modules and config modules
------------------------------

Neutron-lan modules are categolized into two categories:

Category 1: rpc modules (like SaltStack execution modules):
- init
- system
- test
- (other modules to be added)

For example, the following will reboot all the routers on the roster: 
<pre>
$ python nlan.py system.reboot 
</pre>

Category 2: config modules (like SaltStack state modules):
- bridges
- services
- gateway
- vxlan
- subnets
- (other modules to be added) 

nlan.py reads a YAML file and invoke corresponding config modules on remote routers:
<pre>
$ python nlan.py dvsdvr.yaml
</pre>

To support CRUD operations, each config module should implement "add", "get", "update" and "delete" functions in it.

For example,
- "init.run()" initializes the local system setting
- "bridges.add(...)" adds bridges required for neutron-lan

The config modules interworks with OVSDB (Open vSwtich Database) to create/read/update/delete local config, and my plan is to write a script that reads the config in OVSDB to re-configure the system when rebooting.

OVSDB schema for neutron-lan is defined [in this page](https://github.com/araobp/neutron-lan/blob/master/doc/ovsdb-schema.md)

All the way from YAML to OVSDB
------------------------------

The following command reads a local YAML file, generates CRUD operations and invokes modules at each router:
<pre>
$ python nlan.py dvsdvr.yaml
</pre>

Each remote module stores its 'model' in OVSDB at the end of the configuration process.

Here is a sample output of 'ovsdb-client dump Open_vSwitch':

At "rpi1",
<pre>
$ ovsdb-client dump Open_vSwitch

NLAN table
_uuid                                bridges                              gateway services                               subnets
                              vxlan
------------------------------------ ------------------------------------ ------- -------------------------------------- -----------------------------------------------
----------------------------- ------------------------------------
2995e0c6-1580-4fdf-91e3-fe23e4c5eaa5 f7599b4b-ed10-4de3-8ddc-633b6c72138d []      [041ac945-ddc1-4e7b-b04f-68bfaf990596] [79fe5fe6-4181-44f1-86a5-107ce7c7c8c9, ccb8a49f
-6645-4f61-87f1-f0bb6db1522b] 73d29aef-ed68-4d40-bfcc-8c08edf57b05

NLAN_Bridges table
_uuid                                controller ovs_bridges
------------------------------------ ---------- -----------
f7599b4b-ed10-4de3-8ddc-633b6c72138d []         enabled

NLAN_Gateway table
_uuid network rip
----- ------- ---

NLAN_Service table
_uuid                                chain                  name
------------------------------------ ---------------------- --------
041ac945-ddc1-4e7b-b04f-68bfaf990596 ["dmz.1001", "mz.101"] "snort1"

NLAN_Subnet table
_uuid                                default_gw ip_dvr ip_vhost peers                              ports        vid vni
------------------------------------ ---------- ------ -------- ---------------------------------- ------------ --- ----
ccb8a49f-6645-4f61-87f1-f0bb6db1522b []         {}     []       ["192.168.1.101"]                  ["dmz.1001"] 111 1001
79fe5fe6-4181-44f1-86a5-107ce7c7c8c9 []         {}     []       ["192.168.1.102", "192.168.1.103"] ["mz.101"]   1   101

NLAN_VXLAN table
_uuid                                local_ip        remote_ips
------------------------------------ --------------- ---------------------------------------------------
73d29aef-ed68-4d40-bfcc-8c08edf57b05 "192.168.1.104" ["192.168.1.101", "192.168.1.102", "192.168.1.103"]
</pre>


At "openwrt1",
<pre>
$ ovsdb-client dump Open_vSwitch

NLAN table
_uuid                                bridges                              gateway                              services subnets
                                                                    vxlan
------------------------------------ ------------------------------------ ------------------------------------ -------- -----------------------------------------------
------------------------------------------------------------------- ------------------------------------
f41f2732-c9a0-42ef-a72f-3275ec79c13d 90af6783-f57c-418f-8102-6e02e30d1427 1b3f608c-9a3e-4c4a-9b7c-9805cb8d0d69 []       [3965d784-b309-4d64-b700-396d1ad0a2a4, 53cc4e84
-db7b-4a1e-9d02-df29fa5d9afc, aa54b72e-a22c-47a6-8c0f-c537da6fa8cf] 88d7ad5f-158f-437e-9169-78f79d2e38d5

NLAN_Bridges table
_uuid                                controller ovs_bridges
------------------------------------ ---------- -----------
90af6783-f57c-418f-8102-6e02e30d1427 []         enabled

NLAN_Gateway table
_uuid                                network rip
------------------------------------ ------- -------
1b3f608c-9a3e-4c4a-9b7c-9805cb8d0d69 "eth2"  enabled

NLAN_Service table
_uuid chain name
----- ----- ----

NLAN_Subnet table
_uuid                                default_gw ip_dvr                              ip_vhost             peers                              ports vid vni
------------------------------------ ---------- ----------------------------------- -------------------- ---------------------------------- ----- --- ----
53cc4e84-db7b-4a1e-9d02-df29fa5d9afc []         {addr="10.0.1.1/24", mode=hub}      "10.0.1.101/24"      ["192.168.1.104"]                  []    1   1001
3965d784-b309-4d64-b700-396d1ad0a2a4 []         {addr="10.0.3.1/24", mode=dvr}      "10.0.3.101/24"      ["192.168.1.102", "192.168.1.103"] []    3   103
aa54b72e-a22c-47a6-8c0f-c537da6fa8cf []         {addr="192.168.100.1/24", mode=dvr} "192.168.100.101/24" ["192.168.1.102", "192.168.1.103"] []    2   1

NLAN_VXLAN table
_uuid                                local_ip        remote_ips
------------------------------------ --------------- ---------------------------------------------------
88d7ad5f-158f-437e-9169-78f79d2e38d5 "192.168.1.101" ["192.168.1.102", "192.168.1.103", "192.168.1.104"]
</pre>


At "openwrt2",
<pre>
$ ovsdb-client dump Open_vSwitch

NLAN table
_uuid                                bridges                              gateway services subnets
                                       vxlan
------------------------------------ ------------------------------------ ------- -------- ----------------------------------------------------------------------------
-------------------------------------- ------------------------------------
03a6b672-1ad4-449f-ab8d-d17a51855afe 741f89be-7827-4c35-b29b-6aeb265989bf []      []       [0ac15551-cb16-496c-ad4e-d013648ca07f, 730ac859-68e7-45c1-b0cd-f7238a3cbcbb,
 a691eb74-d0ab-469d-ab51-87019d59442c] 5bf6be90-c856-4a41-a271-4e1476f67132

NLAN_Bridges table
_uuid                                controller ovs_bridges
------------------------------------ ---------- -----------
741f89be-7827-4c35-b29b-6aeb265989bf []         enabled

NLAN_Gateway table
_uuid network rip
----- ------- ---

NLAN_Service table
_uuid chain name
----- ----- ----

NLAN_Subnet table
_uuid                                default_gw      ip_dvr                               ip_vhost             peers                              ports vid vni
------------------------------------ --------------- ------------------------------------ -------------------- ---------------------------------- ----- --- ---
a691eb74-d0ab-469d-ab51-87019d59442c []              {addr="10.0.1.1/24", mode=spoke_dvr} "10.0.1.102/24"      ["192.168.1.103", "192.168.1.104"] []    1   101
730ac859-68e7-45c1-b0cd-f7238a3cbcbb []              {addr="10.0.3.1/24", mode=dvr}       "10.0.3.102/24"      ["192.168.1.101", "192.168.1.103"] []    3   103
0ac15551-cb16-496c-ad4e-d013648ca07f "192.168.100.1" {addr="192.168.100.2/24", mode=dvr}  "192.168.100.102/24" ["192.168.1.101", "192.168.1.103"] []    2   1

NLAN_VXLAN table
_uuid                                local_ip        remote_ips
------------------------------------ --------------- ---------------------------------------------------
5bf6be90-c856-4a41-a271-4e1476f67132 "192.168.1.102" ["192.168.1.101", "192.168.1.103", "192.168.1.104"]
</pre>

