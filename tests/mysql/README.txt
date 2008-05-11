This is a system for testing the startup speed and/or file usage of MySQL.

table-setup.py : A script that I wrote to insert random values into the test tables.
teststate.sql : The schema and data of the test database used for my measurements.
run.py : This is the actual testing script: clears cache, starts mysql, does query, stops mysql

Note that if you want to do this test yourself, you'll have to create a database "testing"
which allows selects from a user "testuser" identified by password "testpass", and then
run "mysql < teststate.sql" to populate that database with the test tables.
