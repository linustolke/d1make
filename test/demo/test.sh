#!/bin/sh

D1MAKE_HOSTS="localhost 127.0.0.1" \
D1MAKE_CLIENT_MAKEARGS="-j12" ../../d1make.py -j2 all
