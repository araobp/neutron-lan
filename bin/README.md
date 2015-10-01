##docker_ip.py

This script obtains an IP address of a docker container's eth0.
```
$ ./docker_ip openwrt1
```

##docker_mng.py

This script manage Docker containers.

For example, if you want to creates ten Docker containers and manage them:
```
$ ./docker_mng.py openwrt run 10
$ ./docker_mng.py openwrt stop 10
$ ./docker_mng.py openwrt start 10
$ ./docker_mng.py openwrt rm 10
```

##mako_render.py

This script accept a mako template and outputs data.
```
$ ./mako_render.py <mako_template_file>
```

