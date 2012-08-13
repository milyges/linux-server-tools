<VirtualHost {$IP}:80>
	DocumentRoot "{$VHOST_ROOT}/htdocs"
	ServerName {$DOMAIN}
	ServerAdmin {$SERVER_ADMIN}
	
	ErrorLog "{$VHOST_ROOT}/logs/error_log"
	CustomLog "{$VHOST_ROOT}/logs/access_log" combined

	{IF $SUEXEC}
	SuexecUserGroup {$USER} {$GROUP}
	{ENDIF}
	
	<Directory "{$VHOST_ROOT}/htdocs">
		{IF $PHP_FCGI}
			FCGIWrapper {$FCGI_PHP} .php
			AddHandler fcgid-script .php
		{ENDIF}
		
		Options +FollowSymLinks -MultiViews +ExecCGI
		Order Deny, Allow
		Allow from all
	</Directory>
</VirtualHost>

