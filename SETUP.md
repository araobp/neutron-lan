#Prerequisites

##NLAN python dependencies

- python2.7
- pyyaml
- paramiko
- scp
- layered-yaml-attrdict-config==12.06.2
- mako

##Open vSwitch installation

```
$wget http://openvswitch.org/releases/openvswitch-2.4.0.tar.gz
```
Follow the instructions included in the archive.

NLAN requires "dkms", "common" and "switch" only. Use dpkg command (dpkg -i) to install the deb packages.

##Working with Docker

![working_with_docker](https://docs.google.com/drawings/d/161Bn80w8JZKQ7BXmIo0br7xQ4kqEdBc_XZ254zuORSU/pub?w=680&h=400)

[Step1] Create an image of Debian/Ubuntu with Open vSwitch installed

You need to copy the following deb packages to the Docker containers:
- openvswitch-switch_*.deb
- openvswitch-common_*.deb

Then "dpkg -i" to install them.

[Step2] Allow ssh root login to the Docker container
```
/etc/ssh/ssh_config

#PermitRootLogin wihtout-password
PermitRootLogin yes
```

[Step3] Append the following lines to $HOME/.bashrc
```
/etc/init.d/ssh start
/etc/init.d/openvswitch-switch start
if [ -f /opt/nlan/nlan_agent.py ]
then
    cd /opt/nlan
    python nlan_agent.py init.run false
else
    echo "nlan_agent.py not found."
fi
nlan_rc="/etc/init.d/nlan"
if [ -f "$nlan_rc" ]
then
    /etc/init.d/nlan start
else
    echo "$nlan_rc not found."
fi
```

[Step4] Create Docker containers

For example, if the image name is 'router' then:
```
$ docker run -t -i --privileged=true --name router1 router /bin/bash
$ docker run -t -i --privileged=true --name router2 router /bin/bash
$ docker run -t -i --privileged=true --name router3 router /bin/bash
                           :
```

[Step5] Start Docker containers
```
$ docker start router1
$ docker start router2
$ docker start router3
         :
```

[Step6] Add a secondary IP address to Docker container

Include "docker: true" in your roster file:
```
openwrt1:
    host: 172.18.0.1
    user: root
    password: root
    platform: debian
    docker: true
       :
```

And also Include "command..." in your state file:
```
openwrt1:
    command:
      command:
         - ip address add <local_ip>/16 dev eth0
           :
```

Then execute the following command:
```
$ sudo ip address add 172.18.42.1/16 dev docker 0
$ ./nlan.py -S
```

Confirm that those secondary IP addresses have been correctly set to the containers. For example, if a container's name is "router1" then:
```
$ docker attach router1
$ ip addr show
$ ip route show
```

[Step7] Ping test
```
$ ./nlan.py -w 10 -v
```

[Step8] Copy NLAN Agent to the Docker containers
```
$ ./nlan.py -m -v
```

[Step9] Update OVSDB schema on the Docker containers
```
$ ./schema.sh
$ ./nlan.py db.update -v
```

[Step10] Update and enable rc script for nlan
```
$ ./nlan.py system.rc enable_docker
```

[Step11] Deploy your network

For example,
```
$ ./nlan.py docker_openflow.yaml
```

[Step12(optional)] Flush arp table

When you restart (stop/start) those Docker containers, NLAN agent (nlan_agent.py) will automatically resume the config by reading the previous state from OVSDB.

You might face a problem that you cannot get access to those containers with the secondary IP addresses: In that case, you need to flush the arp table for the containers with this command:
```
$ ./nlan.py -F
```

Enjoy!

##Working with Docker without setting secondary IP addresses


Include "<docker_ip>" in your roster file:
```
openwrt1:
    host: <docker_ip> 
    user: root
    password: root
    platform: debian
       :
```
NLAN master (nlan.py) replaces the placeholder <docker_ip> with the container's IP address (i.e., 172.17.42.X).

Note that NLAN Agent's config-auto-resume feature does not work if you don't set secondary IP addresses to the containers.


