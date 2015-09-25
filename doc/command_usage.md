NLAN Command Usage
==================

DevOps operations
-----------------
<pre>
- copy NLAN Agent and NLAN modules to remote routers
$ nlan.py -m

- enable the rc script (/etc/init.d/nlan)
$ nlan.py system.rc enable

- update the rc script (/etc/init.d/nlan)
$ nlan.py system.rc update 

- update OVSDB(conf.db) with new schema
$ nlan.py db.update

- deploy a network service with a default state file
$ nlan.py deploy 

- deploy a network service with a default state file and with verbose output
$ nlan.py -v deploy

- deploy a network service with a specific state file (e.g., 'state.yaml')
$ nlan.py state.yaml 

- deploy network service with logging enabled (either --info or --debug)
$ nlan.py dvsdvr.yaml --info

- execute a raw command at remote routers (e.g., ping)
$ nlan.py -t openwrt1 --raw 'ping -c4 192.168.1.10'

- execute a raw command at all the routers on the roster
$ nlan.py --raw 'ping -c4 192.168.1.10'

- wait until all the routers on the roster become accessible (-w <timeout>)
$ nlan.py -w 100

- wait until all the routers on the roster become inaccessible (-w -<timeout>)
$ nlan.py -w -50 
</pre>

Working with a local Git repo
------------------------------
<pre>
- deploy a network service with a default state file (the state file is commited to the local git repo after the deployment)
$ nlan.py -G deploy 

- rollback to the previous state
$ nlan.py init.run
$ nlan.py -R deploy
</pre>

CRUD operations (using nlan.py)
-----------------------------------------
<pre>
print a list of modules
$ nlan.py -s

print a schema for the module
$ nlan.py -s subnets

CRUD
$ nlan.py --add bridges ovs_bridges=enabled
$ nlan.py -t openwrt1 --add vxlan local_ip=192.168.1.101 remote_ips=192.168.1.102,192.168.1.103
$ nlan.py -t openwrt1 --add subnets _index=10 vid=1 vni=10
$ nlan.py -t openwrt1 --add subnets _index=10 ip_dvr=addr:10.0.1.9/24,mode:dvr
$ nlan.py -t openwrt1 --update subnets _index=10 ip_dvr=addr:10.0.1.1/24,mode:dvr
$ nlan.py -t openwrt1 --add subnets _index=10 ip_vhost=10.0.1.101/24
$ nlan.py -t openwrt1 --delete subnets _index=10 ip_vhost=10.0.1.101/24
$ nlan.py -t openwrt1 --get subnets _index=10 ip_dvr 
$ nlan.py -t openwrt1 --get subnets _index=10
$ nlan.py -t openwrt1 --get subnets
</pre>

Local CRUD operations (w/o using nlan.py)
-----------------------------------------
<pre>
print a list of modules
$ nlan_agent.py -s

print a schema for the module
$ nlan_agent.py -s subnets

CRUD
$ nlan_agent.py --add bridges ovs_bridges=enabled
$ nlan_agent.py --add vxlan local_ip=192.168.1.101 remote_ips=192.168.1.102,192.168.1.103
$ nlan_agent.py --add subnets _index=10 vid=1 vni=10
$ nlan_agent.py --add subnets _index=10 ip_dvr=addr:10.0.1.9/24,mode:dvr
$ nlan_agent.py --update subnets _index=10 ip_dvr=addr:10.0.1.1/24,mode:dvr
$ nlan_agent.py --add subnets _index=10 ip_vhost=10.0.1.101/24
$ nlan_agent.py --delete subnets _index=10 ip_vhost=10.0.1.101/24
$ nlan_agent.py --get subnets _index=10 ip_dvr 
$ nlan_agent.py --get subnets _index=10
$ nlan_agent.py --get subnets
</pre>


Scenario Runner
---------------
<pre>
- execute a scenario (e.g., a scenario 'all.yaml')
$ nlans.py all.yaml
</pre>

MIME Multipart output
---------------------
<pre>
$ nlan.py --mime --debug --verbose <other options/arguments>
</pre>

Maintenance
-----------
<pre>
- echo test
$ nlan.py test.echo Hello World!

- show rpc list
$ nlan.py rpc.list

- ping test 
$ nlan.py test.ping 192.168.1.10

- shutdown all the routers
$ nlan.py system.halt

- reboot all the routers
$ nlan.py system.reboot

- show NLAN Agent environment(shows built-in "__n__" variable)
$ nlan.py nlan.env

- show the current NLAN state in OVSDB
$ nlan.py db.state

- show the current NLAN state in OVSDB at a specific router
$ nlan.py -t openwrt1 db.state

- show a specific NLAN row in OVSDB (e.g., subnets vni=101)
$ nlan.py db.getrow subnets vni 101
</pre>


NLAN schema update
------------------
<pre>
Update 'env.py' and 'schema.sh' at first. Then,
$ schema.sh
$ nlan -m
$ nlan db.update 

Do not forget to update env.py either.
</pre>


Using NLAN REST APIs
--------------------
<pre>
$ curl -s -H Content-Type:application/json -X POST http://192.168.56.101:8080/_ALL/rpc/test/echo?params=Hello!
$ curl -s -H Content-Type:application/json -X OPTIONS http://192.168.56.101:8080?params=subnets
$ curl -s -H Content-Type:application/json -X POST http://192.168.56.101:8080/openwrt1/rpc/init/run
$ curl -s -H Content-Type:application/json -X POST http://192.168.56.101:8080/openwrt1/config/bridges?ovs_bridges=enabled
$ curl -s -H Content-Type:application/json -X POST http://192.168.56.101:8080/openwrt1/config/vxlan?local_ip=192.168.1.101&remote_ips=192.168.1.102,192.168.56.103
</pre>

