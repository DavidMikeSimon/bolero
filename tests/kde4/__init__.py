#!/usr/bin/python

import subprocess, sys, os, time, socket

class Timing:
	def __init__(self):
		self.serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.serv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.serv.bind(('127.0.0.1', 8080))
		self.serv.listen(3)
	
	def pretiming(self):
		pass
	
	def timing(self):
		# Once Konqueror starts up and connects, timing is done
		self.kdep = subprocess.Popen(("startx"))
		(client, addr) = self.serv.accept()
		client.close()
	
	def posttiming(self):
		os.system("killall ksmserver")
		self.kdep.wait()
