#Importing all the libraries and modules that are required
import smtplib
import time
import json
from threading import Thread
from time import sleep
try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus
from bme280 import BME280
from threading import Lock
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit
async_mode = None

#Initial declaration of variables
Temperature = "No sensor data!"
Pressure = "No sensor data!"
Humidity = "No sensor data!"
NewDate = 0
CurrentDate = 0
ServerTime = time.strftime('%d-%m-%Y %H:%M:%S')

currentMeasurements = {
               "temperature":"0",
               "pressure":"0",
                "humidity":"0",
                "date": ServerTime
               }


#Setting up the variables as global
from app import Temperature
from app import Pressure
from app import Humidity
from app import NewDate
from app import CurrentDate
from app import ServerTime


# creating the write to file thread
def WriteToFile_thread():
    while True:
        sleep(20)
        currentMeasurements = {
            "temperature":Temperature,
            "pressure":Pressure,
            "humidity":Humidity,
            "date": ServerTime
            }
        if Temperature and Humidity and Pressure !=0:
            writeMeasurementsToJSON(currentMeasurements)
            print("##########-Writing to File-##########")
       
    


#Setup of the server
app = Flask(__name__)
app.config['SECRET_KEY'] = 'HRISTOsecretKey!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None #Set thread to none
thread_lock = Lock() #Lock thread
bus = SMBus(1)
sensor = BME280(i2c_dev=bus)
#sensor = bme680.BME680()#Naming the sensor for use in the code

def ReadSensorValues():# this function will read the data from the sensors and the current time and return those values
    
    global Temperature
    global Pressure
    global Humidity
    global ServerTime
    
    Temperature =sensor.get_temperature()
    Pressure = sensor.get_pressure()
    Humidity = sensor.get_humidity()
    ServerTime = time.strftime('%d-%m-%Y %H:%M:%S')#Getting the server time with format
    return


def background_thread():#Defining the thread fucntion to read and update sensor data to the flask server
    SEC_FOR_UPDATE = 1
    while True:
        socketio.sleep(SEC_FOR_UPDATE)#sleep for 1 second

        ReadSensorValues()
        
        socketio.emit('my_response',
                      {'data': 'Server generated event','T' : '{0:.2f}'.format(sensor.get_temperature()), 'P' : '{0:.2f}'.format(sensor.get_pressure()),
                       'H' : '{0:.2f}%RH'.format(sensor.get_humidity()),'S':ServerTime},
                      namespace='/Weather')#Send the sensor data and date to the server as messages T for temperature etc.
                      


def writeMeasurementsToJSON(currentMeasurements, filename='data.json'):
    with open(filename,'r+') as file:
          # First we load existing data into a dict.
        file_data = json.load(file)
        # Join currentMeasurements with the existing data inside measurements
        file_data["measurements"].append(currentMeasurements)
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
        json.dump(file_data, file, indent = 4)
 




@app.route('/')#Enable to use the hmtl page for displaying
def index():
    return render_template('index.html', async_mode=socketio.async_mode)




@socketio.on('connect', namespace='/Weather')#Testing the connection to the server
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread)# connect and start background_thread
            #threadWriting = Thread(target = WriteToFile_thread)#initiate a new thread 
            #threadWriting.setDaemon(True) # make the thread deamonic i.e makes the thread run at the background until the main thread is terminated
            #threadWriting.start()
    emit('my_response', {'data': 'Connected','T':'Reading...','P':'Reading...','H':'Reading...','S':'Starting...'})#To be displayed when the server is loaded
    
    


if __name__ == '__main__':#Run server
    socketio.run(app, debug=True)
    #threadWriting.join()
    print("writing thread finished...exiting")

    
