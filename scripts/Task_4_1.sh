allNames=("ATL" "BOS" "DFW" "DFWDC" "DIA" "DIADC" "IAD" "LAX" "MIA" "MSP" "ORD" "PPX" "SFO")

routerNames=("ATL" "BOS" "DFW" "DIA" "IAD" "LAX" "MIA" "MSP" "ORD" "PDX" "SFO")
AS=5


# 4.1 a) DIA-L2 interface added to DIA router
echo "conf t
interface DIA-L2
ip address 5.200.0.1/23
" |./goto.sh DIA router


# 4.1 b) DIADC DIA_dnsmasq. Add 5.200.0.2 as the host IP address.
# netstat -i :shows further info
# Muster: ifconfig [interface name] [ip address]
echo "
ifconfig 5-SPINE 5.200.0.2
ifconfig 5-SPINE
" |./goto.sh ./goto.sh DIADC DIA_dnsmasq
# now the dnsmasq host is pingable from DIA router


#  Add 5.200.0.0/23 as interface
# edit /etc/dnsmasq.conf file in vim:
# 
#interface=5-SPINE
#dhcp-range=5.200.0.3,5.200.1.254,6h
# start from 5.200.0.3, last one is 254, since 255 ist the broadcast address
# every 6 hours the host will get a new ip address assigned by dnsmasq
# afterwards run:
echo "
dnsmasq --test
service dnsmasq restart
" |./goto.sh DIADC DIA_dnsmasq


# 4.1 b) DIADC DIA_dnsmasq. Add expand-hosts and add domain DIA-DC.group5 => name resolution 
# edit /etc/dnsmasq.conf file in vim:
# 
#
#server=198.0.0.100
#interface=5-SPINE
#dhcp-range=5.200.0.3,5.200.1.254,255.255.254.0,6h
#expand-hosts
#domain=DIA-DC.group5 
# 
# enable option to refresh every 6h:
#dhcp-option=option6:information-refresh-time,6h


# After this is run, both server can ping the dnsmasq host
echo "
dhclient -v 5-LEAF1
" |./goto.sh DIADC DIA_server_1

echo "
dhclient -v 5-LEAF2
" |./goto.sh DIADC DIA_server_2

# 4.1 c) address
#
#server=198.0.0.100
#interface=5-SPINE
#dhcp-range=5.200.0.3,5.200.1.254,6h
#expand-hosts
#domain=DIA-DC.group5 

#following lines were commented out for now:
# dhcp-host=26:76:11:C0:10:FB,DIA-DC.server1 =>IGNORE! This is the  MAC of LEAF1 potentailly
#dhcp-host=06:6c:01:73:ce:a9,DIA-DC.server1 
# dhcp-host=16:3A:86:6C:7D:4E,DIA-DC.server2 =>IGNORE! This is the MAC of LEAF2 potentailly
#dhcp-host=86:c7:f7:1e:fb:79,DIA-DC.server2

#DIA host in /etc/resolv.conf nameserver was changed to 5.200.0.2

# this snippet is the "advertise_bgp.sh"
for i in ${!routerNames[@]}; 
do
    curRouter="${routerNames[$i]} router"

echo "conf t
router bgp 5
network 5.200.0.0/23
"|./goto.sh $curRouter
done


# Add default route 
#dhcp-range=option:router,5.200.0.1

# how to reset Server hosts:
echo "
dhclient -r
dhclient
" |./goto.sh DIADC DIA_server_1

echo "
dhclient -r
dhclient
" |./goto.sh DIADC DIA_server_2



