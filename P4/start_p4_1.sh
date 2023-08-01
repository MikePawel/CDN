echo "
simple_switch -i 0@p4 -i 1@5-DFW_dnsmasq -i 2@5-DFW_server_1 -i 3@5-P4_2 -i 4@5-P4_3 -i 5@DFWrouter switch.json
" | ./goto.sh DFWDC P4_1