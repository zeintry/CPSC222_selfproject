import xml.etree.ElementTree as ET
import pandas as pd
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt

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
    if save:
        cleaned_data_df.to_csv('cleaned_apple_steps.csv', index=False)

    return cleaned_data_df
    pass

def print_bar(data, xlabel_str='', ylabel_str=None, custom_rot=None):
    plt.figure()  
    # plot the month versus number of steps
    for key, group in data.groupby(pd.Grouper(key='creationDate', freq='D')):
        plt.bar(str(key.month) + '/' + str(key.day), sum(group['value']))
    plt.xticks(rotation=custom_rot)
    plt.xlabel(xlabel_str)
    plt.ylabel(ylabel_str)
    plt.show()