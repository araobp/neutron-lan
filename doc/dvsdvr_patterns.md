<pre>
Location A                                  Location C

VLAN 1 --+---[GW]--+-- VNI 100 -----[GW]---+-- VLAN 23
         |         |                       |
       [IR]        |                     [IR]
         |         |                       |
VLAN 3 --+---[GW]--- VNI 103 -+-----[GW]---+-- VLAN 27
                   |          |
                   |          |
                 [GW]       [GW]
                   |          |
                   +---[IR]---+
                   |          |
                 VLAN 14    VLAN 15

                    Location B


Location A                                  Location C

VLAN 1 --+---[GW]--+-- VNI 100 -----[GW]---+-- VLAN 23
         |         |                       |
       [IR]        |                     [IR]
         |         |                       |
     X --+---[GW]--- VNI 103 -+-----[GW]---+-- VLAN 27
                   |          |
                   |          |
                 [GW]       [GW]
                   |          |
                   +---[IR]---+
                   |          |
                   X        VLAN 15

                    Location B


Location A                                  Location C

VLAN 1 --+---[GW]--+-- VNI 100 -----[GW]---+-- VLAN 23
         |         |                       |                   (        )
       [IR]-[GW]---------+--VNI 1---[GW]-[IR]--[Internet GW]--( Internet )
         |         |     |                 |                   (        )
VLAN 3 --+---[GW]--- VNI 103 -+-----[GW]---+-- VLAN 27
                   |     |    |
                   |     |    |
                 [GW]  [GW] [GW]
                   |     |    |
                   +---[IR]---+
                   |          |
                 VLAN 14    VLAN 15

                    Location B


Location A                                  Location C

VLAN 1 --+---[GW]--+-- VNI 100 -----[GW]---+-- VLAN 23
         |         |                       |
        [IR ]      |                      [IR ]
         | |NAPT   |                       | |NAPT
VLAN 3 --+---[GW]--- VNI 103 -+-----[GW]---+-- VLAN 27
           |       |          |              |
           |       |          |              |
           |     [GW]       [GW]             |
           |       |          |              |
           V       +---[IR]---+              V
   The Internet    |     |NAPT|          The Internet
                 VLAN 14 |   VLAN 15
                         |
                         V
                    The Internet

</pre>
