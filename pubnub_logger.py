#Sense Hat Logger
#Program: pubnub_logger.py
#Version 2.0
#Author: Stein Castillo
#Date: Mar 19 2016

#################
### Libraries ###
#################

from sense_hat import SenseHat
from datetime import datetime
from time import sleep
from threading import Thread
from pubnub import Pubnub
import os
import smtplib
import sys

########################
### Logging Settings ###
########################

#Set sampling universe and rate
DELAY = 60       #Delay between samples in seconds
SAMPLES = 60    #Number of samples to take

#Set sensors to read/log
TEMP_H = True   #Temperature from humidity sensor
TEMP_P = True   #Temperature from pressure sensor
TEMP_R = True   #"real" temperature corrected for CPU heat effect
HUMIDITY = True 
PRESSURE = True 
ORIENTATION = False
ACCELERATION = False
MAG = False
GYRO = False

#Set other logging parameters
FILENAME = "test"
WRITE_FREQUENCY = 10
DISPLAY = True  #Raspberry pi connected to a display?
ECHO = True  #Display values as they are measured?
EMAIL = False #Send email when the process is complete?

#set emailing parameters
smtpUser = "raspberrymonitor641@gmail.com"  #email account
smtpPass = "jebret83"          #email password
fromAdd = smtpUser
toAdd = "stein@americamail.com"      #email recipient

#define sensor hat display colors
R = [255, 0, 0]     #red
O = [255, 127, 0]   #orange
Y = [255, 255, 0]   #yellow
G = [0, 255, 0]     #green
B = [0, 0, 255]     #black
I = [75, 0, 130]    #pink
V = [159, 0, 255]   #violet
E = [0, 0, 0]       #empty/black

#Set date and time formats
DATE_FORMAT = "%Y"+"-"+"%m"+"-"+"%d"+"_"+"%H"+":"+"%M"+":"+"%S" #2016-03-16_17:23:15
TIME_FORMAT = "%H"+":"+"%M"+":"+"%S" #22:11:30

#Pubnub channel settings
pubnub = Pubnub(
            publish_key   = "pub-c-4c366fe0-5497-4f20-af8b-eb46de436dd7",
			subscribe_key = "sub-c-8b69ef34-30ce-11e6-b700-0619f8945a4f"
                )
TEMPCHANNEL = "tempeon"
HUMCHANNEL = "humeon"
FREEBOARD = "freebrd"

led_level = 255

#################
### Functions ###
#################

#This function reads the cpu temperature
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

#This function displays 2 digit temperature reading on the hat display (upper section)
def display_temp():
    while tot_samples < SAMPLES:
        #display temperature on the hat
        cpu = cpu_temp()
        
        #calculation to correct for the CPU temperature effect on temperature sensors
        #verified against a standalone temperature gauge for raspberry B+
        temp1 = sense.get_temperature_from_humidity()
        temp2 = sense.get_temperature_from_pressure()
        temp3 = sense.get_temperature()
        temp = (temp1+temp2+temp3)/3
        temp = temp-(cpu/5)        
        temp = round(temp,1)
        temp_int = int(temp)
        temp_dis = str(temp_int)

        temp_num_matrix_1(temp_dis[0])
        temp_num_matrix_2(temp_dis[1])

        hum = round(sense.get_humidity(),1)
        press = round(sense.get_pressure(),1)

        if ECHO:
            print("\t".join(str(value) for value in sense_data))

            #publish temperature readings in PUBNUB
            pubnub.publish(
                channel = TEMPCHANNEL,
                message =
                {"eon":
                {"Temp":temp}}
                )
            #publish Pressure readings in PUBNUB
            pubnub.publish(
                channel = HUMCHANNEL,
                message =
                {"eon":
                {"Humidity":hum}}
                )

            #publish data for freeboard
            pubnub.publish(
                channel = FREEBOARD,
                message =
                {"temp": temp, "humidity": hum, "pressure": press}
                )


        sleep(DELAY)
    sense.clear()

#This functions sets the .CSV file header
def file_setup(filename):
    header = []
    if TEMP_H:
        header.append("temp_h")
    if TEMP_P:
        header.append("temp_p")
    if TEMP_R:
        header.append("temp_r")
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

    #Log temperature from humidity sensor
    if TEMP_H:
        temp = sense.get_temperature_from_humidity()
        temp = temp-(cpu-temp)
        temp = round(temp,1)
        sense_data.append(temp)

    #Log temperature from pressure sensor             
    if TEMP_P:
        temp = sense.get_temperature_from_pressure()
        temp = temp-(cpu-temp)
        temp = round(temp,1)
        sense_data.append(temp)

    #Log "real" temperature corrected for CPU heat effect
    if TEMP_R:
        temp1 = sense.get_temperature()
        temp2 = sense.get_temperature_from_pressure()
        temp3 = sense.get_temperature_from_humidity()
        temp = ((temp1+temp2+temp3)/3)-(cpu/5)
        temp = round(temp,1)
        sense_data.append(temp)

    #Log humidity
    if HUMIDITY:
        sense_data.append(round(sense.get_humidity(),1))

    #Log atmospheric pressure
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

def send_email(header, body):
    email = smtplib.SMTP("smtp.gmail.com", 587)
    email.ehlo()
    email.starttls()
    email.ehlo()
    email.login(smtpUser, smtpPass)
    email.sendmail(fromAdd, toAdd, header + "\n\n" + body)
    email.quit()

def disp_logo(time):
    image = [
    E,E,E,R,R,R,E,E,
    E,E,E,R,E,R,E,E,
    E,E,E,R,E,E,E,E,
    E,E,R,R,R,E,E,E,
    E,E,R,R,R,E,E,E,
    E,E,E,R,E,E,E,E,
    E,R,E,R,E,E,E,E,
    E,R,R,R,E,E,E,E
    ]
    sense.set_pixels(image)
    sleep(time)
    sense.clear()

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

#display initia logo for 3 seconds
disp_logo(3)

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
    print("*           Version: 2.0                *")
    print("*****************************************")
    print("\n")
    print("Creating file: "+filename)
    print("Sense Hat Logging Initiated!")
    print("****************************\n")
    

Thread(target=display_temp).start()

if DELAY > 0:
    sense_data = get_sense_data()
    Thread(target=timed_log).start()

while tot_samples < SAMPLES:
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
    timestamp = datetime.now()
    timestamp = datetime.strftime(timestamp, TIME_FORMAT)
    mailsubject= "Sampling process completed!"
    mailbody = "Sense Hat logger process successfully completed at " + timestamp + "\n\n" + \
               "A total of " + str(SAMPLES) + " samples were taken with a frecuency of " + \
               str(DELAY) + " seconds"
    mailheader = "To: " + toAdd + "\n" + "From: " + fromAdd + "\n" + "Subject: " + mailsubject
    send_email(mailheader, mailbody)

if DISPLAY:
    print ("*****************")
    print ("Process complete!")
    print ("Created file: "+filename)
    print ("Total samples: " + str(SAMPLES))
    print ("*****************")
