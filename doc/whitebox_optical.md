#Whitebox optical simulation

Just an idea...

##Target use case

DCI with whitebox optical transport gears and legacy PE routers

##What is whitebox optical?

Real example: [Cyan N-series](http://www.cyaninc.com/products/n-series-hyperscale-transport)

##Who is promoting this concept?
- Internet content providers operating a very large scale datacenters
- Tier-1 carriers

##Architecture
```
                              E2E orchestrator   HBase, Cassandra, Spark etc         
                                      ^                 ^
                                      |                 | Stream computing
                                      |                 |
                                RESTCONF/YANG     gRPC or Thrift (log/alaram/statistics)
                                      |                 |
                                      V                 |         Clustering
               +------------------------------------------------+               +--
               | Controller node on Docker/CoreOS               | <-- NOSQL --> |
               +------------------------------------------------+  (e.g., etcd) +--
                  [Driver]                             [Driver]
                     ^                                    ^
                     |                                    |
                gRPC/protobuf                        gRPC/protobuf
                     |                                    |
                     V                                    V
               [Agent        ]                       [Agent      ]             
               [Quagga daemon]                            ^
                     ^                                    |
                     |                                    |
                     V                                    V

               <-- PE router -------->          <--- Whitebox optical --->
                                                     (e.g., ROADM)
               . . . . . .
               :         :
          +--+ :         :    +------+            +------+    VXLAN tunnel
[vHost]---|br| : Linux   : O--|      |            |      |  /
[vHost]---|  | : Routing :    |br-int| Tag VLAN   |br-tun|/
          +--+ :         :    |      |============|      |--- VXLAN tunnel
          +--+ :         :    |      |            |      |\
[vHost]---|br| :         : O--|      |            |      |  \
[vHost]---|  | :         :    +------+            +------+    VXLAN tunnel
          +--+ :         :
               . . . . . .
```

##Simulation

|Optical          | VXLAN        |
|-----------------|--------------|
|Color            | VNI          |
|Fiber Cable      | VXLAN tunnel |

##Simulation environment
- Docker (a simulated network on just a single PC)
- Or physical whitebox switches supporting Linux, ONIE, OVS/OVSDB and optical interfaces

##Controller node
- Config: initial config (deployment) and operations
- Path computation for optical
- Policy computation for routers

##Technologies

OpenConfig seems to be the right approach for whitebox optical:
- Protobuf/gRPC as Southbound API ([gRPC-go](https://github.com/grpc/grpc-go) and [gRPC-java](https://github.com/grpc/grpc-java))
- RESTCONF/YANG as Northbound API (use [goyang](https://github.com/openconfig/goyang), [pyangbind](https://github.com/robshakir/pyangbind) and/or ODL/ONOS)
- Python and/or Go lang to implement the agent
- [etcd](https://github.com/coreos/etcd) (or ONOS/ODL distributed datastore) for config sharing among orchestrator nodes
- Quagga/Zebra as routing daemon, Route Reflector and Route Server (PE simulation)
- OSPF for automatic optical topology detection (requires M-Plane for optical)
- Physical wirling by NLAN (initial config)

##OpenConfig
- [Slides by Google at NANOG](https://www.nanog.org/sites/default/files//meetings/NANOG64/1011/20150604_George_Sdn_In_The_v1.pdf)
- [Web site](http://www.openconfig.net/)
- [OpenConfig on github](https://github.com/openconfig)

##etcd

I have an experience on ZooKeeper and felt some problems on it:
- Nested ephemeral nodes unsupported.
- Structure data unsupported: byte[] only.
- Its API is not on HTTP.

etcd seems to be better than ZooKeeper... I need to examine it.

##Kubernetes

[Kubernetes](http://kubernetes.io/) is a new breed of cloud infrastrucutre.

Compared to OpenStack, Kubernetes seems to be light and faster... It includes CoreOS, Dokcer, etcd, Open vSwitch and VXLAN-based overlay networking.

It might be an interesting idea to run the whole SDN/NFV system on Kubernetes...

##FBOSS

Something similar: [FBOSS](https://github.com/facebook/fboss)

##Telemetory

One example is [Cassandra-log4j-appender](https://github.com/datastax/cassandra-log4j-appender) ([and my fork of it](https://github.com/araobp/cassandra-log4j2-appender))

These days, Apache Spark is becoming very active for such a purpose: stream computing.

Note that those are just repositories of time-series data, and you also need to have an analyzer to analyze the data collected from the network.
