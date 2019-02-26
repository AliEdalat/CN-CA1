import os
import select
import signal
import struct
import sys
import time
import socket,sys
from impacket import ImpactPacket
from random import randint

default_timer = time.time

ICMP_ECHOREPLY = 0
ICMP_ECHO = 8
ICMP_MAX_RECV = 2048

MAX_SLEEP = 1000

def is_valid_ip4_address(addr):
	parts = addr.split(".")
	if not len(parts) == 4:
		return False
	for part in parts:
		try:
			number = int(part)
		except ValueError:
			return False
		if number > 255 or number < 0:
			return False
	return True


class Ping(object):
	def __init__(self, payload=None, pieceNumber = None):

		self.destination = "10.0.0.0"
		self.source = "10.0.0.0"
		self.payload = payload
		self.pieceNumber = pieceNumber
		self.send_count = 0
		self.receive_count = 0
		self.min_time = 999999999
		self.max_time = 0.0
		self.total_time = 0.0
		self.rec = False

	def header2dict(self, names, struct_format, data):

        	unpacked_data = struct.unpack(struct_format, data)
        	return dict(zip(names, unpacked_data))
    
    	def run(self, deadline=None):

		while True:
			delay = self.do()
            
			if deadline and self.total_time >= deadline:
				break

			if delay == None:
				delay = 0

			if (MAX_SLEEP > delay):
				time.sleep((MAX_SLEEP - delay) / 1000.0)
        
	def int2ip(self, addr):
		return socket.inet_ntoa(struct.pack("!I", addr))

    	def do(self):

		try: 
			current_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
			current_socket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
		except socket.error, (errno, msg):
			if errno == 1:
				etype, evalue, etb = sys.exc_info()
				evalue = etype(
					"%s - Note that ICMP messages can only be sent from processes running as root." % evalue
				)
				raise etype, evalue, etb
			raise

		receive_time, packet_size, ip, ip_header, icmp_header, payload = self.receive_one_ping(current_socket)
		print(payload)
		print(ip_header)
		if ip_header:
			self.rec = True
		send_time = self.send_one_ping(current_socket, ip_header, payload)
		if send_time == None:
			return
		self.send_count += 1

		
		current_socket.close()
		if receive_time:
			self.receive_count += 1
			delay = (receive_time - send_time) * 1000.0
			self.total_time += delay
			if self.min_time > delay:
				self.min_time = delay
			if self.max_time < delay:
				self.max_time = delay
			return delay
    
    	def send_one_ping(self, current_socket, ip_header, payload):
		if self.rec:
			self.source = self.int2ip(ip_header["dest_ip"])
			self.destination = self.int2ip(ip_header["src_ip"])
			# self.rec = False
		else:
			self.source = "10.0.0."+ str(randint(1,4))
			self.destination = "10.0.0."+ str(randint(1,4))
		print(self.source)
		print(self.destination)
		src = self.source
		dst = self.destination
		ip = ImpactPacket.IP()
		ip.set_ip_src(src)
		ip.set_ip_dst(dst)	
		icmp = ImpactPacket.ICMP()
		icmp.set_icmp_type(icmp.ICMP_ECHO)
		if not self.rec:
			icmp.contains(ImpactPacket.Data(self.payload))
		else:
			print('rec')
			self.rec = False
			icmp.contains(ImpactPacket.Data(payload))
		ip.contains(icmp)
		icmp.set_icmp_id(self.pieceNumber)
		icmp.set_icmp_cksum(0)
		icmp.auto_checksum = 1
		send_time = default_timer()
		try:
			current_socket.sendto(ip.get_packet(), (dst, 1))
		except socket.error as e:
			self.response.output.append("General failure (%s)" % (e.args[1]))
			current_socket.close()
			return
		return send_time	

	def receive_one_ping(self, current_socket):

		while True:
			select_start = default_timer()
			inputready, outputready, exceptready = select.select([current_socket], [], [], 1)
			select_duration = (default_timer() - select_start)
			if inputready == []:
				return None, 0, 0, 0, 0, None

			packet_data, address = current_socket.recvfrom(ICMP_MAX_RECV)
			icmp_header = self.header2dict(
				names=[
					"type", "code", "checksum",
					"packet_id", "seq_number"
				],
				struct_format="!BBHHH",
				data=packet_data[20:28]
			)
			receive_time = default_timer()
			ip_header = self.header2dict(
				names=[
					"version", "type", "length",
					"id", "flags", "ttl", "protocol",
					"checksum", "src_ip", "dest_ip"
				],
				struct_format="!BBHHHBBHII",
				data=packet_data[:20]
			)
			packet_size = len(packet_data) - 28
			ip = socket.inet_ntoa(struct.pack("!I", ip_header["src_ip"]))
			return receive_time, packet_size, ip, ip_header, icmp_header, packet_data[28:]
    
def readChunks():
	return f.read(512)

def ping():
	pieceNumber = 0
	for piece in iter(readChunks, ''):
		pieceNumber += 1
		p = Ping(piece, pieceNumber)
	return p.run()

f = open('file.dat')
ping()
