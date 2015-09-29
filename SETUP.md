#Prerequisites

##NLAN python dependencies

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

##Working with Docker

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

[Step9] Update and enable rc script for nlan
```
$ ./nlan.py system.rc update
$ ./nlan.py system.rc enable
```

[StepX]
Issue: Docker containers change their IP address every time they restart, so /etc/init.d/nlan doe not work properly.
