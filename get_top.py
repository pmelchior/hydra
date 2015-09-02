#!/bin/env python

from os import popen
import sqlite3,json
from time import time, sleep
from os import fork, chdir, setsid, umask
from sys import exit
 

wait = 5 # minutes wait time between polls

def poll_top(t0, c):
    host = popen('hostname').read().strip().split(".")[0]
    cpus = int(popen('lscpu -p').readlines()[-1].split(",")[0]) + 1
    response = popen('top -b -n 2 | grep "Cpu(s)" -A ' + str(cpus + 4) + ' | tail -n ' + str(cpus + 5)).readlines()
    if response:
        cputil = response[0].split("%")[0][7:] # user cpu utilization, 0..100
        mem = response[1].split()
        mem_used = float(mem[3][:-1])/float(mem[1][:-1])*100 # mem utilization, 0..100
        c.execute("INSERT INTO cputils VALUES ('" + host + "', " + str(t0) + ", " + str(cputil) + "," + str(mem_used) + ",'" + ("").join(response[4:]) + "')")


def main():
    # setup database
    conn = sqlite3.connect('cputils.db')
    c = conn.cursor()
    #main daemon process loop
    while 1:
        # poll hosts for cpu/mem utilization 
        t0 = time()
        poll_top(int(t0), c)
        conn.commit()
        t1 = time()
        sleep(60*wait - t1 + t0)
    c.close()
    conn.close()

# Dual fork hack to make process run as a daemon
if __name__ == "__main__":
    try:
        pid = fork()
        if pid > 0:
            exit(0)
    except OSError, e:
        exit(1)
 
    chdir("/n/home00/melchior.12/public_html/cputil")
    setsid()
    umask(0)
    
    try:
        pid = fork()
        if pid > 0:
            exit(0)
    except OSError, e:
        exit(1)
    main()
