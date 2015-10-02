#!/usr/bin/env python3.4

import sys
import subprocess

IMAGE = 'router'  # Docker image name

name = lambda prefix, i: '{}{}'.format(prefix, str(i))
run = lambda prefix, i: ['docker', 'run', '-i', '-t', '-d', '--privileged',
        '--name', name(prefix, i), IMAGE, '/bin/bash']
stop = lambda prefix, i: ['docker', 'stop', name(prefix, i)]
start = lambda prefix, i: ['docker', 'start', name(prefix, i)]
rm = lambda prefix, i: ['docker', 'rm', name(prefix, i)]

cmds = dict(run=run, stop=stop, start=start, rm=rm)

def build_command(command):
    '''
    Closure to build a func for executing a command to manage Docker.
    '''
    def exec(prefix, max_):
        for i in range(1, max_+1):
            subprocess.call(command(prefix, i))
    return exec

if __name__ == '__main__':
    '''
    Usage example:
    $ ./docker_mng.py openwrt1 run 10
    $ ./docker_mng.py openwrt1 stop 10
    $ ./docker_mng.py openwrt1 start 10
    $ ./docker_mng.py openwrt1 rm 10
    '''

    prefix = sys.argv[1]
    ope = sys.argv[2]
    max_ = int(sys.argv[3])
    build_command(cmds[ope])(prefix, max_)

