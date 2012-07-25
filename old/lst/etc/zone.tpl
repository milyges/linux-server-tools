$TTL 86400
$ORIGIN biuro2.lanox.lan.

@	IN	SOA	ns1.biuro2.lanox.lan.	gglinski.lanox.pl. (
	%SERIAL% ;; Serial
	2d         ;; Refresh
	15m        ;; Update retry
	2w         ;; Expiry
	1h         ;; Minimum
)

@	IN	NS	ns1
ns1	IN	A	10.10.10.1

