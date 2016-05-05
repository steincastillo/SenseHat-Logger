#Sense Hat Logger
#Program: logger.py
#Version 1.9
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
import smtplib


########################
### Logging Settings ###
########################

FILENAME = "senselog"
WRITE_FREQUENCY = 5

DELAY = 2       #Delay between samples in seconds
SAMPLES = 10    #Number of samples to take

DATE_FORMAT = "%Y"+"-"+"%m"+"-"+"%d"+"_"+"%H"+":"+"%M"+":"+"%S" #2016-03-16_17:23:15
TIME_FORMAT = "%H"+":"+"%M"+":"+"%S" #22:11:30
DISPLAY = True  #Raspberry pi connected to a display?
EMAIL = False #Send email when the process is finished?

#Set sensors to read/log
TEMP_H = True
TEMP_P = True
HUMIDITY = True
PRESSURE = True
ORIENTATION = False
ACCELERATION = False
MAG = False
GYRO = False

#set emailing parameters
smtpUser = "email_account"  #email account
smtpPass = "email_password"                 #email password
fromAdd = smtpUser
toAdd = "mail_recepient"             #email recipient

led_level = 255

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

#this functions display 2 digit temperature reading on the hat display (upper section)
def blinking_led():
    while tot_samples < SAMPLES:
        #display temperature on the hat
        cpu = cpu_temp()
        temp = sense.get_temperature_from_humidity()
        temp = temp-(cpu-temp)
        temp = round(temp,1)
        temp_int = int(temp)
        temp_dis = str(temp_int)
        temp_num_matrix_1(temp_dis[0])
        temp_num_matrix_2(temp_dis[1])
        sleep(DELAY)
        # sense.set_pixel(3, 0, G)
        # sense.set_pixel(4, 0, G)
        # sleep(1)
        # sense.set_pixel(3, 0, E)
        # sense.set_pixel(4, 0, E)
    sense.clear()

#This functions sets the .CSV file header
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
        

#This function reads the SenseHat sensors
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

    #Log orientation data
    if ORIENTATION:
        yaw,pitch,roll = sense.get_orientation().values()
        yaw = round(yaw,2)
        pitch = round(pitch,2)
        roll = round(roll,2)
        sense_data.extend([pitch, roll, yaw])

    #Log compass data
    if MAG:
        mag_x,mag_y,mag_z = sense.get_compass_raw().values()
        mag_x = round(mag_x,2)
        mag_y = round(mag_y,2)
        mag_z = round(mag_z,2)
        sense_data.extend([mag_x, mag_y, mag_z])

    #Log accelerometer data
    if ACCELERATION:
        x,y,z = sense.get_accelerometer_raw().values()
        x = round(x,2)
        y = round(y,2)
        z = round(z,2)
        sense_data.extend ([x, y, z])
        
    #Log gyroscope data
    if GYRO:
        gyro_x,gyro_y,gyro_z = sense.get_gyroscope_raw().values()
        gyro_x = round(gyro_x,2)
        gyro_y = round(gyro_y,2)
        gyro_z = round(gyro_z,2)
        sense_data.extend([gyro_x, gyro_y, gyro_z])

    #Log the time stamp
    time_stamp = datetime.now()
    time_stamp = datetime.strftime(time_stamp, TIME_FORMAT)
    sense_data.append(time_stamp)
    return sense_data

#define sensor hat display colors
R = [255, 0, 0]     #red
O = [255, 127, 0]   #orange
Y = [255, 255, 0]   #yellow
G = [0, 255, 0]     #green
B = [0, 0, 255]     #black
I = [75, 0, 130]    #pink
V = [159, 0, 255]   #violet
E = [0, 0, 0]       #empty/black

def temp_num_matrix_1(num):

  if num == '0':
        # number 0_top_left - TEMPERATURE
    sense.set_pixel(0, 0, led_level, 0, 0)   
    sense.set_pixel(0, 1, led_level, 0, 0)   
    sense.set_pixel(0, 2, led_level, 0, 0)   
    sense.set_pixel(0, 3, led_level, 0, 0)
    sense.set_pixel(1, 0, led_level, 0, 0)   
    sense.set_pixel(1, 1, 0, 0, 0)   
    sense.set_pixel(1, 2, 0, 0, 0)   
    sense.set_pixel(1, 3, led_level, 0, 0)
    sense.set_pixel(2, 0, led_level, 0, 0)   
    sense.set_pixel(2, 1, led_level, 0, 0)   
    sense.set_pixel(2, 2, led_level, 0, 0)   
    sense.set_pixel(2, 3, led_level, 0, 0)
    sense.set_pixel(3, 0, 0, 0, 0)   
    sense.set_pixel(3, 1, 0, 0, 0)   
    sense.set_pixel(3, 2, 0, 0, 0)   
    sense.set_pixel(3, 3, 0, 0, 0)

  if num == '1':
        # number 1_top_left - TEMPERATURE
    sense.set_pixel(0, 0, 0, 0, 0)   
    sense.set_pixel(0, 1, led_level, 0, 0)   
    sense.set_pixel(0, 2, 0, 0, 0)   
    sense.set_pixel(0, 3, led_level, 0, 0)
    sense.set_pixel(1, 0, led_level, 0, 0)   
    sense.set_pixel(1, 1, led_level, 0, 0)   
    sense.set_pixel(1, 2, led_level, 0, 0)   
    sense.set_pixel(1, 3, led_level, 0, 0)
    sense.set_pixel(2, 0, 0, 0, 0)   
    sense.set_pixel(2, 1, 0, 0, 0)   
    sense.set_pixel(2, 2, 0, 0, 0)   
    sense.set_pixel(2, 3, led_level, 0, 0)
    sense.set_pixel(3, 0, 0, 0, 0)   
    sense.set_pixel(3, 1, 0, 0, 0)   
    sense.set_pixel(3, 2, 0, 0, 0)   
    sense.set_pixel(3, 3, 0, 0, 0)

  if num == '2':
        # number 2_top_left - TEMPERATURE
    sense.set_pixel(0, 0, led_level, 0, 0)   
    sense.set_pixel(0, 1, 0, 0, 0)   
    sense.set_pixel(0, 2, 0, 0, 0)   
    sense.set_pixel(0, 3, led_level, 0, 0)
    sense.set_pixel(1, 0, led_level, 0, 0)   
    sense.set_pixel(1, 1, 0, 0, 0)   
    sense.set_pixel(1, 2, led_level, 0, 0)   
    sense.set_pixel(1, 3, led_level, 0, 0)
    sense.set_pixel(2, 0, led_level, 0, 0)   
    sense.set_pixel(2, 1, led_level, 0, 0)   
    sense.set_pixel(2, 2, 0, 0, 0)   
    sense.set_pixel(2, 3, led_level, 0, 0)
    sense.set_pixel(3, 0, 0, 0, 0)   
    sense.set_pixel(3, 1, 0, 0, 0)   
    sense.set_pixel(3, 2, 0, 0, 0)   
    sense.set_pixel(3, 3, 0, 0, 0)

  if num == '3':
        # number 3_top_left - TEMPERATURE
    sense.set_pixel(0, 0, led_level, 0, 0)   
    sense.set_pixel(0, 1, 0, 0, 0)   
    sense.set_pixel(0, 2, 0, 0, 0)   
    sense.set_pixel(0, 3, led_level, 0, 0)
    sense.set_pixel(1, 0, led_level, 0, 0)   
    sense.set_pixel(1, 1, led_level, 0, 0)   
    sense.set_pixel(1, 2, 0, 0, 0)   
    sense.set_pixel(1, 3, led_level, 0, 0)
    sense.set_pixel(2, 0, led_level, 0, 0)   
    sense.set_pixel(2, 1, led_level, 0, 0)   
    sense.set_pixel(2, 2, led_level, 0, 0)   
    sense.set_pixel(2, 3, led_level, 0, 0)
    sense.set_pixel(3, 0, 0, 0, 0)   
    sense.set_pixel(3, 1, 0, 0, 0)   
    sense.set_pixel(3, 2, 0, 0, 0)   
    sense.set_pixel(3, 3, 0, 0, 0)

  if num == '4':
        # number 4_top_left - TEMPERATURE
    sense.set_pixel(0, 0, led_level, 0, 0)   
    sense.set_pixel(0, 1, led_level, 0, 0)   
    sense.set_pixel(0, 2, led_level, 0, 0)   
    sense.set_pixel(0, 3, 0, 0, 0)
    sense.set_pixel(1, 0, 0, 0, 0)   
    sense.set_pixel(1, 1, 0, 0, 0)   
    sense.set_pixel(1, 2, led_level, 0, 0)   
    sense.set_pixel(1, 3, 0, 0, 0)
    sense.set_pixel(2, 0, 0, 0, 0)   
    sense.set_pixel(2, 1, led_level, 0, 0)   
    sense.set_pixel(2, 2, led_level, 0, 0)   
    sense.set_pixel(2, 3, led_level, 0, 0)
    sense.set_pixel(3, 0, 0, 0, 0)   
    sense.set_pixel(3, 1, 0, 0, 0)   
    sense.set_pixel(3, 2, 0, 0, 0)   
    sense.set_pixel(3, 3, 0, 0, 0)

  if num == '5':
        # number 5_top_left - TEMPERATURE
    sense.set_pixel(0, 0, led_level, 0, 0)   
    sense.set_pixel(0, 1, led_level, 0, 0)   
    sense.set_pixel(0, 2, 0, 0, 0)   
    sense.set_pixel(0, 3, led_level, 0, 0)
    sense.set_pixel(1, 0, led_level, 0, 0)   
    sense.set_pixel(1, 1, 0, 0, 0)   
    sense.set_pixel(1, 2, led_level, 0, 0)   
    sense.set_pixel(1, 3, led_level, 0, 0)
    sense.set_pixel(2, 0, led_level, 0, 0)   
    sense.set_pixel(2, 1, 0, 0, 0)   
    sense.set_pixel(2, 2, 0, 0, 0)   
    sense.set_pixel(2, 3, led_level, 0, 0)
    sense.set_pixel(3, 0, 0, 0, 0)   
    sense.set_pixel(3, 1, 0, 0, 0)   
    sense.set_pixel(3, 2, 0, 0, 0)   
    sense.set_pixel(3, 3, 0, 0, 0)

  if num == '6':
        # number 6_top_left - TEMPERATURE
    sense.set_pixel(0, 0, led_level, 0, 0)   
    sense.set_pixel(0, 1, led_level, 0, 0)   
    sense.set_pixel(0, 2, led_level, 0, 0)   
    sense.set_pixel(0, 3, led_level, 0, 0)
    sense.set_pixel(1, 0, 0, 0, 0)   
    sense.set_pixel(1, 1, led_level, 0, 0)   
    sense.set_pixel(1, 2, 0, 0, 0)   
    sense.set_pixel(1, 3, led_level, 0, 0)
    sense.set_pixel(2, 0, 0, 0, 0)   
    sense.set_pixel(2, 1, led_level, 0, 0)   
    sense.set_pixel(2, 2, led_level, 0, 0)   
    sense.set_pixel(2, 3, led_level, 0, 0)
    sense.set_pixel(3, 0, 0, 0, 0)   
    sense.set_pixel(3, 1, 0, 0, 0)   
    sense.set_pixel(3, 2, 0, 0, 0)   
    sense.set_pixel(3, 3, 0, 0, 0)

  if num == '7':
        # number 7_top_left - TEMPERATURE
    sense.set_pixel(0, 0, led_level, 0, 0)   
    sense.set_pixel(0, 1, led_level, 0, 0)   
    sense.set_pixel(0, 2, 0, 0, 0)   
    sense.set_pixel(0, 3, 0, 0, 0)
    sense.set_pixel(1, 0, led_level, 0, 0)   
    sense.set_pixel(1, 1, 0, 0, 0)   
    sense.set_pixel(1, 2, 0, 0, 0)   
    sense.set_pixel(1, 3, 0, 0, 0)
    sense.set_pixel(2, 0, led_level, 0, 0)   
    sense.set_pixel(2, 1, led_level, 0, 0)   
    sense.set_pixel(2, 2, led_level, 0, 0)   
    sense.set_pixel(2, 3, led_level, 0, 0)
    sense.set_pixel(3, 0, 0, 0, 0)   
    sense.set_pixel(3, 1, 0, 0, 0)   
    sense.set_pixel(3, 2, 0, 0, 0)   
    sense.set_pixel(3, 3, 0, 0, 0)
  
  if num == '8':
        # number 8_top_left - TEMPERATURE
    sense.set_pixel(0, 0, led_level, 0, 0)   
    sense.set_pixel(0, 1, led_level, 0, 0)   
    sense.set_pixel(0, 2, led_level, 0, 0)   
    sense.set_pixel(0, 3, led_level, 0, 0)
    sense.set_pixel(1, 0, led_level, 0, 0)   
    sense.set_pixel(1, 1, 0, 0, 0)   
    sense.set_pixel(1, 2, led_level, 0, 0)   
    sense.set_pixel(1, 3, led_level, 0, 0)
    sense.set_pixel(2, 0, led_level, 0, 0)   
    sense.set_pixel(2, 1, led_level, 0, 0)   
    sense.set_pixel(2, 2, led_level, 0, 0)   
    sense.set_pixel(2, 3, led_level, 0, 0)
    sense.set_pixel(3, 0, 0, 0, 0)   
    sense.set_pixel(3, 1, 0, 0, 0)   
    sense.set_pixel(3, 2, 0, 0, 0)   
    sense.set_pixel(3, 3, 0, 0, 0)

  if num == '9':
        # number 9_top_left - TEMPERATURE
    sense.set_pixel(0, 0, led_level, 0, 0)   
    sense.set_pixel(0, 1, led_level, 0, 0)   
    sense.set_pixel(0, 2, led_level, 0, 0)   
    sense.set_pixel(0, 3, 0, 0, 0)
    sense.set_pixel(1, 0, led_level, 0, 0)   
    sense.set_pixel(1, 1, 0, 0, 0)   
    sense.set_pixel(1, 2, led_level, 0, 0)   
    sense.set_pixel(1, 3, 0, 0, 0)
    sense.set_pixel(2, 0, led_level, 0, 0)   
    sense.set_pixel(2, 1, led_level, 0, 0)   
    sense.set_pixel(2, 2, led_level, 0, 0)   
    sense.set_pixel(2, 3, led_level, 0, 0)
    sense.set_pixel(3, 0, 0, 0, 0)   
    sense.set_pixel(3, 1, 0, 0, 0)   
    sense.set_pixel(3, 2, 0, 0, 0)   
    sense.set_pixel(3, 3, 0, 0, 0)

def temp_num_matrix_2(num):
    
  if num == '0':
        # number 0_top_right - TEMPERATURE
    sense.set_pixel(4, 0, led_level, 0, 0)   
    sense.set_pixel(4, 1, led_level, 0, 0)   
    sense.set_pixel(4, 2, led_level, 0, 0)   
    sense.set_pixel(4, 3, led_level, 0, 0)
    sense.set_pixel(5, 0, led_level, 0, 0)   
    sense.set_pixel(5, 1, 0, 0, 0)   
    sense.set_pixel(5, 2, 0, 0, 0)   
    sense.set_pixel(5, 3, led_level, 0, 0)
    sense.set_pixel(6, 0, led_level, 0, 0)   
    sense.set_pixel(6, 1, led_level, 0, 0)   
    sense.set_pixel(6, 2, led_level, 0, 0)   
    sense.set_pixel(6, 3, led_level, 0, 0)
    sense.set_pixel(7, 0, 0, 0, 0)   
    sense.set_pixel(7, 1, 0, 0, 0)   
    sense.set_pixel(7, 2, 0, 0, 0)   
    sense.set_pixel(7, 3, 0, 0, 0)

  if num == '1':
        # number 1_top_right - TEMPERATURE
    sense.set_pixel(4, 0, 0, 0, 0)   
    sense.set_pixel(4, 1, led_level, 0, 0)   
    sense.set_pixel(4, 2, 0, 0, 0)   
    sense.set_pixel(4, 3, led_level, 0, 0)
    sense.set_pixel(5, 0, led_level, 0, 0)   
    sense.set_pixel(5, 1, led_level, 0, 0)   
    sense.set_pixel(5, 2, led_level, 0, 0)   
    sense.set_pixel(5, 3, led_level, 0, 0)
    sense.set_pixel(6, 0, 0, 0, 0)   
    sense.set_pixel(6, 1, 0, 0, 0)   
    sense.set_pixel(6, 2, 0, 0, 0)   
    sense.set_pixel(6, 3, led_level, 0, 0)
    sense.set_pixel(7, 0, 0, 0, 0)   
    sense.set_pixel(7, 1, 0, 0, 0)   
    sense.set_pixel(7, 2, 0, 0, 0)   
    sense.set_pixel(7, 3, 0, 0, 0)

  if num == '2':
        # number 2_top_right - TEMPERATURE
    sense.set_pixel(4, 0, led_level, 0, 0)   
    sense.set_pixel(4, 1, 0, 0, 0)   
    sense.set_pixel(4, 2, 0, 0, 0)   
    sense.set_pixel(4, 3, led_level, 0, 0)
    sense.set_pixel(5, 0, led_level, 0, 0)   
    sense.set_pixel(5, 1, 0, 0, 0)   
    sense.set_pixel(5, 2, led_level, 0, 0)   
    sense.set_pixel(5, 3, led_level, 0, 0)
    sense.set_pixel(6, 0, led_level, 0, 0)   
    sense.set_pixel(6, 1, led_level, 0, 0)   
    sense.set_pixel(6, 2, 0, 0, 0)   
    sense.set_pixel(6, 3, led_level, 0, 0)
    sense.set_pixel(7, 0, 0, 0, 0)   
    sense.set_pixel(7, 1, 0, 0, 0)   
    sense.set_pixel(7, 2, 0, 0, 0)   
    sense.set_pixel(7, 3, 0, 0, 0)

  if num == '3':
        # number 3_top_right - TEMPERATURE
    sense.set_pixel(4, 0, led_level, 0, 0)   
    sense.set_pixel(4, 1, 0, 0, 0)   
    sense.set_pixel(4, 2, 0, 0, 0)   
    sense.set_pixel(4, 3, led_level, 0, 0)
    sense.set_pixel(5, 0, led_level, 0, 0)   
    sense.set_pixel(5, 1, led_level, 0, 0)   
    sense.set_pixel(5, 2, 0, 0, 0)   
    sense.set_pixel(5, 3, led_level, 0, 0)
    sense.set_pixel(6, 0, led_level, 0, 0)   
    sense.set_pixel(6, 1, led_level, 0, 0)   
    sense.set_pixel(6, 2, led_level, 0, 0)   
    sense.set_pixel(6, 3, led_level, 0, 0)
    sense.set_pixel(7, 0, 0, 0, 0)   
    sense.set_pixel(7, 1, 0, 0, 0)   
    sense.set_pixel(7, 2, 0, 0, 0)   
    sense.set_pixel(7, 3, 0, 0, 0)

  if num == '4':
        # number 4_top_right - TEMPERATURE
    sense.set_pixel(4, 0, led_level, 0, 0)   
    sense.set_pixel(4, 1, led_level, 0, 0)   
    sense.set_pixel(4, 2, led_level, 0, 0)   
    sense.set_pixel(4, 3, 0, 0, 0)
    sense.set_pixel(5, 0, 0, 0, 0)   
    sense.set_pixel(5, 1, 0, 0, 0)   
    sense.set_pixel(5, 2, led_level, 0, 0)   
    sense.set_pixel(5, 3, 0, 0, 0)
    sense.set_pixel(6, 0, 0, 0, 0)   
    sense.set_pixel(6, 1, led_level, 0, 0)   
    sense.set_pixel(6, 2, led_level, 0, 0)   
    sense.set_pixel(6, 3, led_level, 0, 0)
    sense.set_pixel(7, 0, 0, 0, 0)   
    sense.set_pixel(7, 1, 0, 0, 0)   
    sense.set_pixel(7, 2, 0, 0, 0)   
    sense.set_pixel(7, 3, 0, 0, 0)

  if num == '5':
        # number 5_top_right - TEMPERATURE
    sense.set_pixel(4, 0, led_level, 0, 0)   
    sense.set_pixel(4, 1, led_level, 0, 0)   
    sense.set_pixel(4, 2, 0, 0, 0)   
    sense.set_pixel(4, 3, led_level, 0, 0)
    sense.set_pixel(5, 0, led_level, 0, 0)   
    sense.set_pixel(5, 1, 0, 0, 0)   
    sense.set_pixel(5, 2, led_level, 0, 0)   
    sense.set_pixel(5, 3, led_level, 0, 0)
    sense.set_pixel(6, 0, led_level, 0, 0)   
    sense.set_pixel(6, 1, 0, 0, 0)   
    sense.set_pixel(6, 2, 0, 0, 0)   
    sense.set_pixel(6, 3, led_level, 0, 0)
    sense.set_pixel(7, 0, 0, 0, 0)   
    sense.set_pixel(7, 1, 0, 0, 0)   
    sense.set_pixel(7, 2, 0, 0, 0)   
    sense.set_pixel(7, 3, 0, 0, 0)

  if num == '6':
        # number 6_top_right - TEMPERATURE
    sense.set_pixel(4, 0, led_level, 0, 0)   
    sense.set_pixel(4, 1, led_level, 0, 0)   
    sense.set_pixel(4, 2, led_level, 0, 0)   
    sense.set_pixel(4, 3, led_level, 0, 0)
    sense.set_pixel(5, 0, 0, 0, 0)   
    sense.set_pixel(5, 1, led_level, 0, 0)   
    sense.set_pixel(5, 2, 0, 0, 0)   
    sense.set_pixel(5, 3, led_level, 0, 0)
    sense.set_pixel(6, 0, 0, 0, 0)   
    sense.set_pixel(6, 1, led_level, 0, 0)   
    sense.set_pixel(6, 2, led_level, 0, 0)   
    sense.set_pixel(6, 3, led_level, 0, 0)
    sense.set_pixel(7, 0, 0, 0, 0)   
    sense.set_pixel(7, 1, 0, 0, 0)   
    sense.set_pixel(7, 2, 0, 0, 0)   
    sense.set_pixel(7, 3, 0, 0, 0)

  if num == '7':
        # number 7_top_right - TEMPERATURE
    sense.set_pixel(4, 0, led_level, 0, 0)   
    sense.set_pixel(4, 1, led_level, 0, 0)   
    sense.set_pixel(4, 2, 0, 0, 0)   
    sense.set_pixel(4, 3, 0, 0, 0)
    sense.set_pixel(5, 0, led_level, 0, 0)   
    sense.set_pixel(5, 1, 0, 0, 0)   
    sense.set_pixel(5, 2, 0, 0, 0)   
    sense.set_pixel(5, 3, 0, 0, 0)
    sense.set_pixel(6, 0, led_level, 0, 0)   
    sense.set_pixel(6, 1, led_level, 0, 0)   
    sense.set_pixel(6, 2, led_level, 0, 0)   
    sense.set_pixel(6, 3, led_level, 0, 0)
    sense.set_pixel(7, 0, 0, 0, 0)   
    sense.set_pixel(7, 1, 0, 0, 0)   
    sense.set_pixel(7, 2, 0, 0, 0)   
    sense.set_pixel(7, 3, 0, 0, 0)

  if num == '8':
        # number 8_top_right - TEMPERATURE
    sense.set_pixel(4, 0, led_level, 0, 0)   
    sense.set_pixel(4, 1, led_level, 0, 0)   
    sense.set_pixel(4, 2, led_level, 0, 0)   
    sense.set_pixel(4, 3, led_level, 0, 0)
    sense.set_pixel(5, 0, led_level, 0, 0)   
    sense.set_pixel(5, 1, 0, 0, 0)   
    sense.set_pixel(5, 2, led_level, 0, 0)   
    sense.set_pixel(5, 3, led_level, 0, 0)
    sense.set_pixel(6, 0, led_level, 0, 0)   
    sense.set_pixel(6, 1, led_level, 0, 0)   
    sense.set_pixel(6, 2, led_level, 0, 0)   
    sense.set_pixel(6, 3, led_level, 0, 0)
    sense.set_pixel(7, 0, 0, 0, 0)   
    sense.set_pixel(7, 1, 0, 0, 0)   
    sense.set_pixel(7, 2, 0, 0, 0)   
    sense.set_pixel(7, 3, 0, 0, 0)

  if num == '9':
        # number 9_top_right - TEMPERATURE
    sense.set_pixel(4, 0, led_level, 0, 0)   
    sense.set_pixel(4, 1, led_level, 0, 0)   
    sense.set_pixel(4, 2, led_level, 0, 0)   
    sense.set_pixel(4, 3, 0, 0, 0)
    sense.set_pixel(5, 0, led_level, 0, 0)   
    sense.set_pixel(5, 1, 0, 0, 0)   
    sense.set_pixel(5, 2, led_level, 0, 0)
    sense.set_pixel(5, 3, 0, 0, 0)
    sense.set_pixel(6, 0, led_level, 0, 0)   
    sense.set_pixel(6, 1, led_level, 0, 0)   
    sense.set_pixel(6, 2, led_level, 0, 0)   
    sense.set_pixel(6, 3, led_level, 0, 0)
    sense.set_pixel(7, 0, 0, 0, 0)   
    sense.set_pixel(7, 1, 0, 0, 0)   
    sense.set_pixel(7, 2, 0, 0, 0)   
    sense.set_pixel(7, 3, 0, 0, 0)

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
    print("*           Version: 1.9                *")
    print("*****************************************")
    print("\n")
    print("Creating file: "+filename)
    print("Sense Hat Logging Initiated!")
    print("****************\n")

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
        tot_samples += WRITE_FREQUENCY
        if DISPLAY:
            print("Writing to file...")
            for line in batch_data:
                print(line)
            #calculate sampling progress
            progress = int((tot_samples/SAMPLES)*100)
            progress = str(progress)
            #sense.show_letter(progress[0])
            print("Sampling progress: "+progress+"%")
            print ("\n")
        with open(filename, "a") as f:
            for line in batch_data:
                f.write(line + "\n")
            batch_data = []
            f.flush()

f.close()
sense.clear() #clear SenseHat display

if EMAIL:
    if DISPLAY:
        print ("Sendig email...")
    email = smtplib.SMTP("smtp.gmail.com", 587)
    timestamp = datetime.now()
    timestamp = datetime.strftime(timestamp, TIME_FORMAT)
    mailsubject= "Sampling process completed!"
    mailbody = "Sense Hat logger process successfully completed at " + timestamp + "\n\n" + \
               "A total of " + str(SAMPLES) + " samples were taken with a frecuency of " + \
               str(DELAY) + " seconds"
    header = "To: " + toAdd + "\n" + "From: " + fromAdd + "\n" + "Subject: " + mailsubject
    email.ehlo()
    email.starttls()
    email.ehlo()
    email.login(smtpUser, smtpPass)
    email.sendmail(fromAdd, toAdd, header + "\n\n" + mailbody)
    email.quit()


if DISPLAY:
    print ("*****************")
    print ("Process complete!")
    print ("Created file: "+filename)
    print ("Total samples: " + str(SAMPLES))
    print ("*****************")
