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
device_folder = glob.glob('/sys/bus/w1/devices/28*')
device_file = [device_folder[0] + '/w1_slave',device_folder[1] + '/w1_slave']
device_name = glob.glob('/sys/bus/w1/devices/28*/name')

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

def read_temp_raw(): #A function that grabs the raw temp data from the sensors
    f_1 = open(device_file[0], 'r')
    lines_1 = f_1.readlines()
    f_1.close()
    f_2 = open(device_file[1], 'r')
    lines_2 = f_2.readlines()
    f_2.close()
    return lines_1 + lines_2 

def read_temp(): #A function to check the connection was good and strip out the temperature
    lines = read_temp_raw()
    print(lines[0]+lines[1])
    print(lines[2]+lines[3])
    while lines[0].strip()[-3:] != 'YES' and lines[2].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t='), lines[3].find('t=')
    temp = float(lines[1][equals_pos[0]+2:])/1000, float(lines[3][equals_pos[1]+2:])/1000
    return temp


_init_influxdb_database()
while True:
    print(time.ctime())
    temp = read_temp()#get the temp
    _send_data_to_influxdb(temp)
    print('T1:'+str(temp[0])+ ' T2:'+str(temp[1]))
    #print('name_T1 : ' + str(device_name[0]) + ' name_T2 : ' + str(device_name[1]))
    time.sleep(1)
