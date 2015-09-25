# 2014/3/27
# system.py
#

import os
from cmdutil import cmd, check_cmd, output_cmd

def reboot():
    
    return output_cmd('reboot')

def halt():
    
    return output_cmd('halt') 

def service(*args):
    
    scripts = {'networking':{'openwrt': '/etc/init.d/network','raspbian': 'service networking'}}

    script = args[0]
    command = args[1]
    platform = __n__['platform']

    return output_cmd(scripts[script][platform], command)

def rc(args=None):

    platform = __n__['platform']
    share_dir = __n__['share_dir']

    init_script = None 
    command = {} 
    chmod = 'chmod 755 /etc/init.d/nlan'
    if platform == 'debian':
        init_script = os.path.join(share_dir, 'nlan_debian')
        command['enable'] = ['cp {} /etc/init.d/nlan'.format(init_script), chmod, 'update-rc.d nlan defaults']
        command['update'] = ['cp {} /etc/init.d/nlan'.format(init_script)]
        command['disable'] = ['rm /etc/init.d/nlan', 'update-rc.d nlan remove']
        command['status'] = ['ls /etc/rc2.d/']
    elif platform == 'openwrt':
        init_script = os.path.join(share_dir, 'nlan_openwrt')
        command['enable'] = ['cp {} /etc/init.d/nlan'.format(init_script), chmod, '/etc/init.d/nlan enable']
        command['update'] = ['cp {} /etc/init.d/nlan'.format(init_script)]
        command['disable'] = ['/etc/init.d/nlan disable', 'rm /etc/init.d/nlan']
        command['status'] = ['ls /etc/rc.d/']

    if args in command:
        # Caution: this is just a workaround to cope with
        # the situation that OpenWrt's 'enable' always returns
        # exit code = 1, even if it is successful.
        if platform == 'openwrt' and args == 'enable':
            for l in command[args]:
                # Does not raise an exception even if exit code = 1
                cmd(l)
            # Tests if S85nlan exists
            exitcode = check_cmd('test -f /etc/rc.d/S85nlan')
            if exitcode == 0:
                pass
            else:
                raise Exception('system.rc: nlan enable failure')
        else:
            for l in command[args]:
                print output_cmd(l)
    else:
        return "Usage:\nsystem.rc (enable|update|disable|status)"
        

