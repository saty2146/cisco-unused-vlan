#!/usr/bin/python

import os
from devices import devices
from netmiko import ConnectHandler

def main():

    #print "Enter your cisco username:"
    #user = raw_input()
    #print "Enter your cisco password:"
    #passwd = raw_input()
    

    if os.path.exists('./files'):
        pass
    else:
        os.makedirs('./files')

    os.chdir('./files')

    for host in devices:
    
        net_connect = ConnectHandler(**devices[host])

        output= net_connect.send_command_expect('show vlan brief')
        with open(host + '_vlan_list.txt', 'w') as open_file:
            open_file.write(output)

        output= net_connect.send_command_expect('show vlan counters')
        with open(host + '_vlan_count.txt', 'w') as open_file:
            open_file.write(output)
            
        output= net_connect.send_command_expect('sh mac address-table | in static | dynamic')
        with open(host + '_mac_table.txt', 'w') as open_file:
            open_file.write(output)

    net_connect.disconnect()



#    for hostname, ip in boxes.iteritems():
#
#        client = connect(ip, user, passwd)
#        shell = client.invoke_shell()
#        print "Interactive SSH session established to %s\n" % hostname
#        send_command(shell, "terminal length 0", hostname, False)
#    
#        output  = send_command(shell, "show vlan brief", hostname, True)
#
#        with open(hostname + '_vlan.txt', 'w') as open_file:
#            #open_file.write("\n".join(output))
#            open_file.write(output)
#    
#        output  = send_command(shell, "sh vlan counters", hostname, True)
#
#        with open(hostname + '_vlan_counters.txt', 'w') as open_file:
#            #open_file.write("\n".join(output))
#            open_file.write(output)
#
#        output  = send_command(shell, "sh mac address-table | in static | dynamic", hostname, True)
#
#        with open(hostname + '_mac_table.txt', 'w') as open_file:
#            #open_file.write("\n".join(output))
#            open_file.write(output)
#
#    client.close()

if __name__ == "__main__":
    main()

