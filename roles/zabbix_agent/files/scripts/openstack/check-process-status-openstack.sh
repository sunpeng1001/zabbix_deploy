#!/bin/bash
#:***********************************************
#:Program: check-process-status-openstack.sh
#:
#:Author: keanli
#:
#:History: 2017-06-20
#:
#:Version: 1.0
#:***********************************************

export OS_PROJECT_DOMAIN_NAME=default
export OS_USER_DOMAIN_NAME=default
export OS_PROJECT_NAME=admin
export OS_USERNAME=admin
export OS_PASSWORD=ADMIN_PASS
export OS_AUTH_URL=http://10.131.78.149:10006/v3
export OS_IDENTITY_API_VERSION=3
export OS_IMAGE_API_VERSION=2

case $1 in
nova)
    process_status=$(nova service-list  | awk -F '|' '{print  $3 $4 $6 $7}' | grep -E 'down|disabled' | awk '{print $2": "$1}')
       if [[ $process_status = "" ]]; then
           echo 1
       else
           echo $process_status
       fi
;;
neutron)
    process_status=$(openstack network agent list | awk -F '|' '{print $4 $6 $7 $8 }' | grep -E 'XXX|DOWN' | awk '{print $1 ": "$4 }')
       if [[ $process_status = "" ]]; then
               echo 1
       else
               echo $process_status
       fi
;;
cinder)
    process_status=$(cinder service-list | awk -F '|' '{print $2 $3 $5 $6}' | grep enabled | grep down | awk '{print $2": "$1}' )
       if [[ $process_status = "" ]]; then
               echo 1
       else
               echo $process_status
       fi
;;
esac
