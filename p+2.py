#!/usr/bin/env python3
import sys
import os
import socket
import socketserver
import threading
from time import sleep

# constants
VERSION     = "0.1"
MIN_ARGS    = 2
ENCODING    = "utf_8"
PEER_LIST   = 0
QUERY       = 1
DOWNLOAD    = 2
OK_COLOR    = "\033[1;32m"
BOLD        = "\033[1;1m"
END_COLOR   = "\033[0m"

# some functions needed
# this functions returns a list with the names of the files that match the pattern
def searchFiles(path, pattern):
	entries = os.listdir(path)
	matchingFiles = []
	for e in entries:
		if   (os.path.isdir(path + os.sep + e)): matchingFiles += searchFiles(path + os.sep + e, pattern)
		elif (e.lower().find(pattern) != -1):    matchingFiles.append(path[len(myFolder) + 1:] + os.sep + e)
	return matchingFiles

# this function checks if a given port is valid or not 
def goodPort(port):
	if port.isdigit() and int(port)>0 and int(port)<65536: return True
	return False

# this function checks if a given IP is valid or not 
def goodIP(ip):
	ipSplitted = ip.split(".")
	if len(ipSplitted)!=4: return False
	for n in ipSplitted:
		if not n.isdigit() or int(n)<0 or int(n)>255: return False
	return True

# this function checks if the user wrote the IP:PORT with errors
def hasErrorsAddPeer(inputSplitted):
	if len(inputSplitted) != 2: return True
	peer = inputSplitted[1]
	peerSplitted = peer.split(":")
	if len(peerSplitted) != 2: return True
	ip = peerSplitted[0]
	port = peerSplitted[1]
	if not goodIP(ip) or not goodPort(port): return True
	return False

# some needed classes
class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
	pass

class PeerList(socketserver.BaseRequestHandler):
	# overriding the handle method
	def handle(self):
		data = self.request.recv(1024)
		peer = str(data.decode(ENCODING))[:-1] # [:-1] to remove the '\n'
		# adding the peer if it's not in the list
		if peer != (myHost +":"+ str(myPort)) and peer not in peers:
			peers.append(peer)
		# sending our list
		msg = "\n".join(peers)
		msg += "\n"
		response = bytes(msg, ENCODING)
		self.request.send(response)
		self.request.shutdown(socket.SHUT_RDWR)
		self.request.close()

class Query(socketserver.BaseRequestHandler):

	def handle(self):
		data = self.request.recv(1024)
		pattern = str(data.decode(ENCODING))[:-1]
		msg = ""
		if os.path.exists(myFolder):
			foundFiles = searchFiles(myFolder, pattern.lower())
			# sending the list of files that match
			msg += "\n".join(foundFiles)
		msg += "\n"
		response = bytes(msg, ENCODING)
		self.request.send(response)
		self.request.shutdown(socket.SHUT_RDWR)
		self.request.close()

class Upload(socketserver.BaseRequestHandler):

	def handle(self):
		data = self.request.recv(2048)
		fileName = os.sep + str(data.decode(ENCODING))[:-1]
		try:
			f = open(myFolder + fileName, "rb")
			fileContent = f.read()
		finally:
			f.close()
		# sending the file
		self.request.send(fileContent)
		self.request.shutdown(socket.SHUT_RDWR)
		self.request.close()
	
class UpdatePeers ( threading.Thread ):

	def run ( self ):
		global peers
		while not byeBye:
			#print(peers)
			auxPeers = []
			for p in peers:
				try:
					sockt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					address = p.split(":")
					sockt.connect( (address[0], int(address[1]) + PEER_LIST) )
					sockt.sendall(bytes(myHost +":"+ str(myPort) +"\n", ENCODING))
					dataReceived = sockt.recv(1024)
					otherPeers = str(dataReceived.decode(ENCODING)).split("\n")[:-1]
					for oP in otherPeers:
						if oP != "" and oP != (myHost +":"+ str(myPort)) and oP not in peers and oP not in auxPeers:
							auxPeers.append(oP)
				except socket.error:
					peers.remove(p)
				finally:
					sockt.close()
			
			peers += auxPeers
					
			for t in range(100):
				if not byeBye: sleep(0.1)
			

if __name__ == "__main__":
	# processing arguments
	args = sys.argv
	peers = [] # this list will contain all the peers that we will talk with
	
	if len(args) < MIN_ARGS:
		sys.stderr.write("Usage:\n")
		sys.stderr.write("\t"+ args[0] +" local-port\n")
		exit(1)
	
	myHost = socket.gethostbyname(socket.gethostname())
	myPort = int(args[1])
	myFolder = ""
	
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
	
	byeBye = False
	UpdatePeers().start()
	
	# main loop
	command = ""
	while command != "quit":
		userInput = input("> ").strip()
		inputSplitted = userInput.split(" ")
		command = inputSplitted[0]
			
		if   command == "help":
			print("Allowed commands: ")
			print("\t"+ BOLD +"addpeer"+ END_COLOR +" IP:PORT (Add the given IP:port to the list of peers")
			print("\t"+ BOLD +"list"+ END_COLOR +" shows the list of peers to which we are connected")
			print("\t"+ BOLD +"query"+ END_COLOR +" FILENAME (Search, the file name given to each of the peers)")
			print("\t"+ BOLD +"quit"+ END_COLOR +" (Returns you to a new dimension of happiness and awesomeness)")
			print("\t"+ BOLD +"setfolder"+ END_COLOR +" PATH (Set the download/upload folder to the given path)")
		elif command == "setfolder":
			if len(inputSplitted) == 2 and os.path.exists(inputSplitted[1]):
				myFolder = inputSplitted[1]
			else:
				sys.stderr.write("That folder does not exist\n")
		elif command == "addpeer":
			error = "A peer must be specified in this way:\n\tpeer-ip:peer-port\n"
			if hasErrorsAddPeer(inputSplitted): 
				sys.stderr.write(error)
			else: 
				if (myHost +":"+ str(myPort)) != inputSplitted[1] and not inputSplitted[1] in peers: 
					peers.append(inputSplitted[1])
		elif command == "list":
			print(peers)
		elif command == "query":
			if   len(myFolder) == 0:
				sys.stderr.write("First you have to set the folder.\n")
			elif len(peers) == 0:
				sys.stderr.write("You have no peers to talk with, you can add a peer with the "+ BOLD +"addpeer"+ END_COLOR +" command.\n")
			else:
				fileName = userInput.split(None, 1)
				if len(fileName) == 2: fileName = fileName[1]
				else: fileName = ""
				nameToSend = bytes(fileName + "\n", ENCODING)
				i = 0
				files = []
				sourcePeer = []
				for p in peers:
					try:
						sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
						address = p.split(":")
						sock.connect((address[0], int(address[1]) + QUERY))
						sock.sendall(nameToSend)
						aux = sock.recv(1024)
						dataReceived = aux
						while len(aux) > 0:
							aux = sock.recv(1024)
							dataReceived += aux
						filesPeer = str(dataReceived.decode(ENCODING)).split("\n")[:-1]
						if len(filesPeer) >= 1 and filesPeer[0] != "":
							files += filesPeer
							print("\nMatches in peer ("+ p +")")
							for j in range(i, len(files)):
								line = files[j]
								file = line[line.rfind(os.sep) + 1:]
								i += 1
								print("%5d\t" % i, end="")
								if fileName == "": 
									print(OK_COLOR + file + END_COLOR)
								else:
									pos = 0
									fileLower = file.lower().split(fileName.lower())
									for k in range(len(fileLower)-1):
										aux = pos + len(fileLower[k])
										print(file[pos:aux] + OK_COLOR + file[aux: aux+len(fileName)] + END_COLOR, end="")
										pos = aux + len(fileName)
									print(file[pos:pos+len(fileLower[len(fileLower)-1])])
						sourcePeer.append( (i, p) )
					except socket.error:
						pass
				if len(files) >= 1 and files[0] != "":
					numFile = ""
					while not numFile.isdigit() or int(numFile) < 0 or int(numFile) > i:
						numFile = input("\nSelect the file you want to download (0 if you want to cancel): ")
					numFile = int(numFile)
					if numFile > 0:
						k = 0
						sP = sourcePeer[k]
						while numFile > sP[0]:
							k += 1
							sP = sourcePeer[k]
						try:
							sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
							address = sP[1].split(":")
							print("Starting download...")
							sock.connect( (address[0], int(address[1]) + DOWNLOAD) )
							sock.sendall(bytes(files[numFile - 1] + "\n", ENCODING))
							f = open(myFolder + files[numFile - 1][files[numFile - 1].rfind(os.sep):], "wb")
							dataReceived = sock.recv(1024)
							f.write(dataReceived)
							while len(dataReceived) > 0:
								dataReceived = sock.recv(1024)
								f.write(dataReceived)
							f.close()
							print("Download completed ("+ (myFolder + files[numFile - 1][files[numFile - 1].rfind(os.sep):]) +")")
						except socket.error:
							sys.stderr.write("The peer is down.\n")
					
		elif command == "quit":
			byeBye = True
		elif command == "":
			pass
		else:
			sys.stderr.write("Command not found\n")
	exit(0)
