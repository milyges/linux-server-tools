#!/bin/sh

set -e

NAME=""
TYPE=""

MASTERS=""
NOTIFY=
FILE=
XFER=

while getopts "s:n:h" OPT; do
    case $OPT in
	h) 
	    cat <<EOF
Użycie:
$0 [-n STREFA [-m IP;IP]] [-h]
 
-n STREFA    Podaj nazwę strefy
-s IP;IP     Dodaj strefę typu slave z podanymi
             numerami IP dla mastera. Numery IP
             oddzielone średnikami
-h           Niniejsza pomoc             
EOF
	    exit
	    ;;
	s) 
	    TYPE="slave"
	    MASTERS="$OPTARG"
	    ;;
	n) 
	    NAME="$OPTARG"
	    ;;
    esac
done

if [ -z "$NAME" ]; then
    echo -n "Podaj nazwę domeny: " && read NAME
    echo -n "Podaj IP mastera oddzielone średnikami JEŚLI rekord jest typu slave: " && read MASTERS
    [ -z "$MASTERS" ] || TYPE="slave"
fi

TYPE=${TYPE:-master}

if [ "$TYPE" = "master" ]; then
	NOTIFY="yes"
	FILE="pri/${NAME}.zone"
	XFER="xfer"
elif [ "$TYPE" = "slave" ]; then
	NOTIFY="no"
	FILE="sec/${NAME}.zone"
	XFER="none"
fi

cat >> /etc/bind/named.conf <<EOF

zone "${NAME}" {
	type ${TYPE};
	file "${FILE}";
	notify ${NOTIFY};
	allow-query { any; };
	allow-transfer { ${XFER}; };
EOF

[ -z "${MASTERS}" ] || echo "	masters { ${MASTERS}; };" >>  /etc/bind/named.conf 

echo "};" >> /etc/bind/named.conf 

if [ "${TYPE}" = "slave" ]
then
	/etc/init.d/named reload
	exit 0
fi

# Tworzymy wyjsciowy plik strefy
cat > /etc/bind/${FILE} <<EOF
\$TTL 86400
\$ORIGIN ${NAME}.

@	IN	SOA	ns1.dug.net.pl. admin.dug.net.pl. (
	0000000000	;; Serial
	2d		;; Refresh
        15m		;; Update retry
        2w		;; Expiry
        1h		;; Minimum
)

@	IN	NS	ns1.dug.net.pl.
@	IN	NS	ns2.dug.net.pl.


EOF

# uruchamiamy edycje strefy
/root/skrypty/dns_edytuj_strefe.sh "$NAME"
