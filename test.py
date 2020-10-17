import os
import glob
import time
import logging
from influxdb import InfluxDBClient

INFLUXDB_ADDRESS = '10.100.100.187'
INFLUXDB_USER = 'mydb'
INFLUXDB_PASSWORD = 'cjboat'
INFLUXDB_DATABASE = 'db_version2'

influxdb_client = InfluxDBClient(INFLUXDB_ADDRESS, 8086, INFLUXDB_USER, INFLUXDB_PASSWORD, None)

#these tow lines mount the device:
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
 
base_dir = '/sys/bus/w1/devices/'
device_path = glob.glob(base_dir + '28*')[0] #get file path of sensor
rom = device_path.split('/')[-1] #get rom name
logging.basicConfig(filename='temperature.log', filemode='a', format='%(created)f%(message)s', level=logging.INFO)

def _init_influxdb_database():
    print('access to init database')
    databases = influxdb_client.get_list_database()
    if len(list(filter(lambda x: x['name'] == INFLUXDB_DATABASE, databases))) == 0:
        influxdb_client.create_database(INFLUXDB_DATABASE)
    influxdb_client.switch_database(INFLUXDB_DATABASE)

def _send_data_to_influxdb(temp):
    json_body = [
            {
                "measurement": "temperature",
                "tags": {
                    "location": "sensor1"
                }, 
                "fields": {
                    "value": temp
                }
            }
        ]
    influxdb_client.write_points(json_body)

def read_temp_raw():
    with open(device_path +'/w1_slave','r') as f:
        valid, temp = f.readlines()
    return valid, temp
 
def read_temp():
    valid, temp = read_temp_raw()

    while 'YES' not in valid:
        time.sleep(0.2)
        valid, temp = read_temp_raw()

    pos = temp.index('t=')
    if pos != -1:
        #read the temperature .
        temp_string = temp[pos+2:]
        temp_c = float(temp_string)/1000.0 
        temp_f = temp_c * (9.0 / 5.0) + 32.0
        return temp_c, temp_f
 
print(' ROM: '+ rom)

while True:
    _init_influxdb_database()
    c, f = read_temp()
    print('C={:,.3f} F={:,.3f}'.format(c, f))
    _send_data_to_influxdb(c)
    logging.info(' Temp={0:0.3f} C '.format(c))
    time.sleep(1)

