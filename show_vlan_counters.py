#!/usr/bin/python

import argparse
import re
import os
import sys
import pandas as pd
from hosts import boxes

pd.set_option('display.max_columns', None)

def check_arg(args=None):

    parser = argparse.ArgumentParser(description='Cisco find unused VLANs')
    maingroup = parser.add_argument_group(title='optional')
    maingroup.add_argument('-m', '--mac_zero',
                           help='show VLANs with ZERO MACs in mac-address-table table',
                           action='store_true')
    maingroup.add_argument('-c', '--frame_zero',
                           help='show VLANs with ZERO FRAMES in vlan counters',
                           action='store_true')

    results = parser.parse_args(args)

    return (results.mac_zero,
            results.frame_zero,
            )

def join_vlans(hosts):
    
    vlans = []
    vlan_regex = re.compile(r'^\d{1,4}')
    
    for host in hosts:
        with open(host + '_vlan.txt', 'r') as open_file:
            for line in open_file:
                line_list = line.split(" ")
                mo_vlan = re.search(vlan_regex, line_list[0])
                if mo_vlan:
                    vlans.append(mo_vlan.group())

    vlans = set(vlans)
    vlans_sorted = sorted(vlans, key = int)

    return vlans_sorted

def vlan_macs(hosts, vlans):

    columns = []

    for host in hosts:
        columns.append(host + 'S')
    for host in hosts:
        columns.append(host + 'D')

    df = pd.DataFrame(index=vlans, columns=columns)
    df = df.fillna(0)
    #df.set_value('1', 'sit2_s', 10)
    

    for host in hosts: 
        with open(host + '_mac_table.txt', 'r') as open_file:
            lines = open_file.readlines()[1:-1]
            for line in lines:
                line_list = line.split(" ")
                line_list = filter(None, line_list)
                line_list = filter(lambda name: name[:] != "*", line_list)
                line_list = filter(lambda name: name[:] != "R", line_list)
                
                if line_list[0] == "R":
                    print line_list[0]

                if 'N/A' not in line and '---' not in line:
                    #print line_list
                    vlan  = str(line_list[0])
                    type_entry = str(line_list[2])
                    #mac_address = str(line_list[1])
                    if vlan in df.index:
                        if type_entry == 'static':
                            df.ix[vlan, host + 'S'] += 1
                        else:
                            df.ix[vlan, host + 'D'] += 1
                    else:
                        pass
    return df

def main():
    
    mac_zero, frame_zero = check_arg(sys.argv[1:])
    
    hosts = []

    for key in boxes:
        hosts.append(key)
   

    os.chdir('./files')

    vlans = join_vlans(hosts)
    #print vlans
    df = vlan_macs(hosts, vlans)

    if mac_zero:
        df_zero = df.loc[(df==0).all(1)]
        print(df_zero.to_string())
    else:
        print(df.to_string())


 
                    

    #print df.head(100)
    #print df.ix['112']
    #df_zero = df[any(df[df.columns[1:]] != 0, axis=1)]
    #df_zero = df.loc[(df[1:]==0).any(axis=1)]
    #print(df.to_string())
    


if __name__ == "__main__":
    main()
