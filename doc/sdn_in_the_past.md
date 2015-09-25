# SDN in the past

Distributed precessing for scalability (~2000)
--------------------------------------

![co_switch](https://docs.google.com/drawings/d/1_OIm1e-LKiloChkpxHNd1YaNaCVIUbf4mih6Lk2XCxY/pub?w=960&h=720)

- ITU-T
- Duplex: packages, CPUs, memories, system bus ...
- Single thread at each CPU
- Memory synchronization
- Messaging among CPUs via system bus or via signalling with other nodes
- Common memory shared by CPUs via system bus
- Common database shared by CPUs via signalling
- Realtime OS + coroutine-like concurrency + periodic interrput for realtime processing
- Actor-model-like distributed processing for linear scalability
- Abstracted models: calls, connections...
- C-plane: Signalling System No.7
- Signalling = pipelines across the nodes and state machines at each node on the path being setup
- Automatic rollback supported by signalling
- Multi-layers in the node: L1, L2, MTP(L3), SCCP(L4), TCAP(L5), ISUP, INAP ...
- MTP = ip-like, SCCP = tcp/udp-like, TCAP = database-transaction-like
- Periodic audit between layers for state consistency
- Distributed control for basic serivces and centralized control (FT server) for value-added services
- 100% connection-oriented services: connection on demand
- Inflexible bandwidth allocation: 64kbps or 64kbps * 2 + 32kbps
- Call detail record for billing
- Multi-domains or federation: among PBXes and central office switches via trunk

Migration to edge-overlay (2000~)
--------------------------------

![SIP](https://docs.google.com/drawings/d/1x8mm-h4Gxn8rfL7fV-2sgnjpxejSaR8cLfzr9vNJFu4/pub?w=960&h=720)

[The origin of the migration](http://www.cs.columbia.edu/~hgs/papers/Schu9807_Comparison.pdf)

- IETF
- Single-layer: SIP (C-plane) and RTP/RTCP (D-Plane)
- Multi-layer: [SIP, COPS and RSVP](http://www.google.com.ar/patents/US7369536)
- ASCII-based header encoding and MIME-based payload for C-plane
- Edge overlay: RTP/RTCP over data communications (i.e., routers, switched etc)
- State machines distributed to the edge nodes
- Distributed control for basic serivces and centralized control & pubsub for value-added services
- Flexible bandwidth allocations
- Diffserv rather than Intserv
- NAT traversal by ICE/STUN/TURN
- Better CODEC for jitter/packet-loss torellance
- Software CODEC
- Inter-operability problems remained
- Multi-domains or federation: among IP-PBXes (B2BUAs) and carrier SIP serveres via SIP trunk

Migrating to web-based technoliges (2013~)
------------------------------------------

- W3C and IETF
- WebRTC: web server and distributed agents on the browser
- WebSocket and AJAX
- Distributed agents: HTML5, JavaScript and CSS
- State machines distributed to the browsers
- Distributed control for basic serivces and centralized control & pubsub for value-added services
- "Agent on demand" rather than "connection on demand"
- NAT traversal by ICE/STUN/TURN
- 100% software-defined
