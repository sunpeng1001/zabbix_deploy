#!/bin/bash
speed=`cat /sys/class/net/$1/speed`
echo $(($speed*1024*1024))
