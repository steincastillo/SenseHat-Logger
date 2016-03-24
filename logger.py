#Sense Hat Logger
#Program: logger.py
#Version 1.5
#Author: Stein Castillo
#Date: Mar 19 2016

#################
### Libraries ###
#################

from sense_hat import SenseHat
from datetime import datetime
from time import sleep
from threading import Thread
import os


########################
### Logging Settings ###
########################

FILENAME = "senselog"
WRITE_FREQUENCY = 5
DELAY = 120
SAMPLES = 260
DATE_FORMAT = "%Y"+"-"+"%m"+"-"+"%d"+"_"+"%H"+":"+"%M"+":"+"%S" #2016-03-16_17:23:15
DISPLAY = True

TEMP_H = True
TEMP_P = True
HUMIDITY = True
PRESSURE = True
ORIENTATION = False
ACCELERATION = False
MAG = True
GYRO = False

#define sensor hat display colors
R = [255, 0, 0]     #red
O = [255, 127, 0]   #orange
Y = [255, 255, 0]   #yellow
G = [0, 255, 0]     #green
B = [0, 0, 255]     #black
I = [75, 0, 130]    #pink
V = [159, 0, 255]   #violet
E = [0, 0, 0]       #empty/black

#################
### Functions ###
#################

#this function reads the cpu temperature
def cpu_temp():
    tx = os.popen('/opt/vc/bin/vcgencmd measure_temp')
    cputemp = tx.read()
    cputemp = cputemp.replace('temp=','')
    cputemp = cputemp.replace('\'C\n','')
    cputemp = float(cputemp)
    return cputemp

def log_data():
    log_line = ",".join(str(value) for value in sense_data)
    batch_data.append(log_line)

def timed_log():
    while True:
        log_data()
        sleep(DELAY)

def blinking_led():
    while tot_samples < SAMPLES:
        sense.set_pixel(3, 0, G)
        sense.set_pixel(4, 0, G)
        sleep(1)
        sense.set_pixel(3, 0, E)
        sense.set_pixel(4, 0, E)
        sleep(1)
    sense.clear()

def file_setup(filename):
    header = []
    if TEMP_H:
        header.append("temp_h")
    if TEMP_P:
        header.append("temp_p")
    if HUMIDITY:
        header.append("humidity")
    if PRESSURE:
        header.append("pressure")
    if ORIENTATION:
        header.extend(["pitch", "roll", "yaw"])
    if MAG:
        header.extend(["mag_x", "mag_y", "mag_z"])
    if ACCELERATION:
        header.extend(["accel_x", "accel_y", "accel_z"])
    if GYRO:
        header.extend(["gyro_x", "gyro_y", "gyro_z"])
    header.append("timestamp")

    with open(filename, "w") as f:
        f.write(",".join(str(value) for value in header) + "\n")
        

#This function reads all the SenseHat sensors
def get_sense_data():

    sense_data = []

    cpu = cpu_temp()

    if TEMP_H:
        temp = sense.get_temperature_from_humidity()
        temp = temp-(cpu-temp)
        temp = round(temp,1)
        sense_data.append(temp)
        
    if TEMP_P:
        temp = sense.get_temperature_from_pressure()
        temp = temp-(cpu-temp)
        temp = round(temp,1)
        sense_data.append(temp)

    if HUMIDITY:
        sense_data.append(round(sense.get_humidity(),1))

    if PRESSURE:
        sense_data.append(round(sense.get_pressure(),1))

    #Read orientation data
    if ORIENTATION:
        yaw,pitch,roll = sense.get_orientation().values()
        yaw = round(yaw,2)
        pitch = round(pitch,2)
        roll = round(roll,2)
        sense_data.extend([pitch, roll, yaw])

    #Read compass data
    if MAG:
        mag_x,mag_y,mag_z = sense.get_compass_raw().values()
        mag_x = round(mag_x,2)
        mag_y = round(mag_y,2)
        mag_z = round(mag_z,2)
        sense_data.extend([mag_x, mag_y, mag_z])

    #Read accelerometer data
    if ACCELERATION:
        x,y,z = sense.get_accelerometer_raw().values()
        x = round(x,2)
        y = round(y,2)
        z = round(z,2)
        sense_data.extend ([x, y, z])
        
    #Read gyroscope data
    if GYRO:
        gyro_x,gyro_y,gyro_z = sense.get_gyroscope_raw().values()
        gyro_x = round(gyro_x,2)
        gyro_y = round(gyro_y,2)
        gyro_z = round(gyro_z,2)
        sense_data.extend([gyro_x, gyro_y, gyro_z])

    sense_data.append(datetime.now())
    return sense_data

#################
### Main Loop ###
#################

sense = SenseHat()
batch_data = []
tot_samples = 0


#Set the logging file name
time = datetime.now()
time = datetime.strftime(time, DATE_FORMAT)
if FILENAME == "":    
    filename = "SenseLog_"+str(time)+".csv"
else:
    filename = FILENAME+"_"+str(time)+".csv"

file_setup(filename)

if DISPLAY:
    print("\n")
    print("*****************************************")
    print("*         Sense Hat Logger              *")
    print("*                                       *")
    print("*           Version: 1.5                *")
    print("*****************************************")
    print("\n")
    print("Creating file: "+filename)
    print("Logging Initiated!")
    print("****************")

Thread(target=blinking_led).start()

if DELAY > 0:
    sense_data = get_sense_data()
    Thread(target=timed_log).start()

while tot_samples < SAMPLES:
    #print("reading sensors")
    sense_data = get_sense_data()
    if DELAY == 0:
        log_data()
        
    if len(batch_data) >= WRITE_FREQUENCY:
        if DISPLAY:
            print("Writing to file...")
            for line in batch_data:
                print(line)
            #calculate sampling progress
            tot_samples += WRITE_FREQUENCY
            progress = int((tot_samples/SAMPLES)*100)
            progress = str(progress)
            #sense.show_letter(progress[0])
            print("Sampling progress: "+progress+"%")
        with open(filename, "a") as f:
            for line in batch_data:
                f.write(line + "\n")
            batch_data = []
            f.flush()

f.close()

print ("Process complete!")
sense.clear()
