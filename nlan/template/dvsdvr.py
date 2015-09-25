# 2014/04/03
# 2014/07/06 Handling multiple <local ip> in VXLAN model
#
import re
from yamldiff import *
from env import STATE_ORDER, ROSTER

# Placeholders: <local_ip>, <remote_ips>, <peers> and <sfports>

TYPES = {'<local_ip>': str, '<remote_ips>': str, '<peers>': str, '<sfports>': str} 

def placeholder_types():
    return TYPES
    
def fillout(slist):

    ips = {}
    vnis = {}
    chain = {}
    
    for l in slist:
        if re.search('vxlan\[local_ip|local_ip', l):
            router = get_node(l)
            ips[router] = ROSTER[router]['host']
        if re.search('vid=', l):
            router = get_node(l)
            vni = get_index_value(l)
            if vni not in vnis:
                vnis[vni] = []
            vnis[vni].append(router)
        if re.search('chain=', l):
            router = get_node(l)
            chain[router] = get_value(l)

    # Placeholders
    local_ip = {}
    remote_ips = {}
    peers = {}
    sfports = {}

    for router in ips.keys():
        remote_ips[router] = []
        peers[router] = {}
        for r in ips.keys():
            if r != router:
                remote_ips[router].append(ips[r])
        for vni in vnis.keys():
            l = list(vnis[vni])
            if router in l:
                l.remove(router)
                for r in l:
                    l[l.index(r)] = ips[r]
                peers[router][vni] = l

    for router in chain.keys():
        sfports[router] = {}
        for path in chain[router]:
            p = path.split('.')
            peer_router = p[0]
            vni = int(p[1])
            sfports[router][vni] = [path] 

    tl = Template(slist)
    tl.add_values('local_ip', ips, False)
    tl.add_values('remote_ips', remote_ips, False)
    tl.add_values('peers', peers, True)
    tl.add_values('sfports', sfports, True)

    return tl.fillout()

