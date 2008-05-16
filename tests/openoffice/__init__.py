#!/usr/bin/python

import subprocess, sys, os, time, socket

resp = "HTTP/1.0 200 OK\nConnection: close\n\n<html>Testing</html>"

class Timing:
	def __init__(self):
		self.serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.serv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.serv.bind(('127.0.0.1', 8181))
		self.serv.listen(3)
	
	def pretiming(self):
		pass
	
	def timing(self):
		# Once the macro in this document connects, timing is done
		self.oop = subprocess.Popen(("openoffice", "openoffice/testdoc.odt"))
		
		(client, addr) = self.serv.accept()
		client.close()
	
	def posttiming(self):
		os.system("killall soffice.bin")
		self.oop.wait()
		
		# Prevent OpenOffice from trying to recover after its "crash"
		os.system("rm -f ~/.openoffice.org2/user/registry/data/org/openoffice/Office/Recovery.xcu")
	
	def close(self):
		self.serv.close()
