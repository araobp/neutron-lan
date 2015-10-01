#Whitebox optical

Just an idea...

##Target use case

DCI with whitebox optical transport gears and legacy PE routers

##Architecture
```
                                      ^
                                      |
                                RESTCONF/YANG
                                      |
                                      V                            Clustering
               +------------------------------------------------+               +--
               | Orchestrator                                   | <-- NOSQL --> |
               +------------------------------------------------+               +--
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
----------------------------------
|Color            | VNI          |
|Fiber Cable      | VXLAN tunnel |

##Technologies

OpenConfig seems to be the right approach for whitebox optical:
- Protobuf/gRPC as Southbound API
- RESTCONF/YANG as Northbound API
- Go lang to implement the agent
- etcd (or ONOS/ODL distributed datastore) for config sharing among orchestrator nodes
- Quagga/Zebra as routing daemon, Route Reflector and Route Server (PE simulation)
- OSPF for automatic optical topology detection (requires M-Plane for optical)
- Physical wirling by NLAN (initial config)

