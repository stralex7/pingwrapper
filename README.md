# pingwrapper
This is a simple wrapper to record timestamps when ICMP ECHO REPLY is not received.

QUICK HOWTO:

chmod +x ./pw.py
./pw.py ping -D -O -W.5 <dst_ip>

This code is based on https://gist.github.com/jaddison/d4966f9e789d1d6e987fda49638a284b
