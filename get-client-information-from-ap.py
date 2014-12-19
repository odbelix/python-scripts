import getpass
import sys
import telnetlib

HOST = "192.168.20.135"
user = raw_input("Enter your remote account: ")
password = getpass.getpass()

tn = telnetlib.Telnet(HOST)

tn.read_until("User:")
tn.write(user + "\n")
#if password:
tn.read_until("Password:")
tn.write(password + "\n")
print tn.read_all()

print tn.read_all()

tn.write("show client ap 802.11b ap-establo-01\n" + "\n")
print tn.read_all()
