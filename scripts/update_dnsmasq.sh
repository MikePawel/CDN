# Goes to DIA_dnsmasq, checks for syntax and restarts dnsmasq

echo "
dnsmasq --test
service dnsmasq restart
" |./goto.sh DIADC DIA_dnsmasq