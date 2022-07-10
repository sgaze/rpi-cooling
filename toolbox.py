#!/usr/bin/env python3
# -- coding: utf-8 --

import logging
import config
import cooling

logging.basicConfig(format='%(asctime)s %(message)s',
            filename=config.LOG_FILE,
            level=logging.INFO)
cooling.loop()
