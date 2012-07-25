#!/bin/sh

#set -x
DATABASES="redmine gtp gjms"
DATE=$(date +'%d-%m-%Y')
BACKUP_PATH="/home/backup/mysql"
USER="backup"
PASSWD="uFHdSdetNTYujcvQ"
EMAIL="rwachol@lanox.pl gglinski@lanox.pl"

for DB in ${DATABASES}
do
	rm -f ${BACKUP_PATH}/${DB}-${DATE}.sql.bz2
	mysqldump --user=${USER} --password=${PASSWD} ${DB} > ${BACKUP_PATH}/${DB}-${DATE}.sql 2>> /tmp/mysql_backup.$$
	if [ $? -ne 0 ]
	then
		rm ${BACKUP_PATH}/${DB}-${DATE}.sql
	else
		bzip2 ${BACKUP_PATH}/${DB}-${DATE}.sql
	fi
done

if [ -s "/tmp/mysql_backup.$$" ]
then
	cat /tmp/mysql_backup.$$ | mail -s "mysql_backup: $HOSTNAME: backup $DATE fail report" ${EMAIL}
fi

rm -f /tmp/mysql_backup.$$
