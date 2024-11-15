Jason Wu 114474379 CSE310 HW2

i. A.a. I was able to obtain the source IP address and the destination IP address by using the socket.inet_ntoa() function on the IP address obtain from ethernet.data. The ports were obtained by simply using the data found in tcp: tcp.sport and tcp.dport

A.b. The transaction values were obtained by adding the sequence numbers, ACK numbers and window sizes of every transaction to a list after the TCP connection was set up. I was able to obtain the first and second transaction data by using the correct indexes within the list to access the corresponding information.

A.c. I created a "counter" that counted the amount of data that was in the packets. I also had a time_start and time_end that allowed me to calculate the time taken for the packets to travel. With these variables I was able to compute total data/time taken.

B.1. I was able to estimate the RTT during the initial TCP handshake, and I used this estimation to approximate the size of the congestion windows based on the packet counts within each RTT interval.

B.2. As the code is ran, I keep track of two variables, acked_seq_nums and sent_seq_nums. If the tcp.seq was already in sent_seq_nums, then I would find the time it was last sent and find the time difference. This time difference is then compared  to the timeout threshold (which is 2*RTT), and if it's greater, it is considered a timeout. For the triple ACKs, I used asked_seq_nums, where if the tcp.ack occured more than 3 times, it was considered a triple ACK, and the asked_seq_nums would be reset to. 


iii. analysis_pcap_tcp.py is a function that uses the path to the pcap file as a parameter. When given the correct path to a pcap.file, it will print the following information (same format shown):

-------------------------------
Flow #  
Source Port  
Source IP  
Destination Port  
Destination IP  

Two transactions that contain:  
Sequence Number  
ACK Number  
Receiver Window Size  

Total Bytes  
Total Duration  
Throughput  

First 3 Congestion Window Sizes  
Retransmission Due to Timeout  
Retransmission Due to Triple ACK  

-------------------------------
