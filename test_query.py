#!/usr/bin/python
# This file is: /usr/share/cacti/site/scripts/flow_temps.py

import os, glob, time, sys, datetime
from influxdb import InfluxDBClient

INFLUXDB_ADDRESS = '10.100.100.188'
INFLUXDB_USER = 'mydb'
INFLUXDB_PASSWORD = 'cjboat'
INFLUXDB_DATABASE = 'db_version2'

influxdb_client = InfluxDBClient(INFLUXDB_ADDRESS, 8086, INFLUXDB_USER, INFLUXDB_PASSWORD, None)
#Set up the location of the DS18B20 sensors in the system


def _init_influxdb_database():
    print('access to init database')
    databases = influxdb_client.get_list_database()
    if len(list(filter(lambda x: x['name'] == INFLUXDB_DATABASE, databases))) == 0:
        influxdb_client.create_database(INFLUXDB_DATABASE)
    influxdb_client.switch_database(INFLUXDB_DATABASE)

def _send_data_to_influxdb(temp):
    json_body1 = [
            {
                "measurement": "temperature",
                "tags": {
                    "location": "sensor1"
                }, 
                "fields": {
                    "value": temp[0]
                }
            }
        ]
    json_body2 = [
            {
                "measurement": "temperature",
                "tags": {
                    "location": "sensor2"
                }, 
                "fields": {
                    "value": temp[1]
                }
            }
        ]
    influxdb_client.write_points(json_body1)
    influxdb_client.write_points(json_body2)
    print('Success write data to InfluxDB')




_init_influxdb_database()
while True:
    print("access to while")
    result = influxdb_client.query('SELECT * FROM temperature;')
    result.raw
    print(result.raw)
    time.sleep(10)
