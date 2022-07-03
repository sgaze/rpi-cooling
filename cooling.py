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
from logging import Logger
import RPi.GPIO as GPIO
import Adafruit_DHT

TEMP_SENSOR = Adafruit_DHT.DHT22
TEMP_PROBE_PIN = 18  # GPIO18, pin 12
RELAY_GAIN = 4  # GPIO4 (7)


def loop(logger: Logger, temp_low: float, temp_high: float, delay: int):
    """Cooling loop

    Args:
        logger (Logger): Logger
        temp_low (float): Lower temperature
        temp_high (float): Higher temperature
        delay (int): Loop delay

    Raises:
        err: Unexpected error
    """
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RELAY_GAIN, GPIO.OUT)
    # GPIO.setwarnings(False)

    logger.info('Min=%s  Max=%s', temp_low, temp_high)

    try:
        while True:
            i = 0

            while i < 5:

                relay_state = GPIO.input(RELAY_GAIN)

                humidity, temperature = Adafruit_DHT.read_retry(
                    TEMP_SENSOR, TEMP_PROBE_PIN)

                if humidity is not None and temperature is not None:
                    system_status = 'Cooling' if relay_state else 'Idle'
                    logger.info('Temp={0:0.1f}°C  Humidity={1:0.1f}% | {2}'.format(
                        temperature,
                        humidity,
                        system_status
                    ))

                    if i == 0:
                        logger.info('Checking cooling system: %s',
                                    system_status)

                        if (
                            temperature >= temp_high
                            and not relay_state
                        ):
                            logger.info(
                                'Starting cooling system, target=%s', temp_low)
                            GPIO.output(RELAY_GAIN, GPIO.HIGH)
                        elif (
                            temperature < temp_low
                            and relay_state
                        ):
                            logger.info(
                                'Stopping cooling system, target=%s', temp_high)
                            GPIO.output(RELAY_GAIN, GPIO.LOW)

                else:
                    logger.warn('Failed to get reading. Try again!')

                i += 1
                sleep(delay)

    except KeyboardInterrupt:
        pass

    except Exception as err:
        raise err

    finally:
        GPIO.cleanup()
