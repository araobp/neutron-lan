#Prerequisites

##Python dependencies

- python2.7
- pyyaml
- paramiko
- scp
- layered-yaml-attrdict-config==12.06.2

##Open vSwitch installation

```
$wget http://openvswitch.org/releases/openvswitch-2.4.0.tar.gz
```
Follow the instructions included in the archive.

NLAN requires "dkms", "common" and "switch" only. Use dpkg command (dpkg -i) to install the deb packages.

##Working with OpenWrt

NLAN supports openwrt, raspbian and debian(ubuntu) platforms.

The latest OpenWrt release support Open vSwtich.

##Working with Docker

[Step1] Create an image of Debian/Ubuntu with Open vSwitch installed

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

[Step6] Ping test
```
$ ./nlan.py -w 10 -v
```

[Step7] Copy NLAN Agent to the Docker containers
```
$ ./nlan.py -m -v
```

[Step8] Update OVSDB schema on the Docker containers
```
$ ./schema.sh
$ ./nlan.py db.update -v
```
