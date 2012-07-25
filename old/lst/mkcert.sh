#!/bin/sh

if [ -z "${1}" ]
then
        echo "Uzycie: $0 nazwa_klienta"
        exit 1
fi

cd /usr/share/openvpn/easy-rsa/
source ./vars
./build-key "$1"
#cp keys/* /etc/openvpn/keys/
mkdir -p "$HOME/tmp/$1"
cp keys/$1.crt "$HOME/tmp/$1"
cp keys/$1.key "$HOME/tmp/$1"
cp keys/ca.crt "$HOME/tmp/$1"                                                                                                

cat > "$HOME/tmp/$1/shinigami.ovpn" <<EOF
client
dev tun
proto tcp 
remote shinigami.lanox.pl
resolv-retry infinite
nobind

persist-key
persist-tun

ca ca.crt
cert $1.crt
key $1.key

comp-lzo
verb 3

EOF

cd $HOME/tmp/$1

zip $HOME/shinigami-${1}-vpn.zip *

echo "Archiwum $HOME/shinigami-${1}-vpn.zip gotowe! "

