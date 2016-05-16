# SenseHat-Logger
Raspberry Pi Sense Hat logger
Program: logger.py
Version: 1.6
Author: Stein Castillo

---Short Description: 
Read the sensors from the Sense Hat and log the results in a CSV file

--- What does it do? 
SenseHat-logger reads the Sense Hat sensors (temperature, barometric pressure, humidity, accelerometer, magnetometer, gyroscope and compass) and logs the results in a CSV file. 

The program gives the user control to determine which sensors to log, the sampling frecuency and the number of samples. Additionally, it can be configured to work with the raspberry pi attached or not to a display.

--- What do you need? 
Raspberry Pi and Sense Hat (AstroPi). 
More info: https://www.raspberrypi.org/learning/getting-started-with-the-sense-hat/

--- Configuration parameters:
To control the logger, go to the logging settings section. Adjust the logging parameters accordingly:
*FILENAME: (text) Name of the CSV file. date and time will be added to allow for several versions
*WRITE_FREQUENCY: Determines the number of samples to take before committing the data to the logging file
*DELAY: (integer) Time between samples in seconds
*SAMPLES: (integer) Number of samples to take
*DATE_FORMAT: Determines the date format for the CSV file timestamp
*TIME_FORMAT: Determines the time format for the CSV file timestamp
*DISPLAY: (True/False) is the raspberry connected to a display? If true the progress will be shown in the screen
*TEMP_H: (True/False) Log temperature from humidity sensor?
*TEMP_P: (True/False) Log temperature from pressure sensor?
*HUMIDITY: (True/False) Log humidty?
*PRESSURE: (True/False) Log barometric pressure?
*ORIENTATION: (True/False) Log orientation data?
*ACCELERATION: (True/False) Log acceleration data?
*MAG: (True/False) Log magnetometer data?
*GYRO: (True/False) Log gyroscope data?
