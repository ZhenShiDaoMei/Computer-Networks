import dpkt
import socket

SOURCE_IP = ''
DEST_IP = ''

def analyze_tcp(path_to_pcap_file):
    global SOURCE_IP
    global DEST_IP

    # Opens in read binary
    with open(path_to_pcap_file, 'rb') as f:
        pcap = dpkt.pcap.Reader(f)
        tcp_flow_dict = {}

        # Iterate through each packet in pcap file
        for timestamp, buffer in pcap:
            ethernet = dpkt.ethernet.Ethernet(buffer)

            # Check if ethernet contains IP packet
            if not isinstance(ethernet.data, dpkt.ip.IP):
                continue
            ip = ethernet.data

            if SOURCE_IP == '' or DEST_IP == '':
                SOURCE_IP = socket.inet_ntoa(ip.src)
                DEST_IP = socket.inet_ntoa(ip.dst)

            # Check if IP packet contains TCP
            if not isinstance(ip.data, dpkt.tcp.TCP):
                continue
            tcp = ip.data

            # Only process packets with the defined SOURCE_IP and DEST_IP
            if socket.inet_ntoa(ip.src) != SOURCE_IP or socket.inet_ntoa(ip.dst) != DEST_IP:
                continue

            # Gets the IP address and port of source, and also gets the IP address and port of dest
            temp_key = (SOURCE_IP, tcp.sport, DEST_IP, tcp.dport)
            
            # If not in dictionary, add
            if temp_key not in tcp_flow_dict:
                tcp_flow_dict[temp_key] = {
                    'packets': [], 
                    'time_start': timestamp, 
                    'time_end': timestamp, 
                    'num_bytes': 0, 
                    'seq_nums': [], 
                    'ack_nums': [], 
                    'win_sizes': [], 
                    'win_scale': 0,
                    'retrans_timeout': 0, 
                    'retrans_duplicate_ack': 0, 
                    'acked_seq_nums': {},
                    'sent_seq_nums': {},
                    'packet_counts_per_rtt': [], 
                    'last_packet_time': timestamp, 
                    'packets_this_rtt': 0,
                    'initial_rtt_complete': False,
                    'initial_rtt': None
                }

            # Update tcp_flow_dict values
            flow = tcp_flow_dict[temp_key]
            flow['time_end'] = timestamp
            flow['packets'].append(tcp)
            flow['seq_nums'].append(tcp.seq)
            flow['ack_nums'].append(tcp.ack)
            flow['win_sizes'].append(tcp.win)
            if len(tcp.data) > 0:
                flow['num_bytes'] += len(tcp.data)

            # Find if timeout
            if tcp.seq in flow['sent_seq_nums']:
                time_since_first_transmission = timestamp - flow['sent_seq_nums'][tcp.seq]
                # Using 2*RTT as the threshold for identifying a timeout
                timeout_threshold = 2 * (flow['initial_rtt'] if flow['initial_rtt'] else 1.0)  # Default to 1.0 if RTT is not calculated
                
                # Compare to the threshold meanwhile making sure its not triple ack
                if time_since_first_transmission > timeout_threshold and flow['acked_seq_nums'].get(tcp.ack, 0) < 3:
                    flow['retrans_timeout'] += 1
            else:
                # First time this sequence number is seen, record the timestamp
                flow['sent_seq_nums'][tcp.seq] = timestamp

            # Count duplicate ACKs
            if tcp.ack in flow['acked_seq_nums']:
                flow['acked_seq_nums'][tcp.ack] += 1
                if flow['acked_seq_nums'][tcp.ack] == 3:
                    flow['retrans_duplicate_ack'] += 1
                    flow['acked_seq_nums'][tcp.ack] = 0
            else:
                flow['acked_seq_nums'][tcp.ack] = 1

            # Find window scale if SYN header
            if tcp.flags & dpkt.tcp.TH_SYN and not tcp.flags & dpkt.tcp.TH_ACK:
                tcp_options = dpkt.tcp.parse_opts(tcp.opts)
                for option in tcp_options:
                    # Option kind 3 is window scale
                    if option[0] == 3:  
                        tcp_flow_dict[temp_key]['win_scale'] = option[1][0]  
            
            # Find the congestion window sizes
            if tcp.flags & dpkt.tcp.TH_SYN and not flow['initial_rtt_complete']:
                flow['time_start'] = timestamp 
            
            if tcp.flags & dpkt.tcp.TH_ACK and not flow['initial_rtt_complete']:
                flow['initial_rtt'] = timestamp - flow['time_start']
                flow['initial_rtt_complete'] = True
                flow['last_packet_time'] = timestamp

            if flow['initial_rtt_complete']:
                # Packet counting for cwnd estimation
                if timestamp - flow['last_packet_time'] >= flow['initial_rtt']:
                    # An RTT has passed, update cwnd estimate
                    if len(flow['packet_counts_per_rtt']) < 3:
                        flow['packet_counts_per_rtt'].append(flow['packets_this_rtt'])
                    flow['packets_this_rtt'] = 1  
                    flow['last_packet_time'] = timestamp
                else:
                    flow['packets_this_rtt'] += 1
                 
        # PRINTING FORMAT
        print("--------------------------------------")
        for i, (flow_key, flow_data) in enumerate(tcp_flow_dict.items(), start=1):
            # Extract and calculate needed information from flow_data
            total_duration = flow_data['time_end'] - flow_data['time_start']
            throughput = flow_data['num_bytes'] / total_duration if total_duration > 0 else 0
            
            print(f"Flow {i}")
            print(f"Source Port: {flow_key[1]}")
            print(f"Source IP Address: {flow_key[0]}")
            print(f"Destination Port: {flow_key[3]}")
            print(f"Destination IP Address: {flow_key[2]} \n")
            i = 1

            while i != 3:
                scaled_window_size = flow_data['win_sizes'][i]<<flow_data['win_scale']
                print(f"Transaction: {i}")
                print(f"Sequence Number: {flow_data['seq_nums'][i+1]}")
                print(f"ACK Number: {flow_data['ack_nums'][i+1]}")
                print(f"Receiver Window Size: {scaled_window_size}\n")
                i += 1            

            print(f"Total Bytes: {flow_data['num_bytes']}")
            print(f"Total Duration (seconds): {total_duration}")
            print(f"Throughput (bytes/second): {throughput} \n")

            print(f"First 3 Congestion Window Sizes: {flow_data['packet_counts_per_rtt']}")
            print(f"Retransmission Due to Timeout: {flow_data['retrans_timeout']}")
            print(f"Retransmission Due to Triple ACK: {flow_data['retrans_duplicate_ack']}")
            print("--------------------------------------")
                
# Testing
pcap_file = 'assignment2.pcap'
analyze_tcp(pcap_file)


