#!/bin/sh


LST_DIR="/home/milyges/lst/"

DATE=$(date +'%d-%m-%Y')
WHAT=$(basename $0 | sed -e 's/backup_\(\w*\)\.sh/\1/')
CONFIG=$(awk "\$1 == \"${WHAT}\" { print \$0 }" ${LST_DIR}/etc/backup.conf)

TYPE=$(echo $CONFIG | awk '{ print $2 }')
SOURCE=$(echo $CONFIG | awk '{ print $3 }')
DEST=$(echo $CONFIG | awk '{ print $4 }')
COMP=$(echo $CONFIG | awk '{ print $5 }')
COUNT=$(echo $CONFIG | awk '{ print $6 }')

case "${TYPE}" in
	dir)
		tar cjf "${DEST}/${WHAT}-${DATE}.tar.bz2" -C ${SOURCE} ./ 2> /tmp/$0.$$
	;;
	mysql)
		
	;;
	*) 
		echo "Unknown backup type (${TYPE})" >&2
		exit 1
	;;
esac

if [ -s "/tmp/$0.$$" ]
then
	cat /tmp/$0.$$ | mail -s "$0: $HOSTNAME: backup $WHAT at $DATE fail report" ${EMAIL}
	rm -f /tmp/$0.$$
	exit 2
fi

rm -f /tmp/$0.$$

# Kasujemy stare backupy
