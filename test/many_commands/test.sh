#!/bin/sh

D1MAKE_EXTRA_SSH_PARAMETERS="-F $PWD/ssh_config" \
D1MAKE_SSH_CTL_PATH="/tmp/ssh_ctl_path$$-%n-%h" \
D1MAKE_HOSTS=${D1MAKE_HOSTS-localhost1 localhost2 localhost3 localhost4 localhost5 localhost6 localhost7 localhost8 localhost9 localhost10 localhost11 localhost12 localhost13 localhost14 localhost15 localhost16 localhost17 localhost18 localhost19 localhost20 localhost21} \
	    D1MAKE_CLIENT_MAKEARGS=${D1MAKE_CLIENT_MAKEARGS--j12} \
	    ../../d1make.py ${MAKEARGS--j30} all
