#!/usr/bin/python

import paramiko
import StringIO
import sys, getopt
import time
import argparse
import socket
import re
import os
from hosts import boxes


def connect(host, user, passwd):
    
    try:
        # Create instance of SSHClient object
        client = paramiko.SSHClient()

        # Automatically add untrusted hosts 
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # initiate SSH connection
        client.connect(host, username=user, password=passwd, timeout=5, look_for_keys=False, allow_agent=False)
        print "SSH connection established to %s\n" % host
       
        return client
    
    except paramiko.AuthenticationException:
        print "Authentication failed when connecting to %s" % host
        sys.exit(1)
    
    except socket.timeout:
        sys.exit("Connection timeout")

def send_command(shell, command, hostname, should_print):      

    receive_buffer = ""
    command = command.rstrip()
    shell.send(command + '\n')
    time.sleep(10)
    receive_buffer = shell.recv(1000000)
    output = StringIO.StringIO(receive_buffer)
    contents = output.getvalue()
    return contents

def main():

    print "Enter your cisco username:"
    user = raw_input()
    print "Enter your cisco password:"
    passwd = raw_input()

    if os.path.exists('./files'):
        pass
    else:
        os.makedirs('./files')

        os.chdir('./files')

    for hostname, ip in boxes.iteritems():

        client = connect(ip, user, passwd)
        shell = client.invoke_shell()
        print "Interactive SSH session established to %s\n" % hostname
        send_command(shell, "terminal length 0", hostname, False)
    
        output  = send_command(shell, "show vlan brief", hostname, True)

        with open(hostname + '_vlan.txt', 'w') as open_file:
            #open_file.write("\n".join(output))
            open_file.write(output)
    
        output  = send_command(shell, "sh vlan counters", hostname, True)

        with open(hostname + '_vlan_counters.txt', 'w') as open_file:
            #open_file.write("\n".join(output))
            open_file.write(output)

        output  = send_command(shell, "sh mac address-table | in static | dynamic", hostname, True)

        with open(hostname + '_mac_table.txt', 'w') as open_file:
            #open_file.write("\n".join(output))
            open_file.write(output)

    client.close()

if __name__ == "__main__":
    main()

