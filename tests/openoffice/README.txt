This is a test suite for timing startup of the OpenOffice2 suite.
It's assumed that you're running the test within X; that is, a
single X session is kept up throughout the test session, unlike
the KDE4 test, where each individual sample involves starting up
and stopping a new X session.

Before running the test, make sure that when testdoc.odt is opened
by OpenOffice, you get an error about being unable to connect to
a socket. This indicates that OpenOffice is correctly attempting
to run a macro as the document is loaded.

The macro security setting in OpenOffice may need to be reduced
in order to get this to work.
