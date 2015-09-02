#!/bin/env python

from os import system
from sys import argv
import json
from time import sleep

if len(argv) < 2:
    print "usage: " + argv[0] + " <job file>"
    exit(1)

def push_to_hosts(config):
    counter = 0
    counting = False
    sleep_time = 1
    try:
        counting = config['counting']
        counter = config['min_count']
        max_count = config['max_count']
        sleep_time = config['sleep_time']
    except KeyError:
        pass
    
    for host in config['hosts']:
        if counting:
            if counter > max_count:
                break

        for i in range(host['cpus']):
            command = 'ssh ' + host['name'] + ' \''
            if counting:
                command += config['command'] % counter
            else:
                command += config['command']
            if config['listen']:
                command += '\''
            else:
                command += ' < /dev/null >& /dev/null &\''

            if counting:
                if counter > max_count:
                    break
                print "starting job %d on %s" % (counter, host['name']) 
            else:
                print "starting job %d on %s" % (i, host['name']) 

            system(command)
            sleep(sleep_time)
            counter += 1

    if counting:
        print "submitted jobs %d/%d" % (counter-1, max_count)
    else:
        print "submitted %d jobs" % (counter-1)

# read the job file
fp = open(argv[1])
config = json.load(fp)
push_to_hosts(config)
fp.close()
