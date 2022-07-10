#!/usr/bin/env python3
# -- coding: utf-8 --


import daemon
import logging
import config
import cooling

# Daemon context
def run():
    """run daemon
    """
    with daemon.DaemonContext():
        logging.basicConfig(format='%(asctime)s %(message)s',
                    filename=config.LOG_FILE_SERVICE,
                    level=logging.INFO)
        cooling.loop()


# main
if __name__ == "__main__":
    run()
