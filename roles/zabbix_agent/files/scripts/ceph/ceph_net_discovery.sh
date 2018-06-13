#!/bin/bash
netarray=(`cat /proc/net/dev | grep -E 'eth.*|bond1.2001*|bond0.2000*|e(m|th|no)+[0-9]+$|(en)(p[0-9])?s[0-9]*|^p[ci]?[0-9]+p[0-9]+_?[0-9]?$' | awk -F ':' '{ print $1 }'|sort|uniq   2>/dev/null`)
length=${#netarray[@]}
printf "{\n"
printf  '\t'"\"data\":["
for ((i=0;i<$length;i++))
do
         printf '\n\t\t{'
         printf "\"{#IFNAME}\":\"${netarray[$i]}\"}"
         if [ $i -lt $[$length-1] ];then
                 printf ','
         fi
done
printf  "\n\t]\n"
printf "}\n"

