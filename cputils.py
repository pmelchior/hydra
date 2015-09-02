#!/bin/env python

from os import popen,system
import sqlite3,json
from time import time, sleep
from math import floor, ceil

wait = 5 # minutes wait time between polls

def start_hosts():
    fp = open("hosts")
    hosts = []
    for line in fp:
        if line[0] != "#":
            hosts.append(line.strip())
    fp.close()
    for host in hosts:
        print "starting get_top.py on " + host
        system('ssh ' + host + ' \'python ~/public_html/cputil/get_top.py < /dev/null >& /dev/null &\'')

def delete_entries_older_than(t, c):
    c.execute("DELETE FROM cputils WHERE time < " + str(t))

def createLast2HoursStats(c):
    starttime = time() - 120*60
    now = int(time())
    sql = "SELECT host, time, cpu, processes FROM cputils WHERE time > " + str(starttime) + " ORDER BY host, time DESC"
    c.execute(sql)
    result = c.fetchall()
    stats = {}
    for stat in result:
        host = stat[0]
        if host not in stats.keys():
            stats[host] = []
        delta_min = -(int(floor(now - stat[1])/60)/wait)*wait
        stats[host].append([delta_min, stat[2], stat[3]])
    parsed = []
    for k,v in stats.iteritems():
        host_util = {"hostname" : k, "util" : v}
        parsed.append(host_util)
    fp = open("cputils.json", "w")
    fp.write(json.dumps(parsed))
    fp.close()
    
# setup database
conn = sqlite3.connect('cputils.db')
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS cputils (host text, time integer, cpu real,mem real, processes text)")

# start cpu collecting jobs on hosts
start_hosts()
sleep(60) # make sure that stats are in DB before processing them

# poll hosts for cpu/mem utilization 
while(1):
    
    t0 = time()
    delete_entries_older_than(t0 - 60*60*24, c)
    conn.commit()
    
    createLast2HoursStats(c)
    t1 = time()
    sleep(60*wait - t1 + t0)

c.close()
conn.close()
