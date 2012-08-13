# -*- coding: utf-8 -*-
from app.template import Template

t = Template()
t.assign('VHOST_ROOT', '/var/www/8sim.lanox.pl')
t.assign('DOMAIN', '8sim.lanox.pl')
t.assign('SERVER_ADMIN', 'gglinski@grupaeuro.pl')
t.assign('SUEXEC', False)

print(t.generate('templates/apache_vhost.tpl'))
