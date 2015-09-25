Blueprint
=========

Background
----------

* I have already built lxc-capable OpenWrt and Raspbian kernel.


Plan
----

* Rebuilt OpenWrt image for x86 and lxc command utilities.
* Isolate the process by using lxc-execute/lxc-init.

          OpenWrt/Debian/Raspbian
	  +-------------------------------+
          |           : lxc-execute/init  |
	  | Other     : +---------------+ |
	  | processes : | nlan_agent.py | |
	  |           : +---------------+ |
	  +-------------------------------+
          | Operating System              |
          +-------------------------------+

Limit the cpu and memory usage.

