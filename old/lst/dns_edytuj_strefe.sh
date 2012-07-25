#!/bin/sh

set -e

[ -z "$1" ] && exit 1

NAME="$1"
TMPFILE=$(mktemp)

if [ ! -s "/etc/bind/pri/${NAME}.zone" ]; then
    echo "Błąd! Plik /etc/bind/pri/${NAME}.zone nie istnieje lub jest pusty" >/dev/stderr
    exit 1
fi

# Teraz troche czarów
OLD_SERIAL=$(awk '$3 == "Serial" { print $1 }' /etc/bind/pri/${NAME}.zone)
NEW_SERIAL="$(date '+%Y%m%d')00"

if [ "${OLD_SERIAL}" -ge "${NEW_SERIAL}" ]
then
	NEW_SERIAL=$((${OLD_SERIAL} + 1))
fi

sed -e "s/${OLD_SERIAL}/${NEW_SERIAL}/" /etc/bind/pri/${NAME}.zone > ${TMPFILE}

eval ${EDITOR} ${TMPFILE}

echo -n "Zatwierdzić zmiany? Enter dla TAK, Ctrl+C dla NIE " && read 

mv -f ${TMPFILE} /etc/bind/pri/${NAME}.zone 
chown root:named /etc/bind/pri/${NAME}.zone
chmod 0640 /etc/bind/pri/${NAME}.zone
/etc/init.d/named reload
