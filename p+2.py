#!/usr/bin/env python3
import sys
import os
import socket
import socketserver
import threading

# constants
VERSION		= "p+2 0.0.0.0.0.0.0.0.0.1 megaAlpha"
MIN_ARGS	= 4
ENCODING	= "utf_8"
PEER_LIST 	= 0
QUERY 		= 1
DOWNLOAD 	= 2
OK_COLOR 	= "\033[1;32m"
END_COLOR 	= "\033[0m"

# some classes needed
class PeerList(socketserver.BaseRequestHandler):
	# overriding the handle method
	def handle(self):
		data = self.request.recv(1024)
		peer = str(data.decode(ENCODING))[:-1] # [:-1] to remove the '\n'
		# adding the peer if it's not in the list
		if peer != (myHost + str(myPort)) and peer not in peers:
			peers.append(peer)
		# sending our list
		msg = "\n".join(peers)
		response = bytes(msg, ENCODING)
		self.request.send(response)
		# TODO: close connection from server here (how?)

class Query(socketserver.BaseRequestHandler):
	
	def handle(self):
		data = self.request.recv(1024)
		fileName = str(data.decode(ENCODING))[:-1]
		# creating a list with the files that match
		files = os.listdir(myFolder)
		foundFiles = []
		for f in files: # TODO: look inside folders????
			if (f.find(fileName) != -1): foundFiles.append(f)
		# sending the list of files that match
		msg = "\n".join(foundFiles)
		response = bytes(msg, ENCODING)
		self.request.send(response)
		# TODO: close connection from server here (how?)

class Upload(socketserver.BaseRequestHandler):
	
	def handle(self):
		data = self.request.recv(1024)
		fileName = str(data.decode(ENCODING))[:-1]
		try:
			f = open(myFolder+ fileName, "rb")
			fileContent = f.read()
		finally:
			f.close()
		# sending the file
		self.request.send(fileContent)
		# TODO: close connection from server here (how?)

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
	pass

if __name__ == "__main__":
	# processing arguments
	args = sys.argv
	peers = [] # this list will contain all the peers that we will talk with

	if len(args) < MIN_ARGS:
		sys.stderr.write("Usage:\n")
		sys.stderr.write("\t"+ args[0] +" local-port local-folder peer-ip:peer-port\n")
		exit(1)

	if not os.path.exists(args[2]):
		sys.stderr.write("The folder \""+ args[2] +"\" does not exist\n")
		exit(2)

	peers.append(args[3])
	if len(peers[0].split(":")) < 2:
		sys.stderr.write("A peer must be specified in this way:\n")
		sys.stderr.write("\t"+ "peer-ip:peer-port\n")
		exit(3)

	myHost = socket.gethostbyname(socket.gethostname())
	myPort = int(args[1])
	myFolder = args[2]
	
	# creating and starting the first server (for peer management)
	server1 = ThreadedTCPServer((myHost, myPort + PEER_LIST), PeerList)
	server1Thread = threading.Thread(target = server1.serve_forever)
	server1Thread.setDaemon(True) # exit the server thread when the main thread terminates
	server1Thread.start()
	
	# creating and starting the second server (file searching)
	server2 = ThreadedTCPServer((myHost, myPort + QUERY), Query)
	server2Thread = threading.Thread(target = server2.serve_forever)
	server2Thread.setDaemon(True)
	server2Thread.start()
	
	# creating and starting the third server (data transfer)
	server3 = ThreadedTCPServer((myHost, myPort + DOWNLOAD), Upload)
	server3Thread = threading.Thread(target = server3.serve_forever)
	server3Thread.setDaemon(True)
	server3Thread.start()
	
	while True:
		pass
#		exit(0)
