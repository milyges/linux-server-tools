#!/bin/sh

CONF_DIR="/root/skrypty/etc"

source ${CONF_DIR}/main.conf

# Obliczamy nowe seriale
ZONE_SERIAL="$(date +%Y%m%d)00"
RZONE_SERIAL="$(date +%Y%m%d)00"

ZONE_CSERIAL="$(awk '($2 == ";;") && ($3 == "Serial") { print $1 }' ${ZONE_FILE})"
RZONE_CSERIAL="$(awk '($2 == ";;") && ($3 == "Serial") { print $1 }' ${RZONE_FILE})"

[ "${ZONE_SERIAL}" -gt "${ZONE_CSERIAL}" ] || ZONE_SERIAL=$(($ZONE_CSERIAL + 1))
[ "${RZONE_SERIAL}" -gt "${RZONE_CSERIAL}" ] || RZONE_SERIAL=$(($RZONE_CSERIAL + 1))


sed -e "s/%SERIAL%/${ZONE_SERIAL}/g" ${CONF_DIR}/zone.tpl > ${ZONE_FILE}
sed -e "s/%SERIAL%/${RZONE_SERIAL}/g" ${CONF_DIR}/rzone.tpl > ${RZONE_FILE}

egrep -v '^($|#)' ${CONF_DIR}/hosts.conf | while read LINE
do
	IP=$(echo $LINE | awk '{ print $1 }')
	NAME=$(echo $LINE | awk '{ print $3 }')

	echo -e "${NAME}\tIN\tA\t${IP}" >> ${ZONE_FILE}
	echo -e "$(echo $IP | cut -d. -f4)\tIN\tPTR\t${NAME}.${DOMAIN_NAME}." >> ${RZONE_FILE}

done

/etc/init.d/named reload
