#!/bin/sh
#dockerでmongodを起動する

docker run -p 28001:27017 \
-v /home/mima/work/moviebrowser/static/db:/data/db \
--name dev-mongo -d  mongo
