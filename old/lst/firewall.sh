#!/bin/sh

CONF_DIR="/root/skrypty/etc"

source ${CONF_DIR}/main.conf

IPT="/sbin/iptables"

# Funkcje pomocnicze

# port_open proto port
port_open() 
{
	if [ -z "${1}" ] || [ -z "${2}" ]
	then
		echo "Usage: $0 proto port"
		return
	fi

	$IPT -A INPUT -i ${WAN_IF} -p ${1} --dport ${2} -m state --state NEW -j ACCEPT
}

# port_redirect proto port dest
port_redirect()
{
	if [ -z "${1}" ] || [ -z "${2}" ] || [ -z "${3}" ]
	then
		echo "Usage: $0 proto port dest"
		return
	fi

	$IPT -t nat -A PREROUTING -i ${WAN_IF} -p ${1} --dport ${2} -j DNAT --to ${3}
	$IPT -A FORWARD -i ${WAN_IF} -o ${LAN_IF} -p ${1} --dport ${2} -m state --state NEW
}

# Kasowanie regol
$IPT -F
$IPT -X 
$IPT -t nat -F
$IPT -t nat -X

# Domyslna polityka
$IPT -P INPUT DROP
$IPT -P FORWARD DROP
$IPT -P OUTPUT ACCEPT

# Polaczena nawiazane
$IPT -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
$IPT -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT
$IPT -A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Akceptujemy zaufany ruch
$IPT -A INPUT -i lo -m state --state NEW -j ACCEPT
$IPT -A INPUT -i ${LAN_IF} -s ${LAN_NET} -m state --state NEW -j ACCEPT
$IPT -A INPUT -i ${VPN_IF} -s ${VPN_NET} -m state --state NEW -j ACCEPT

# Ruch LAN <-> VPN
$IPT -A FORWARD -i ${LAN_IF} -s ${LAN_NET} -o ${VPN_IF} -d ${VPN_NET} -m state --state NEW -j ACCEPT
$IPT -A FORWARD -i ${VPN_IF} -s ${VPN_NET} -o ${LAN_IF} -d ${LAN_NET} -m state --state NEW -j ACCEPT

# Puszczamy pingi przychodzace
$IPT -A INPUT -i ${WAN_IF} -p icmp --icmp-type echo-request -j ACCEPT

# Ruch co leci na zewn ip do szalonego pana admina, wrzucamy na shinigami
$IPT -t nat -A PREROUTING -i ${LAN_IF} -s ${LAN_NET} -d 213.134.165.206 -p tcp -m multiport --dport 80,22,443,1080,1443,1022 -j DNAT --to 10.10.10.1

# Ruch HTTP leci przez PROXY
$IPT -t nat -A PREROUTING -i ${LAN_IF} -s ${LAN_NET} '!' -d  ${LAN_NET} -p tcp --dport 80 -j REDIRECT --to-port 3128

# Maskarada
$IPT -t nat -A POSTROUTING -s ${LAN_NET} -o ${WAN_IF} -j MASQUERADE
$IPT -A FORWARD -i ${LAN_IF} -s ${LAN_NET} -o ${WAN_IF} -m state --state NEW -j ACCEPT
$IPT -t nat -A POSTROUTING -s 10.10.11.0/24 -o ${WAN_IF} -j MASQUERADE
$IPT -A FORWARD -i eth2 -s 10.10.11.0/24 -o ${WAN_IF} -m state --state NEW -j ACCEPT

###
# Otwarte porty
###
port_open tcp 22
port_open tcp 80
port_open tcp 443
port_open tcp 1194

###
# Przekierowanie portow
###
