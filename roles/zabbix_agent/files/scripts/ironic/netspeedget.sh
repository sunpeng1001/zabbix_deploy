#!/bin/bash
speed_=`cat /sys/class/net/$1/speed 2>/dev/null`
speed=${speed_:=10000}
echo $(($speed*1024*1024))
