#!/bin/bash
diskarray=(`df -l | grep "^/dev*" | awk '{ print $1 }' 2>/dev/null`)
osdarray=(`df -l | grep "^/dev*" | awk '{ print $6 }' 2>/dev/null`)
length=${#diskarray[@]}
printf "{\n"
printf  '\t'"\"data\":["
for ((i=0;i<$length;i++))
do
         printf '\n\t\t{'
         printf "\"${diskarray[$i]}\":\"${osdarray[$i]}\"}"
         if [ $i -lt $[$length-1] ];then
                 printf ','
         fi
done
printf  "\n\t]\n"
printf "}\n"
