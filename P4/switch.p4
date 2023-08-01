/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

typedef bit<48> macAddr_t;

header ethernet_t {
	macAddr_t dstAddr;
	macAddr_t srcAddr;
	bit<16>   etherType;
}

header mac_learning_t {
  	bit<16> ingress_port;
}

struct metadata {
  	bit<16>	port_in;
    // **HINT** Add your custom metadata here
}

struct headers {
	ethernet_t   ethernet;
	mac_learning_t	mac_learning;
     // **HINT** Add additional headers here
}

/*************************************************************************
*********************** P A R S E R  ***********************************
*************************************************************************/

parser MyParser(
	packet_in packet,
	out headers hdr,
	inout metadata meta,
	inout standard_metadata_t standard_metadata) {

	state start{
		packet.extract(hdr.ethernet);
		transition accept;
	}

}

/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
	apply {  }
}


/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress(
	inout headers hdr,
	inout metadata meta,
	inout standard_metadata_t standard_metadata) {

  	action store_ingress_port(bit<16> ingress_port){
		meta.port_in = ingress_port;
	}

  	action broadcast() {
        standard_metadata.mcast_grp = meta.port_in;
	}

	action unicast(bit<9> egress_port) {
		standard_metadata.egress_port = egress_port;
		standard_metadata.egress_spec = egress_port;
	}

	action copy_to_control(){
		clone_preserving_field_list(CloneType.I2E, 42, 0);
	}

	table mac_learning {
		key = {
          	hdr.ethernet.srcAddr : exact;
			standard_metadata.ingress_port : exact;
		}
		actions = {
			copy_to_control;
			NoAction;
		}
		default_action = copy_to_control();
	}

	table mcgrp_selector {
		key = {
          	standard_metadata.ingress_port : exact;
		}
		actions = {
			store_ingress_port;
		}
	}

  	table l2_forwarding {
		key = {
			hdr.ethernet.dstAddr : exact;
		}
		actions = {
        	broadcast;
			unicast;
		}
		default_action = broadcast();
  	}

	table test_table {
		key = {
			meta.port_in : exact;
			standard_metadata.mcast_grp : exact;
			standard_metadata.egress_port : exact;
			standard_metadata.egress_spec : exact;
		}
		actions = {
			NoAction;
		}
	}

	apply {
          mcgrp_selector.apply();
          mac_learning.apply();
          l2_forwarding.apply();

          test_table.apply();
	}
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(
	inout headers hdr,
	inout metadata meta,
	inout standard_metadata_t standard_metadata) {
	apply {
        // **HINT** Modify packet and metadata in the EGRESS here
        if(standard_metadata.instance_type == 1){
          	hdr.ethernet.etherType = 0x1234;

          	hdr.mac_learning.setValid();
          	hdr.mac_learning = {
          		ingress_port = meta.port_in
          	};
        }
    }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers  hdr, inout metadata meta) {
	apply { }
}

/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
	apply {
		// parsed headers have to be added again into the packet
		packet.emit(hdr.ethernet);
		packet.emit(hdr.mac_learning);
	}
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

//switch architecture
V1Switch(
	MyParser(),
	MyVerifyChecksum(),
	MyIngress(),
	MyEgress(),
	MyComputeChecksum(),
	MyDeparser()
) main;
