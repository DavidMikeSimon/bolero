#!/usr/bin/python

import MySQLdb, random

words = [line.rstrip() for line in file("/usr/share/dict/words")]
def randstring(maxlen):
	s = ""
	while True:
		randword = random.choice(words)
		if s != "":
			randword = " " + randword
		if len(s) + len(randword) > maxlen:
			break
		s += randword
	return s

dbh = MySQLdb.connect("localhost", "testuser", "testpass", "testing")
cursor = dbh.cursor()

for i in range(20000):
	cursor.execute("insert into table1 (f11, f12, f13) values(%s, date_add(\"2008-01-01 12:30:00\", interval %s second), %s)",
		(randstring(120), random.randint(0, 10**6), random.randint(1, 10000)))

for i in range(10000):
	cursor.execute("insert into table2 (f21, f22) values(%s, date_add(\"2008-01-01 12:30:00\", interval %s second))",
		(randstring(50), random.randint(0, 10**6)))
