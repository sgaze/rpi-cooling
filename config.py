# config

import sys
import logging

TEMP_PROBE_PIN = 18  # GPIO18, pin 12
RELAY_GAIN = 4  # GPIO4 (7)

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

# Logger
LOGGER = logging.getLogger('cooling')