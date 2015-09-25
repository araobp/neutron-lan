# 2014/4/18
# db.py
#

import cmdutil
import os
import ovsdb

# Update OVSDB Schema with NLAN-related addition
def update():

    cmd = cmdutil.cmd
    platform = __n__['platform']
    schema = os.path.join(__n__['share_dir'], __n__['schema'])
    stop = None
    start = None

    if platform == 'openwrt':
        cmd('/etc/init.d/openvswitch stop')
        cmd('ovsdb-tool convert /etc/openvswitch/conf.db', schema)
        cmd('cp /etc/openvswitch/conf.db /etc/openvswitch/conf.db.old')
        cmd('/etc/init.d/openvswitch start')
    elif platform == 'debian' or platform == 'raspbian':
        cmd('service openvswitch-switch stop')
        cmd('cp', schema, '/usr/share/openvswitch/vswitch.ovsschema')
        cmd('service openvswitch-switch start')


def getrow(*args):
    Row = ovsdb.Row
    module = args[0]
    index = None
    if len(args) > 1:
        v = args[2]
        try:
            v = eval(v)
            if isinstance(v, int):
                index = (args[1], eval(args[2]))
        except:
            index = (args[1], args[2]) 
    row = Row(module, index)
    return row.getrow()


def state():
    return ovsdb.get_current_state() 
