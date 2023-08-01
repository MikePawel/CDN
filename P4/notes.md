# Notes Assignment 5
### 5.2b)
Switches don't behave as expected, reason: Since the three switches form a loop any packet will be relayed infinitely often between the switches and will therefore arrive infinitely often at the destination. When starting a ping the output shows that the response is received as duplicate packets very often.

### 5.2c)
MAC-Addresses for manual table configuration:
|Host|Interface|Address|
|--|--|--|--|
|P4_1|5-P4_2|62:9b:19:5e:7e:a5|
|P4_1|5-P4_3|de:29:ab:9f:dd:3f|
|P4_2|5-P4_1|92:54:05:66:8e:22|
|P4_2|5-P4_3|ee:4a:52:a0:6b:06|
|P4_3|5-P4_1|5e:89:4a:c9:2e:78|
|P4_3|5-P4_2|0e:f3:8f:b2:73:20|
|DFW_dnsmasq|5-P4_1|3e:a2:0c:19:19:c8|
|DFW_server_1|5-P4_1|ae:d4:ff:54:4f:50|
|DFW_server_2|5-P4_2|26:a8:ba:e7:d6:17|
|DFW_server_3|5-P4_3|ea:7e:24:e1:07:c3|

All Switches: ff:ff:ff:ff:ff:ff => broadcast()

ARP requests are still sent around infinitely, all requests with unknown MAC-Addresses are still broadcast around infinitely
Solution: Check if the packet has already been at the switch