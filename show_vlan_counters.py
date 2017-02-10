#!/usr/bin/python

import argparse
import re
import os
import sys
import pandas as pd
from devices import devices

pd.set_option('display.max_columns', None)

def check_arg(args=None):

    parser = argparse.ArgumentParser(description='Cisco find unused VLANs')
    maingroup = parser.add_argument_group(title='optional')
    maingroup.add_argument('-m0', '--mac_zero',
                           help='show VLANs with ZERO MACs in mac-address-table table',
                           action='store_true')
    maingroup.add_argument('-c0', '--frame_zero',
                           help='show VLANs with ZERO FRAMES in vlan counters',
                           action='store_true')
    maingroup.add_argument('-s', '--static_entry',
                           help='show only static MACs entries in mac-address-table',
                           action='store_true')
    maingroup.add_argument('-d', '--dynamic_entry',
                           help='show only dynamic MACs entries in mac-address-table',
                           action='store_true')
    maingroup.add_argument('-v', '--vlan_id',
                           help='show only dynamic MACs entries in mac-address-table',
                           default=None)

    result = parser.parse_args(args)

    return (result.mac_zero,
            result.frame_zero,
            result.static_entry,
            result.dynamic_entry,
            result.vlan_id
            )

def join_vlans(hosts):
    
    vlans = {}
    vlan_regex = re.compile(r'^\d{1,4}')
    
    for host in devices:
        with open(host + '_vlan_list.txt', 'r') as open_file:
            for line in open_file:
                line_list = line.split(" ")
                line_list = filter(None, line_list)
                mo_vlan = re.search(vlan_regex, line_list[0])
                if mo_vlan:
                    vlans.setdefault(int(mo_vlan.group()), line_list[1])
    return vlans

def dict_to_df(d):
    df=pd.DataFrame(d.items())
    df.set_index(0, inplace=True)
    df.index.name = 'vlan'
    df.rename(columns={1 : 'name'}, inplace = True)
    return df

def vlan_macs(hosts, vlans):

    columns_static = []
    columns_dynamic = []

    for host in hosts:
        columns_static.append(host + 'S')
    for host in hosts:
        columns_dynamic.append(host + 'D')

    index_vlans = vlans.keys()
    columns = columns_static + columns_dynamic
    df1 = dict_to_df(vlans)
    

    df2 = pd.DataFrame(index=vlans, columns=columns)
    df2 = df2.fillna(0)
    df  = pd.concat([df1, df2], axis=1)

    for host in hosts: 
        with open(host + '_mac_table.txt', 'r') as open_file:
            lines = open_file.readlines()[1:-1]
            for line in lines:
                line_list = line.split(" ")
                line_list = filter(None, line_list)
                line_list = filter(lambda name: name[:] != "*", line_list)
                line_list = filter(lambda name: name[:] != "R", line_list)
                
                if 'N/A' not in line and '---' not in line:
                    #print line_list
                    vlan  = int(line_list[0])
                    type_entry = str(line_list[2])
                    #mac_address = str(line_list[1])
                    if vlan in df.index:
                        if type_entry == 'static':
                            df.ix[vlan, host + 'S'] += 1
                        else:
                            df.ix[vlan, host + 'D'] += 1
                    else:
                        pass
    return (df, columns_static, columns_dynamic)

def main():
    
    mac_zero, frame_zero, static_entry, dynamic_entry, vlan_id = check_arg(sys.argv[1:])
    
    hosts = []

    for key in devices:
        hosts.append(key)
   
    os.chdir('./files')

    vlans = join_vlans(hosts)
    df, columns_static, columns_dynamic = vlan_macs(hosts, vlans)
    df.sort_index(inplace=True)
    #print df.iloc[:]

    if mac_zero and static_entry:
        df = df[columns_static]
        df = df.loc[(df==0).all(1)]
        print(df.to_string())

    elif mac_zero and dynamic_entry:
        df = df[columns_dynamic]
        df = df.loc[(df==0).all(1)]
        print(df.to_string())

    elif mac_zero:
        df = df[columns_static + columns_dynamic]
        df = df.loc[(df==0).all(1)]
        print(df.to_string())
    else:
        print(df.to_string())

if __name__ == "__main__":
    main()
