#!/usr/bin/env python3
# -- coding: utf-8 --


import sys
import logging
import daemon
import cooling

LOG_FILE = '/var/log/apps/cooling.log'

# loop sleep in seconds
DELAY = 10

# Input parameters
if len(sys.argv) == 3:
    TEMP_LOW = float(sys.argv[1])
    TEMP_HIGH = float(sys.argv[2])
else:
    TEMP_LOW = 25
    TEMP_HIGH = 26

# Daemon context
def run():
    """run daemon
    """
    with daemon.DaemonContext():
        logging.basicConfig(format='%(asctime)s %(message)s',
                    filename=LOG_FILE,
                    level=logging.INFO)
        logger = logging.getLogger()

        cooling.loop(logger, TEMP_LOW, TEMP_HIGH, DELAY)


# main
if __name__ == "__main__":
    run()
