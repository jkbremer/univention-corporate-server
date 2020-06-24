#!/bin/bash
univention-ldapsearch "(&(objectclass=univentionDomainController)(univentionService=Samba 4))" cn | sed -n 's/^cn: \(.*\)/\1/p'
univention-ldapsearch "uid=Administrator" | ldapsearch-wrapper
declare -a args=()
args[${#args[@]}]="-D"
