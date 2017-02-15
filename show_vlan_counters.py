#!/usr/bin/python
"""
Get vlan_list and mac_table downloaded by get_vlan_info.py and create DataFrame
vlan information through all devices in one table
"""
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
    maingroup.add_argument('-z', '--mac_zero',
                           help='show VLANs with ZERO MACs in mac-address-table table',
                           action='store_true')
    maingroup.add_argument('-s', '--static',
                           help='show only static MACs entries in mac-address-table',
                           action='store_true')
    maingroup.add_argument('-d', '--dynamic',
                           help='show only dynamic MACs entries in mac-address-table',
                           action='store_true')
    maingroup.add_argument('-v', '--vlan_id',
                           help='show only dynamic MACs entries in mac-address-table',
                           default=None)

    result = parser.parse_args(args)

    return (result.mac_zero,
            result.static,
            result.dynamic,
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

    column_static = []
    column_dynamic = []

    for host in hosts:
        column_static.append(host + 'S')

    for host in hosts:
        column_dynamic.append(host + 'D')

    index_vlans = vlans.keys()
    columns = column_static + column_dynamic
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
                    
                    vlan  = int(line_list[0])
                    type_entry = str(line_list[2])

                    if vlan in df.index:
                        if type_entry == 'static':
                            df.ix[vlan, host + 'S'] += 1
                        else:
                            df.ix[vlan, host + 'D'] += 1
                    else:
                        pass
    return (df, column_static, column_dynamic)

def main():
    
    mac_zero, static, dynamic, vlan_id = check_arg(sys.argv[1:])
    
    hosts = []
    columns = []

    for key in devices:
        hosts.append(key)
   
    os.chdir('./files')

    vlans = join_vlans(hosts)
    df, column_static, column_dynamic = vlan_macs(hosts, vlans)

    df.sort_index(inplace=True)
    name_static = list(column_static)
    name_static.insert(0,'name')
    name_dynamic = list(column_dynamic)
    name_dynamic.insert(0,'name')
    

    if static and dynamic:
        df = df[name_static + column_dynamic]
        columns = list(column_static + column_dynamic)
    elif static:
        df = df[name_static]
        columns = list(column_static)
    elif dynamic:
        df = df[name_dynamic]
        columns = list(column_dynamic)
    else:
        columns = [name_static + column_dynamic]
    
    if mac_zero:
        df = df.loc[(df[columns]==0).all(1)]
    else:
        pass

    df.replace({0: '-'}, regex=True, inplace=True)
    print(df.to_string())

if __name__ == "__main__":
    main()
