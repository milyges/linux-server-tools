#!/bin/sh

CONF_DIR="/root/skrypty/etc"

source ${CONF_DIR}/main.conf

rm ${SQUIDACCESS_FILE}

egrep -v '^($|#)' ${CONF_DIR}/hosts.conf | awk '$4 == "0" { print $0 }' | while read LINE
do
	MAC=$(echo $LINE | awk '{ print $2 }')
	
	echo "acl fullaccess arp ${MAC}" >> ${SQUIDACCESS_FILE}
done


/etc/init.d/squid reload
