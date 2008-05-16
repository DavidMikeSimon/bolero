This is a system for testing the startup speed of X+KDE4.

To set up this test:
- Copy the desktop file in this directory to kde4's Autostart directory.
- Make sure that running "startx" will start KDE4 and Konqueror to a localhost:8181 URL

The request from Konqueror to the local port is what triggers the end of the test.
