from datetime import datetime
import xml.etree.ElementTree as ET
import pandas as pd
import datetime as dt
import numpy as np
from pandas.core.tools.datetimes import to_datetime
import matplotlib.pyplot as plt
import requests
import json
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import LabelEncoder

def clean_xml(filename, save=False):
    '''
    load_and_clean_xml()

    Function that creates an xml tree from an xml file.
    Then parses that file to find only elements that are step counts.
    Ouputs cleaned data to file.
    '''
    tree = ET.parse(filename)
    root = tree.getroot()

    values = []
    credate = []
    startDates = []
    endDates = []
    units = []
    recordTypes = []
    
    # traverse xml fro data
    for node in root.findall('.//Record[@type="HKQuantityTypeIdentifierStepCount"]'):    
        # only store nodes past a certain date
        if (node.get('creationDate') >= "2020-07-01 00:00:00 -0700"):
            values.append(int(node.get('value')))
            credate.append(dt.datetime.strptime(node.get('creationDate'), '%Y-%m-%d %H:%M:%S %z').date())
            startDates.append(dt.datetime.strptime(node.get('startDate'),  '%Y-%m-%d %H:%M:%S %z'))
            endDates.append(dt.datetime.strptime(node.get('endDate'), '%Y-%m-%d %H:%M:%S %z'))
            units.append(node.get('unit'))
            recordTypes.append(node.get('type'))

    cleaned_data_df = pd.DataFrame({"recordType" : recordTypes, "unit" : units, "creationDate" : credate, "startDate" : startDates, "endDate" : endDates, "value" : values}, 
                    columns=["recordType","unit","creationDate","startDate","endDate","value"])
    cleaned_data_df.creationDate = to_datetime(cleaned_data_df.creationDate)
    
    # format timestamps as UNIX timestamps for easier classification later
    cleaned_data_df['startDate'] = cleaned_data_df['startDate'].values.astype(np.int64) // 10 ** 9
    cleaned_data_df['endDate'] = cleaned_data_df['endDate'].values.astype(np.int64) // 10 ** 9
    # add columns to distinguish datetimes by week day and month
    cleaned_data_df['day of week (numeric)'] = pd.DatetimeIndex(cleaned_data_df['creationDate']).weekday
    cleaned_data_df['day of week (string)'] = pd.DatetimeIndex(cleaned_data_df['creationDate']).strftime('%A')
    cleaned_data_df['month'] = pd.DatetimeIndex(cleaned_data_df['creationDate']).month
    
    # store data if necessary
    if save:
        cleaned_data_df.to_csv('cleaned_apple_steps.csv', index=False)

    return cleaned_data_df
    pass

def plot_by_weekday(data):    
    # plot the day of week versus number of steps
    plt.figure()
    for key, group in data:
        plt.bar(str(key), sum(group['value']))
    plt.xlabel('Day of Week (0 = Monday)')
    plt.ylabel('Total number of steps')
    plt.title('Step count by day of the week')
    plt.show()
    
def plot_by_day(data):
    # plot the day versus number of steps
    plt.figure()
    for key, group in data:
        plt.bar(str(key.month) + '/' + str(key.day), sum(group['value']))
    plt.xticks(rotation='90')
    plt.xlabel('Days since 7/01/2020')
    plt.ylabel('Number of steps')
    plt.title('Daily step count')
    plt.show()
    
def plot_by_week(data):
    # plot the week versus number of steps
    plt.figure()
    for key, group in data:
        plt.bar(str(key.week - 27), sum(group['value']))
    plt.xlabel('Weeks since 7/01/2020')
    plt.ylabel('Number of steps')
    plt.title('Step count by week')
    plt.show()
    
def plot_by_month(data):
    # plot the month versus number of steps
    plt.figure()
    for key, group in data:
        plt.bar(str(key), sum(group['value']))
    plt.xlabel('Month')
    plt.ylabel('Number of steps')
    plt.title('Step count by month')
    plt.show()
    
def plot_by_holiday(data):
    plt.figure()
    for key, group in data.groupby(['holiday']):
        plt.bar(str(key), sum(group['value'])/ len(group['value']))
        
    plt.title('Average step count on holiday vs non-holiday')
    plt.xlabel('Not Holiday (0), Holiday (1)')
    plt.ylabel('Average step count')
    plt.show()
    
def mark_holidays(data, json_object):
    # mark days with a holiday with a one on dataset
    holidays = json_object['response']['holidays']

    for holiday in holidays:
        if (holiday['date']['iso'][0:10] < '2020-07-01'):
            pass
        else:
            for row in range(len(data['date'])):
                if (holiday['date']['iso'][0:10] == str(data.loc[row, 'date'])[0:10]):
                    data.at[row, 'holiday'] = 1
                    break;
                    
def get_holidays():
    '''
    function to call API and get response
    '''
    calendar_key = 'f73bce93a56ceebc4bed8fba53ea2f53e3044458'

    url = 'https://calendarific.com/api/v2/holidays'
    url += f"?api_key={calendar_key}"
    url += '&country=US'
    url += '&year=2020'

    response = requests.get(url=url)
    return json.loads(response.text)

def append_classification_info(data, holiday_response):
    '''
    Will add custom classification columns to dataset
    '''
    data['day of week'] = pd.DatetimeIndex(data['date']).weekday
    data['month'] = pd.DatetimeIndex(data['date']).month
    data['school'] = [0] * len(data['date'])
    for row in range(len(data['date'])):
                if (data.loc[row, 'date'] >= '2020-09-01'):
                    data.at[row, 'school'] = 1
                else:
                    data.at[row, 'school'] = 0
                    
    # mark holidays
    data['holiday'] = [0] * len(data['date'])
    mark_holidays(data, holiday_response)
                    
def group_by_day(input_data, output):
    '''
    custom group by day function
    '''
    data = input_data.groupby(pd.Grouper(key='creationDate', freq='D'))
    index = 0
    for key, value in data:
        output.loc[index, 'date'] = str(key)[0:10]
        output.loc[index, 'value'] = sum(value['value'])
        index += 1
        
def preprocess(X):
    '''
    Applies preprocessing to X
    '''
    # apply preprocessing to data
    scaler = MinMaxScaler()
    le = LabelEncoder()

    # reshape for the min maxer
    X['month'] = scaler.fit_transform(X['month'].values.reshape(-1,1))
    X['date'] = le.fit_transform(X['date'])