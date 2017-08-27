#!/bin/bash

if [ ! -d redis-stable/src ]; then
    curl -O http://download.redis.io/redis-stable.tar.gz
    tar xvzf redis-stable.tar.gz
    rm redis-stable.tar.gz
	cd redis-stable
    make
fi

./redis-stable/src/redis-server &
