#!/usr/bin/env python3
import sys
import os
import socket
import socketserver
import threading

# constants
VERSION     = "p+2 0.0.0.0.0.0.0.0.1.0 superAlpha"
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
<<<<<<< HEAD
		elif (e.lower().find(pattern) != -1): 	 matchingFiles.append(path[len(myFolder) + 1:] + os.sep + e)
=======
		elif (e.lower().find(pattern) != -1):    matchingFiles.append(path[len(myFolder) + 1:] + os.sep + e)
>>>>>>> query
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

# some classes needed
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
		self.request.close()
		# self.server.close() # test this!

class Query(socketserver.BaseRequestHandler):

	def handle(self):
		data = self.request.recv(1024)
		pattern = str(data.decode(ENCODING))[:-1]
<<<<<<< HEAD
		foundFiles = searchFiles(myFolder, pattern.lower())
		# sending the list of files that match
		msg = "\n".join(foundFiles)
=======
		msg = ""
		if os.path.exists(myFolder):
			foundFiles = searchFiles(myFolder, pattern.lower())
			# sending the list of files that match
			msg += "\n".join(foundFiles)
>>>>>>> query
		msg += "\n"
		response = bytes(msg, ENCODING)
		self.request.send(response)
		self.request.close()

class Upload(socketserver.BaseRequestHandler):

	def handle(self):
		data = self.request.recv(1024)
		fileName = os.sep + str(data.decode(ENCODING))[:-1]
		try:
			f = open(myFolder + fileName, "rb")
			fileContent = f.read()
		finally:
			f.close()
		# sending the file
		self.request.send(fileContent)
		self.request.close()

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
	pass

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
	
	# main loop
	command = ""
	while command != "quit":
<<<<<<< HEAD
		command = input()
	
	exit(0)
=======
		userInput = input("> ")
		inputSplitted = userInput.split(" ")
		command = inputSplitted[0]
			
		if   command == "help":
			print("Allowed commands: ")
			print("\t"+ BOLD +"setfolder"+ END_COLOR +" PATH (Set the download/upload folder to the given path)")
			print("\t"+ BOLD +"addpeer"+ END_COLOR +" IP:PORT (Add the given IP:port to the list of peers")
			print("\t"+ BOLD +"query"+ END_COLOR +" FILENAME (Search, the file name given to each of the peers)")
			print("\t"+ BOLD +"quit"+ END_COLOR +" (Returns you to a new dimension of happiness and awesomeness, now you have all the porn of the world)")
		elif command == "setfolder":
			if len(inputSplitted) == 2 and os.path.exists(inputSplitted[1]):
				myFolder = inputSplitted[1]
			else:
				print("That folder does not exist")
		elif command == "addpeer":
			error = "A peer must be specified in this way:\n\tpeer-ip:peer-port"
			if hasErrorsAddPeer(inputSplitted): print(error)
			else: peers.append(inputSplitted[1])
		elif command == "query" and len(myFolder) == 0:
			print("First, you have to set the folder.")
		elif command == "query" and len(peers) == 0:
			print("First, you have to add a new peer.")
		elif command == "query":
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
					dataReceived = sock.recv(1024)
					filesPeer = str(dataReceived.decode(ENCODING)).split("\n")[:-1]
					files += filesPeer
					if len(filesPeer) >= 1 and filesPeer[0] != "":
						print("\nMatches in peer (" + p + "):")
						for j in range(i, len(files)):
							line = files[j]
							file = line[line.rfind(os.sep) + 1:]
							i += 1
							print("%5d\t" % i, end="")
							if fileName == "": 
								print(OK_COLOR + file + END_COLOR)
							else:
								file = file.split(fileName)
								for k in range(len(file)-1):
									print(file[k] + OK_COLOR + fileName + END_COLOR, end="")
								print(file[len(file)-1])
					sourcePeer.append( (i, p) )
				except:
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
						sock.connect( (address[0], int(address[1]) + DOWNLOAD) )
						sock.sendall(bytes(files[numFile - 1] + "\n", ENCODING))
						f = open(myFolder + files[numFile - 1][files[numFile - 1].rfind(os.sep):], "wb")
						dataReceived = sock.recv(1024)
						#dataReceived = str(dataReceived.decode(ENCODING))
						#f.write(bytes(dataReceived, ENCODING))
						f.close()
					except socket.error:
						print("The peer is down.")
					
		elif command == "quit":
			pass
		elif command == "":
			pass
		else:
			print("Command not found")
	exit(0)
>>>>>>> query
