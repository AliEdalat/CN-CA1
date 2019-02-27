import os
import select
import signal
import struct
import sys
import time
import socket,sys
from impacket import ImpactPacket
from random import randint
import io
import StringIO

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
	def __init__(self, file=None, nodeNum = 0):

		self.destination = "10.0.0.0"
		self.source = "10.0.0.0"
		self.receive_count = 0
		self.min_time = 999999999
		self.max_time = 0.0
		self.total_time = 0.0
		self.file = file
		self.nodeNum = nodeNum
		self.chunkNum = {}
		self.returnFile = ""
		self.ret = False
		self.fileToBeReturned = ""
		self.fileChunks = []
		self.fileGathered = 0
		self.bezi = 0

	def header2dict(self, names, struct_format, data):

        	unpacked_data = struct.unpack(struct_format, data)
        	return dict(zip(names, unpacked_data))
    
	def run(self, deadline=None):
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

		while True:
			print(self.chunkNum)
			print(self.fileGathered)
			if self.chunkNum == self.fileGathered and not self.chunkNum == 0:
				print("fuckkkk2")
				file_output = ""
				for x in self.fileChunks:
					file_output += x
				print(file_output)
				return 
			select_start = default_timer()
			inputready, outputready, exceptready = select.select([sys.stdin], [], [], 2)
			select_duration = (default_timer() - select_start)
			if inputready == []:
				self.do(current_socket)

			elif not self.file is None:
				sin = raw_input()
				inArgs = sin.split()
				if inArgs[0] == 'return':
					print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
					self.returnFile = inArgs[1]
					self.ret = True
            
			if deadline and self.total_time >= deadline:
				break

		current_socket.close()
        
	def int2ip(self, addr):
		return socket.inet_ntoa(struct.pack("!I", addr))

# Share multiple files -> buffer for multi files 
	def do(self,current_socket):

		receive_time, packet_size, ip, ip_header, icmp_header, payload = self.receive_one_ping(current_socket)
		if (not icmp_header is 0) and (not icmp_header["type"] == ICMP_ECHO):
			return
		if (not payload == "") and (not payload is None):
			buf = StringIO.StringIO(payload)
			metadata = buf.readline()
			print(metadata)
			metadata = metadata[:len(metadata)-1]
			metadataParts = metadata.split()
			print(metadataParts)
			if metadataParts[0] == "return":
				self.ret = True
				self.fileToBeReturned = metadataParts[1]
				self.bezi = metadataParts[2]
			elif metadataParts[0] == "finish":
				if self.file is not None:
					self.fileChunks[int(metadataParts[1])-1] = "\n".join(payload.split("\n")[1:])
					self.fileGathered += 1
					print(self.fileGathered)
					# if fileGathered ==
			elif self.ret is True:
				if self.file is not None:
					self.fileChunks[int(metadataParts[1])-1] = "\n".join(payload.split("\n")[1:])
					self.fileGathered += 1
					print(self.fileGathered)
				if self.fileToBeReturned == metadataParts[0]:
					payload = "\n".join(payload.split("\n")[1:])
					payload = "finish " + metadataParts[1] + "\n" + payload
					send_time = self.send_one_ping(current_socket, ip_header, payload)
					if send_time == None:
						return
			elif self.returnFile is not "":
				# print("!!!!!!!!!!")
				payload = 'return ' + self.returnFile + " " + str(self.nodeNum) + "\n"
				send_time = self.send_one_ping(current_socket, ip_header, payload)
				if send_time == None:
					return
			else:
				print(">>>>>>>>>>>Hello from the payload....!")
				send_time = self.send_one_ping(current_socket, ip_header, payload)
				if send_time == None:
					return
		elif not self.file is None:
			payload = self.file.read(512)
			if not payload == "":
				self.chunkNum+=1
				self.fileChunks.append("")
				print("<<<<<<<<<<<<<Hello from the beziiii....!")
				send_time = self.send_one_ping(current_socket, ip_header, 'file.dat ' + str(self.chunkNum) + '\n' +payload)
				if send_time == None:
					return
		
		
    #admin flag
	def send_one_ping(self, current_socket, ip_header, payload):
		if payload[0:6] == "finish":
			firstNode = randint(1,4)
			while(firstNode == self.bezi):
				firstNode = randint(1,4)
			self.source = "10.0.0." + str(firstNode)
			self.destination = "10.0.0." + str(self.bezi)
		else:
			firstNode = randint(1,4)
			secondNode = randint(1,4)
			while(secondNode == self.nodeNum or secondNode == firstNode):
				firstNode = randint(1,4)
				secondNode = randint(1,4)
			self.source = "10.0.0."+ str(firstNode)
			self.destination = "10.0.0."+ str(secondNode)
			print(self.source)
			print(self.destination)
		src = self.source
		dst = self.destination
		ip = ImpactPacket.IP()
		ip.set_ip_src(src)
		ip.set_ip_dst(dst)	
		icmp = ImpactPacket.ICMP()
		icmp.contains(ImpactPacket.Data(payload))
		icmp.set_icmp_type(icmp.ICMP_ECHO)
		ip.contains(icmp)
		icmp.set_icmp_id(icmp.get_icmp_id())####
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

print(sys.argv)
if (sys.argv[1] == 'True'):
	f = open('file.dat')
	p = Ping(file = f,nodeNum = int(sys.argv[2]))
else:
	p = Ping(nodeNum = int(sys.argv[2]))
p.run()
