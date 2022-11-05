#!/usr/bin/env python3
# -- coding: utf-8 --

from time import sleep
from datetime import datetime
import RPi.GPIO as GPIO
import Adafruit_DHT
import boto3
import botocore.exceptions
from botocore.config import Config
import config


TEMP_SENSOR = Adafruit_DHT.DHT22


my_config = Config(
    region_name='eu-west-1'
)
cw = boto3.client('cloudwatch', config=my_config)


def publish_cloud_watch(timestamp: datetime, temperature: float, humidity: float):
    """Publish to CloudWatch

    Args:
        timestamp (datetime): Timestamp
        temperature (float): Temperature
        humidity (float): Humidity
    """
    cw.put_metric_data(
        Namespace='RaspberryPi',
        MetricData=[
            {
                'MetricName': 'Temperature',
                'Dimensions': [
                    {
                        'Name': 'Cooling',
                        'Value': 'DHT22',
                    }
                ],
                'Timestamp': timestamp.isoformat(),
                'Value': temperature,
                'Unit': 'Count',
            },
            {
                'MetricName': 'Humidity',
                'Dimensions': [
                    {
                        'Name': 'Cooling',
                        'Value': 'DHT22',
                    }
                ],
                'Timestamp': timestamp.isoformat(),
                'Value': humidity,
                'Unit': 'Count',
            },
        ],
    )


def loop():
    """Cooling loop

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
            now = datetime.now()
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
                    refresh_time_diff = (now - last_refresh_time)
                    refresh_switch = refresh_time_diff.total_seconds() > 60

                if refresh_switch:
                    # Publish to CloudWatch
                    try:
                        publish_cloud_watch(now, temperature, humidity)
                        logger.info('Published %s %s on CloudWatch', temperature, humidity)
                    except botocore.exceptions.ClientError:
                        logger.warning(
                            'Failed to publish %s %s on CloudWatch', temperature, humidity)

                    logger.info('Device state: Min=%s  Max=%s | %s',
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
                    last_refresh_time = now

            else:
                logger.warning('Failed to get reading. Try again!')

            sleep(delay)

    except KeyboardInterrupt:
        pass

    except Exception as err:
        raise err

    finally:
        GPIO.cleanup()
