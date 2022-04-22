# Importing all the libraries and modules that are required
from app import ServerTime
from app import CurrentDate
from app import NewDate
from app import Humidity
from app import Pressure
from app import Temperature
import smtplib
import os.path
import time
import json
from threading import Thread
from time import sleep
from datetime import timedelta
from IPython.display import display
import csv
import pandas as pd
import matplotlib.pyplot as plt
import warnings
from sklearn.metrics import mean_squared_error as MSE
from math import sqrt
import itertools
import statsmodels.api as sm
try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus
from bme280 import BME280
from threading import Lock
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit
async_mode = None

# Initial declaration of variables
Temperature = "No sensor data!"
Pressure = "No sensor data!"
Humidity = "No sensor data!"
NewDate = 0
CurrentDate = 0
ServerTime = time.strftime('%Y-%m-%d %H:%M:%S')

currentMeasurements = {
    "temperature": "0",
    "pressure": "0",
    "humidity": "0",
                "date": ServerTime
}


# Setting up the variables as global


# creating the write to file thread
def WriteToFile_thread():
    while True:
        sleep(50)
        #currentMeasurements = {"temperature":Temperature,"pressure":Pressure,"humidity":Humidity,"date": ServerTime}

        if Temperature and Humidity and Pressure != 0:
            writeMeasurementsToFile(
                Temperature, Pressure, Humidity, ServerTime)
            print("##########-Writing to File-##########")


# Setup of the server
app = Flask(__name__)
app.config['SECRET_KEY'] = 'HRISTOsecretKey!'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)
socketio = SocketIO(app, async_mode=async_mode)
thread = None  # Set thread to none
thread_lock = Lock()  # Lock thread
bus = SMBus(1)
sensor = BME280(i2c_dev=bus)
# sensor = bme680.BME680()#Naming the sensor for use in the code


def ReadSensorValues():  # this function will read the data from the sensors and the current time and return those values

    global Temperature
    global Pressure
    global Humidity
    global ServerTime

    Temperature = sensor.get_temperature()
    Pressure = sensor.get_pressure()
    Humidity = sensor.get_humidity()
    # Getting the server time with format
    ServerTime = time.strftime('%Y-%m-%d %H:%M:%S')
    # print(Temperature)
    # print(Pressure)
    # print(Humidity)
    return


def background_thread():  # Defining the thread fucntion to read and update sensor data to the flask server
    SEC_FOR_UPDATE = 1
    while True:
        socketio.sleep(SEC_FOR_UPDATE)  # sleep for 1 second

        ReadSensorValues()

        socketio.emit('my_response',
                      {'data': 'Server generated event', 'T': '{0:.2f}'.format(sensor.get_temperature()), 'P': '{0:.2f}'.format(sensor.get_pressure()),
                       'H': '{0:.2f}'.format(sensor.get_humidity()), 'S': ServerTime},
                      namespace='/Weather')  # Send the sensor data and date to the web page as messages T for temperature etc.


def writeMeasurementsToFile(temperature, pressure, humidity, servertime, filename='data.json'):
    '''with open(filename,'r+') as file:
        # First we load existing data into a dict.
        file_data = json.load(file)
        # Join currentMeasurements with the existing data inside measurements
        file_data["measurements"].append(currentMeasurements)
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
        json.dump(file_data, file, indent = 4)'''
    header = ['date', 'temperature', 'pressure', 'humidity']
    data = [servertime, temperature, pressure, humidity]
    # print(os.path.exists('data.csv'))
    if(os.path.exists('data.csv')):
        with open('data.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow(data)
    else:
        with open('data.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerow(data)


# a fuction that fetches the historic data
def getJSONfile(filename='data.json'):
    with open(filename, 'r+') as file:
        file_data = json.load(file)
    return file_data


def predictTemperature():

    weather_data = pd.read_csv('GlasgowTempData.csv', parse_dates=[
        'timestamp'], sep=',', decimal='.', infer_datetime_format=True)

    # prepare dataset
    # extract only the date and temperature columns
    temp_df = weather_data[["timestamp",
                            "Glasgow Temperature [2 m elevation corrected]"]]

    temp_df = temp_df.rename(
        columns={'Glasgow Temperature [2 m elevation corrected]': 'temperature'})
    # convert the temperature column to type float
    temp_df["timestamp"] = pd.to_datetime(
        temp_df['timestamp'], infer_datetime_format=True)
    temp_df = temp_df.set_index(["timestamp"])
    temp_df["temperature"] = pd.to_numeric(
        temp_df["temperature"], downcast="float")
    predicted_df = temp_df["temperature"].to_frame().shift(
        1).rename(columns={"temperature": "T_pred"})
    actual_df = temp_df["temperature"].to_frame().rename(
        columns={"temperature": "T_actual"})
    #date_df = temp_df["date"].to_frame().rename(columns={"date": "Date"})
    one_step_df = pd.concat([actual_df, predicted_df], axis=1)
    one_step_df = one_step_df[1:]
    # print(one_step_df.head(15))

    # Calculate the RMSE
    #temp_pred_err = sqrt(MSE(one_step_df.T_actual, one_step_df.T_pred))
    #print("The RMSE is: ", temp_pred_err)
    #print("Predicted Average temp:", one_step_df["T_pred"].mean())

    # Fit the SARIMAX model using optimal parameters
    mod = sm.tsa.statespace.SARIMAX(one_step_df.T_actual,
                                    order=(1, 1, 1),
                                    seasonal_order=(1, 0, 1, 8),

                                    enforce_invertibility=False)

    results = mod.fit()

    # mod.summary()
    # results.show_model()
    results.plot_diagnostics(figsize=(15, 12))
    # plt.show()
    # print(one_step_df.head(15))
    # print(one_step_df.tail(15))

    pred = results.get_prediction(
        start=pd.to_datetime('2022-04-14'), dynamic=False)
    pred_ci = pred.conf_int()

    ax = one_step_df.T_actual['2022':].plot(label='observed')
    pred.predicted_mean.plot(ax=ax, label='Forecast')

    ax.fill_between(pred_ci.index,
                    pred_ci.iloc[:, 0],
                    pred_ci.iloc[:, 1], color='k', alpha=.2)

    ax.set_xlabel('Date')
    ax.set_ylabel('Temperature (in Celsius)')
    #plt.ylim([-20, 30])
    # plt.legend()
    # plt.show()

    y_forecasted = pred.predicted_mean
    y_truth = one_step_df.T_actual['2022-04-14':]
    # print(y_forecasted.shape)
    # print(y_truth.shape)
    # Compute the mean square error
    mse = MSE(y_truth, y_forecasted, squared=True)
    #print('The Mean Squared Error of forecasts is {}'.format(round(mse, 2)))
    #print("Predicted Average temp:", one_step_df["T_pred"].mean())
    temp = one_step_df["T_pred"].mean()
    # this route serves the prediction fucntinality
    # when the applcation loads and the document is loaded
    # this route is called to fetch the prediction
    formattedTemp = "%.2f" % temp
    return str(formattedTemp + "°C")


@app.route('/getPrediction')
def getPrediction():
    predictedTemp = predictTemperature()
    return predictedTemp


@app.route('/')  # Enable to use the hmtl page for displaying
def index():
    session.permanent = True
    return render_template('index.html', async_mode=socketio.async_mode, content=getJSONfile())


def calculateTemp():
    # load the data from csv file
    weather_data = pd.read_csv('GlasgowTempData.csv', parse_dates=[
        'timestamp'], sep=',', decimal='.', infer_datetime_format=True)
    # prepare dataset
    # extract only the date and temperature columns
    temp_df = weather_data[["timestamp",
                            "Glasgow Temperature [2 m elevation corrected]"]]

    temp_df = temp_df.rename(
        columns={'Glasgow Temperature [2 m elevation corrected]': 'temperature'})
# convert the temperature column to type float
    temp_df["timestamp"] = pd.to_datetime(
        temp_df['timestamp'], infer_datetime_format=True)
    temp_df = temp_df.set_index(["timestamp"])
    temp_df["temperature"] = pd.to_numeric(
        temp_df["temperature"], downcast="float")
    #plt.figure(figsize=(15, 7), dpi=100)
    #plt.plot(temp_df.timestamp, temp_df.temperature, color='tab:red')
    #plt.gca().set(title="test", xlabel='timestamp', ylabel='Degree')
    # plt.show()
    predicted_df = temp_df["temperature"].to_frame().shift(
        1).rename(columns={"temperature": "T_pred"})
    actual_df = temp_df["temperature"].to_frame().rename(
        columns={"temperature": "T_actual"})
    #date_df = temp_df["date"].to_frame().rename(columns={"date": "Date"})
    one_step_df = pd.concat([actual_df, predicted_df], axis=1)
    one_step_df = one_step_df[1:]
    # print(one_step_df.head(15))

    # Calculate the RMSE
    temp_pred_err = sqrt(MSE(one_step_df.T_actual, one_step_df.T_pred))
    #print("The RMSE is: ", temp_pred_err)
    #print("Predicted Average temp:", one_step_df["T_pred"].mean())
    p = d = q = range(0, 2)

    # Generate all different combinations of p, q and q triplets
    pdq = list(itertools.product(p, d, q))

    # Generate all different combinations of seasonal p, q and q triplets
    seasonal_pdq = [(x[0], x[1], x[2], 8)
                    for x in list(itertools.product(p, d, q))]

    for param in pdq:
        for param_seasonal in seasonal_pdq:
            try:
                mod = sm.tsa.statespace.SARIMAX(one_step_df.T_actual,
                                                order=param,
                                                seasonal_order=param_seasonal,

                                                enforce_invertibility=False)

            results = mod.fit()

            print('SARIMA{}x{}8 - AIC:{}'.format(param,
                  param_seasonal, results.aic))
            except:
                continue

    # Fit the SARIMAX model using optimal parameters
    mod = sm.tsa.statespace.SARIMAX(one_step_df.T_actual,
                                    order=(1, 1, 1),
                                    seasonal_order=(1, 0, 1, 8),

                                    enforce_invertibility=False)

    results = mod.fit()

    # mod.summary()
    # results.show_model()
    #results.plot_diagnostics(figsize=(15, 12))
    # plt.show()
    # print(one_step_df.head(15))
    # print(one_step_df.tail(15))
    pred = results.get_prediction(
        start=pd.to_datetime('2022-04-14'), dynamic=False)
    pred_ci = pred.conf_int()

    ax = one_step_df.T_actual['2022':].plot(label='observed')
    pred.predicted_mean.plot(ax=ax, label='Forecast')

    ax.fill_between(pred_ci.index,
                    pred_ci.iloc[:, 0],
                    pred_ci.iloc[:, 1], color='k', alpha=.2)

    ax.set_xlabel('Date')
    ax.set_ylabel('Temperature (in Celsius)')
    #plt.ylim([-20, 30])
    # plt.legend()
    # plt.show()
    y_forecasted = pred.predicted_mean
    y_truth = one_step_df.T_actual['2022-04-14':]
    print(y_forecasted.shape)
    print(y_truth.shape)
    # Compute the mean square error
    mse = MSE(y_truth, y_forecasted, squared=True)
    print('The Mean Squared Error of forecasts is {}'.format(round(mse, 2)))
    #print("Predicted Average temp:", one_step_df["T_pred"].mean())


@app.route('/getPrediction')
def getPrediction():
    predictedTemp = calculateTemp()
    return predictedTemp


# Testing the connection to the server
@socketio.on('connect', namespace='/Weather')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            # connect and start background_thread
            thread = socketio.start_background_task(target=background_thread)
            # initiate a new thread
            threadWriting = Thread(target=WriteToFile_thread)
            # make the thread deamonic i.e makes the thread run at the background until the main thread is terminated
            threadWriting.setDaemon(True)
            threadWriting.start()
    emit('my_response', {'data': 'Connected', 'T': 'Reading...', 'P': 'Reading...',
         'H': 'Reading...', 'S': 'Starting...'})  # To be displayed when the server is loaded


if __name__ == '__main__':  # Run server
    socketio.run(app, debug=True)
    # threadWriting.join()
    print("Server Stopped...")
