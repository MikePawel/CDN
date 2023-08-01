from scapy.all import Ether, sniff, Packet, BitField, raw
from sswitch_thrift_API import *

class SwitchPortHeader(Packet):
    name = 'SwitchPortPacket'
    fields_desc = [BitField('ingress_port', 0, 16)]


class PIXController:

    def __init__(self):
        self.switch_id = -1

        self.known_macs = {}

        self.controller = SimpleSwitchThriftAPI(9090)
        self.init()

    def reset(self):
        # Reset grpc server
        self.controller.reset_state()

    def init(self):
        self.reset()
        self.add_broadcast_groups()
        self.add_clone_session()
        self.setup_table_entries()

    def add_clone_session(self):
        ## Create a mirroring session with ID 42 that clones packets to port 0
        self.controller.mirroring_add(42, 0)
        return

    def add_broadcast_groups(self):
        ## **HINT** You can setup your multicast groups and nodes
        ## self.controller.mc_mgrp_create(<group_id>)
        ## self.controller.mc_node_create(<group_id>)
        ## self.controller.mc_node_associate(<group_id>, <node_id>)

        if self.switch_id == 1:
            # Do not broadcast packets between switches (ports 3 and 4) to prevent loops
            self.controller.mc_mgrp_create(1)
            self.controller.mc_mgrp_create(2)
            self.controller.mc_mgrp_create(3)
            self.controller.mc_mgrp_create(4)
            self.controller.mc_mgrp_create(5)

            node1 = self.controller.mc_node_create(1, [2, 3, 4, 5])
            node2 = self.controller.mc_node_create(2, [1, 3, 4, 5])
            node3 = self.controller.mc_node_create(3, [1, 2, 5])
            node4 = self.controller.mc_node_create(4, [1, 2, 5])
            node5 = self.controller.mc_node_create(5, [1, 2, 3, 4])

            self.controller.mc_node_associate(1, node1)
            self.controller.mc_node_associate(2, node2)
            self.controller.mc_node_associate(3, node3)
            self.controller.mc_node_associate(4, node4)
            self.controller.mc_node_associate(5, node5)
        elif self.switch_id == 2:
            # Do not broadcast packets between switches (ports 2 and 3) to prevent loops
            self.controller.mc_mgrp_create(1)
            self.controller.mc_mgrp_create(2)
            self.controller.mc_mgrp_create(3)
            self.controller.mc_mgrp_create(4)

            node1 = self.controller.mc_node_create(1, [2, 3, 4])
            node2 = self.controller.mc_node_create(2, [1, 4])
            node3 = self.controller.mc_node_create(3, [1, 4])
            node4 = self.controller.mc_node_create(4, [1, 2, 3])

            self.controller.mc_node_associate(1, node1)
            self.controller.mc_node_associate(2, node2)
            self.controller.mc_node_associate(3, node3)
            self.controller.mc_node_associate(4, node4)
        elif self.switch_id == 3:
            # Do not broadcast packets between switches (ports 2 and 3) to prevent loops
            self.controller.mc_mgrp_create(1)
            self.controller.mc_mgrp_create(2)
            self.controller.mc_mgrp_create(3)
            self.controller.mc_mgrp_create(4)

            node1 = self.controller.mc_node_create(1, [2, 3, 4])
            node2 = self.controller.mc_node_create(2, [1, 4])
            node3 = self.controller.mc_node_create(3, [1, 4])
            node4 = self.controller.mc_node_create(4, [1, 2, 3])

            self.controller.mc_node_associate(1, node1)
            self.controller.mc_node_associate(2, node2)
            self.controller.mc_node_associate(3, node3)
            self.controller.mc_node_associate(4, node4)
        else:
            print("Invalid switch_id set in controller.py")

        return

    def setup_table_entries(self):
        #HINT: self.controller.table_add(table_name, action_name, list of matches, list of action parameters)
        self.controller.table_add("mac_learning", "NoAction", ["0xffffffffffff" , "0"])
        self.controller.table_add("mac_learning", "NoAction", ["0xffffffffffff" , "1"])
        self.controller.table_add("mac_learning", "NoAction", ["0xffffffffffff" , "2"])
        self.controller.table_add("mac_learning", "NoAction", ["0xffffffffffff" , "3"])
        self.controller.table_add("mac_learning", "NoAction", ["0xffffffffffff" , "4"])
        self.controller.table_add("mac_learning", "NoAction", ["0xffffffffffff" , "5"])

        self.controller.table_add("mcgrp_selector", "store_ingress_port", ["0x1"], ["0x1"])
        self.controller.table_add("mcgrp_selector", "store_ingress_port", ["0x2"], ["0x2"])
        self.controller.table_add("mcgrp_selector", "store_ingress_port", ["0x3"], ["0x3"])
        self.controller.table_add("mcgrp_selector", "store_ingress_port", ["0x4"], ["0x4"])
        self.controller.table_add("mcgrp_selector", "store_ingress_port", ["0x5"], ["0x5"])
        self.controller.table_add("mcgrp_selector", "store_ingress_port", ["0x6"], ["0x6"])
        self.controller.table_add("mcgrp_selector", "store_ingress_port", ["0x7"], ["0x7"])

        #return

        #temporary static entries

        if self.switch_id == 1:
            #DFW ROUTER
            self.controller.table_add("mac_learning", "NoAction", ["0x06fd05c7f83d", "5"])
            self.controller.table_add("l2_forwarding", "unicast", ["0x06fd05c7f83d"], ["0x5"])

            #dnsmasq
            self.controller.table_add("mac_learning", "NoAction", ["0x3ea20c1919c8", "1"])
            self.controller.table_add("l2_forwarding", "unicast", ["0x3ea20c1919c8"], ["0x1"])

            #DFW server 1
            self.controller.table_add("mac_learning", "NoAction", ["0xaed4ff544f50", "2"])
            self.controller.table_add("l2_forwarding", "unicast", ["0xaed4ff544f50"], ["0x2"])

            #DFW server 2
            self.controller.table_add("mac_learning", "NoAction", ["0x26a8bae7d617", "3"])
            self.controller.table_add("l2_forwarding", "unicast", ["0x26a8bae7d617"], ["0x3"])

            #DFW server 3
            self.controller.table_add("mac_learning", "NoAction", ["0xea7e24e107c3", "4"])
            self.controller.table_add("l2_forwarding", "unicast", ["0xea7e24e107c3"], ["0x4"])
        elif self.switch_id == 2:
            #DFW ROUTER
            self.controller.table_add("mac_learning", "NoAction", ["0x06fd05c7f83d", "2"])
            self.controller.table_add("l2_forwarding", "unicast", ["0x06fd05c7f83d"], ["0x2"])

            #dnsmasq
            self.controller.table_add("mac_learning", "NoAction", ["0x3ea20c1919c8", "2"])
            self.controller.table_add("l2_forwarding", "unicast", ["0x3ea20c1919c8"], ["0x2"])

            #DFW server 1
            self.controller.table_add("mac_learning", "NoAction", ["0xaed4ff544f50", "2"])
            self.controller.table_add("l2_forwarding", "unicast", ["0xaed4ff544f50"], ["0x2"])

            #DFW server 2
            self.controller.table_add("mac_learning", "NoAction", ["0x26a8bae7d617", "1"])
            self.controller.table_add("l2_forwarding", "unicast", ["0x26a8bae7d617"], ["0x1"])

            #DFW server 3
            self.controller.table_add("mac_learning", "NoAction", ["0xea7e24e107c3", "3"])
            self.controller.table_add("l2_forwarding", "unicast", ["0xea7e24e107c3"], ["0x3"])

            #VPN 3 CONFIGS
            #self.controller.table_add("mac_learning", "NoAction", ["<device mac>", "4"])
            #self.controller.table_add("l2_forwarding", "unicast", ["<device mac>"], [0x4])
        elif self.switch_id == 3:
            #DFW ROUTER
            self.controller.table_add("mac_learning", "NoAction", ["0x06fd05c7f83d", "2"])
            self.controller.table_add("l2_forwarding", "unicast", ["0x06fd05c7f83d"], ["0x2"])

            #dnsmasq
            self.controller.table_add("mac_learning", "NoAction", ["0x3ea20c1919c8", "2"])
            self.controller.table_add("l2_forwarding", "unicast", ["0x3ea20c1919c8"], ["0x2"])

            #DFW server 1
            self.controller.table_add("mac_learning", "NoAction", ["0xaed4ff544f50", "2"])
            self.controller.table_add("l2_forwarding", "unicast", ["0xaed4ff544f50"], ["0x2"])

            #DFW server 2
            self.controller.table_add("mac_learning", "NoAction", ["0x26a8bae7d617", "3"])
            self.controller.table_add("l2_forwarding", "unicast", ["0x26a8bae7d617"], ["0x3"])

            #DFW server 3
            self.controller.table_add("mac_learning", "NoAction", ["0xea7e24e107c3", "1"])
            self.controller.table_add("l2_forwarding", "unicast", ["0xea7e24e107c3"], ["0x1"])

            #VPN 4 CONFIGS
            #self.controller.table_add("mac_learning", "NoAction", ["<device mac>", "4"])
            #self.controller.table_add("l2_forwarding", "unicast", ["<device mac>"], [0x4])
        else:
            print("Invalid switch_id set in controller.py")

        return

    def learn_mac(self, mac_addr, ingress_port):
        print("mac: %012s ingress_port: %s " % (mac_addr, ingress_port))
        #HINT: self.controller.table_add(table_name, action_name, list of matches, list of action parameters)
        #HINT: self.controller.table_modify_match(table_name, action_name, list of matches, list of action parameters)
        #HINT: self.controller.table_delete_match(table_name, list of matches)

        #return

        if(mac_addr in self.known_macs):
            old_port = self.known_macs[mac_addr]
            self.controller.table_delete_match("mac_learning", [mac_addr, str(old_port)])
            self.controller.table_modify_match("l2_forwarding", "unicast", [mac_addr], [str(ingress_port)])
        else:
            self.controller.table_add("l2_forwarding", "unicast", [mac_addr], [str(ingress_port)])

        self.controller.table_add("mac_learning", "NoAction", [mac_addr, str(ingress_port)])
        self.known_macs[mac_addr] = ingress_port

        return

    def recv_msg_cpu(self, pkt):
        packet = Ether(raw(pkt))
        if packet.type == 0x1234:
            switch_port_header = SwitchPortHeader(bytes(packet.load))
            self.learn_mac(packet.src, switch_port_header.ingress_port)

    def run_cpu_port_loop(self):
        ## Listen to packets on interface ssh and feed them into recv_msg_cpu
        sniff(iface="p4", prn=self.recv_msg_cpu)


if __name__ == "__main__":
    controller = PIXController().run_cpu_port_loop()
