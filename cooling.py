#!/usr/bin/env python3
# -- coding: utf-8 --

# Dependencies
# sudo apt install gpiod
# sudo apt install libgpiod2
# git clone https://github.com/adafruit/Adafruit_Python_DHT.git
# cd Adafruit_Python_DHT
# sudo python setup.py install
# sudo -H pip install python-daemon

# Logging
# definition: /etc/logrotate.d/apps
# destination: /var/log/apps/cooling

# Service
# definition: /lib/systemd/system/cooling.service
# sudo systemctl start cooling.service

# Schema


from time import sleep
from datetime import datetime
import RPi.GPIO as GPIO
import Adafruit_DHT
import config

TEMP_SENSOR = Adafruit_DHT.DHT22


def loop():
    """Cooling loop

    Args:
        logger (Logger): Logger
        temp_low (float): Lower temperature
        temp_high (float): Higher temperature
        delay (int): Loop delay

    Raises:
        err: Unexpected error
    """
    relay_gain = config.RELAY_GAIN
    temp_low = config.TEMP_LOW
    temp_high = config.TEMP_HIGH
    delay = config.DELAY
    logger = config.LOGGER

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(relay_gain, GPIO.OUT)
    # GPIO.setwarnings(False)

    logger.info('Starting: Min=%s  Max=%s', temp_low, temp_high)

    try:
        last_refresh_time = None
        refresh_switch = True

        while True:
            relay_state = GPIO.input(relay_gain)

            humidity, temperature = Adafruit_DHT.read_retry(
                TEMP_SENSOR, config.TEMP_PROBE_PIN)

            if (
                humidity is not None
                and temperature is not None
            ):
                system_status = 'Cooling' if relay_state else 'Idle'
                logger.info('Temp={0:0.1f}°C  Humidity={1:0.1f}% | {2}'.format(
                    temperature,
                    humidity,
                    system_status
                ))

                # Switch cooling no more often than every 60s
                if last_refresh_time:
                    refresh_time_diff = (datetime.now() - last_refresh_time)
                    refresh_switch = refresh_time_diff.total_seconds() > 60

                if refresh_switch:
                    logger.info('Probing: Min=%s  Max=%s | %s',
                                temp_low, temp_high, system_status)

                    if (
                        temperature >= temp_high
                        and not relay_state
                    ):
                        logger.info(
                            'Starting cooling, target=%s', temp_low)
                        GPIO.output(relay_gain, GPIO.HIGH)
                    elif (
                        temperature < temp_low
                        and relay_state
                    ):
                        logger.info(
                            'Stopping cooling, target=%s', temp_high)
                        GPIO.output(relay_gain, GPIO.LOW)

                    # Last successful switch refresh
                    last_refresh_time = datetime.now()

            else:
                logger.warn('Failed to get reading. Try again!')

            sleep(delay)

    except KeyboardInterrupt:
        pass

    except Exception as err:
        raise err

    finally:
        GPIO.cleanup()
