#!/usr/bin/python
"""
Get useful vlan info from Cisco devices:

show vlan brief
show vlan counters
show mac address-table | in static | dynamic

and write its to files for futher processing

"""

import os
from devices import devices
from netmiko import ConnectHandler

def main():

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
            
        output= net_connect.send_command_expect('show mac address-table | in static | dynamic')
        with open(host + '_mac_table.txt', 'w') as open_file:
            open_file.write(output)

    net_connect.disconnect()

if __name__ == "__main__":
    main()
