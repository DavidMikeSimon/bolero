#!/usr/bin/python

import subprocess, MySQLdb, os, sys, time

class Timing:
	def __init__(self):
		pass
	
	def pretiming(self):
		self.rows = 0

	def timing(self):
		initp = subprocess.Popen(("/etc/init.d/mysql", "start"))	
		initp.wait()
		
		dbh = None
		while True:
			try:
				dbh = MySQLdb.connect("localhost", "testuser", "testpass", "testing")
			except:
				if (int(time.time()*1000) - mtstart) > 20000:
					os.kill(frecord.pid, signal.SIGINT)
					frecordp.wait()
					raise Exception("Couldn't ever connect to MySQL server!")
					sys.exit()
				else:
					time.sleep(0.0005)
			else:
				break
		
		cursor = dbh.cursor()
		cursor.execute("""select * from table1, table2 where f12 < "2008-01-10" and f12 > "2008-01-08" and f11 like 'V%' and id2 = f13 order by f22 desc limit 10""")
		self.rows = 0
		for row in cursor.fetchall():
			self.rows += 1
	
	def posttiming(self):
		deinitp = subprocess.Popen(("/etc/init.d/mysql", "stop"))
		deinitp.wait()
	
		if self.rows != 10:
			raise Exception("Wrong number of rows returned: %u instead of expected 10" % self.rows)
			sys.exit()
