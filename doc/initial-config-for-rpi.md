<pre>
$ apt-get install bridge-utils
$ apt-get install tcpdump
$ apt-get install gdebi
</pre>

To install openvswitch 2.0.0 on Debian Wheezy, follow the instructions on the following page:
http://www.forwardingplane.net/2013/11/openvswitch-2-0-debian-packages/

Some useful links:
* [Raspbian](http://www.raspberrypi.org/downloads)
* [Linux headers](http://www.raspberrypi.org/forums/viewtopic.php?f=71&t=17666)

<pre>
IPv6 seems to be disabled on Raspbian. So, the following config will not be necessary...

$ /etc/sysctl.conf
net.ipv4.ip_forward=1
net.ipv6.conf.all.disable_ipv6 = 1
net.ipv6.conf.default.disable_ipv6 = 1
net.ipv6.conf.lo.disable_ipv6 = 1

$ sysctl -p
</pre>
