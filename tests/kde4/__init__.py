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
		# Once Konqueror starts up and connects, timing is done
		self.kdep = subprocess.Popen(("startx"))
		
		while True:
			(client, addr) = self.serv.accept()
			req = client.recv(4096)
			if "GET / " in req:
				client.send(resp)
				client.close()
				return
			else:
				client.close()
	
	def posttiming(self):
		os.system("killall ksmserver")
		self.kdep.wait()
		os.system("killall dcopserver")
		os.system("killall artsd")
	
	def close(self):
		self.serv.close()
