# Cooling

POC script to:
* retrieve temperature and humidity from a DHT22 probe.
* open relay if temperature goes beyond TEMP_LOW.
* close relay if temperature goes above TEMP_HIGH.
* publish temperature and humidity on AWS Cloudwatch.


## Pin schema

* Probe AM2302 (wired DHT22)
    * out      => GPIO18, pin 12
    * (+)      => 5V PWR, pin 2
    * (-)      => GND, pin 6
* Relay SRD-05VDC-SL-C
    * VCC      => 5V PWR, pin 2
    * GND      => GND, pin 6
    * INx      => PN2222 collector

* PN2222 transistor
    * Collector => Relay INx
    * Base      => 10k resistor => GIPO4, pin 7
    * Emitter   => GND, pin 6

## Dependencies
```
sudo apt install gpiod
sudo apt install libgpiod2

git clone https://github.com/adafruit/Adafruit_Python_DHT.git
cd Adafruit_Python_DHT
sudo python setup.py install
sudo -H pip install python-daemon
sudo -H pip install boto3
```

## Toolbox mode
`python toolbox.py 18 20`

Logs in /var/log/apps/cooling_toolbox.log

## Service mode

### Logging
Logs in /var/log/apps/cooling.log

Log rotate definition:
```
cat /etc/logrotate.d/apps
/var/log/apps/cooling.log {
  rotate 12
  weekly
  compress
  missingok
  notifempty
}
```

### Service
Service definition: /lib/systemd/system/cooling.service
```
cat /lib/systemd/system/cooling.service
[Unit]
Description=Cooling Service
After=multi-user.target
Conflicts=getty@tty1.service

[Service]
Type=simple
ExecStart=/usr/bin/python <path>/service.py 18 20
StandardInput=tty-force

[Install]
WantedBy=multi-user.target
```

Enable service:
```
sudo systemctl daemon-reload
sudo systemctl enable cooling.service
sudo systemctl start cooling.service
sudo systemctl status cooling.service
```
