# 2014/3/3
# 2014/3/17
# gateway.py
#
# Quagga manipulation module 
#

from cmdutil import output_cmd, output_cmd2, output_cmdp, output_cmd2p
from ovsdb import Row
from errors import ModelError

def _vtysh(args):
    cmd_args = ['vtysh'] 
    for line in args.split('\n')[1:-1]:
        cmd_args.append('-c')
        cmd_args.append(line.lstrip())
    try:
        output_cmd2p(cmd_args)
    # Fails if zebrad and ripd have not been started yet.
    except:
        output_cmdp('/etc/init.d/quagga start')
        output_cmd2p(cmd_args)
        output_cmdp('/etc/init.d/quagga restart')

def add():

    if not _rip or not _network:
        raise ModelError('requires both _rip and _network')

    else:
        __n__['logger'].info('Adding a gateway router: rip')

        args = """
        configure terminal
        interface {0}
        link-detect
        exit
        router rip
        version 2
        redistribute connected
        network {0}
        exit
        exit
        write
        exit
        """.format(_network)

        _vtysh(args)


def delete():

    if not _rip or not _network:
        raise ModelError('requires both _rip and _network')
    
    else:
        __n__['logger'].info('Deleting a gateway router: rip')

        args = """
        configure terminal
        interface {0}
        no link-detect
        exit
        router rip
        no version 2
        no redistribute connected
        no network {0}
        exit
        exit
        write
        exit
        """.format(_network)

        _vtysh(args)


def update():

    if not rip_ or not _network:
        raise ModelError('requires rip_ and _network')
    
    else:
        __n__['logger'].info('Updating a gateway router: rip')

        args = """
        configure terminal
        interface {0}
        no link-detect
        exit
        interface {1}
        link-detect
        exit
        router rip
        no network {0}
        network {1}
        exit
        exit
        write
        exit
        """.format(network_, _network_)

        _vtysh(args)
        
