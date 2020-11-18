import xml.etree.ElementTree as ET
import pandas as pd
import datetime as dt
import numpy as np

def load_and_clean_xml(filename, save=False):
    '''
    load_and_clean_xml()

    Function that creates an xml tree from an xml file.
    Then parses that file to find only elements that are step counts.
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
        if (node.get('creationDate') >= "2020-09-16 22:05:05 -0700"):
            values.append(int(node.get('value')))
            credate.append(dt.datetime.strptime(node.get('creationDate'), '%Y-%m-%d %H:%M:%S %z'))
            startDates.append(dt.datetime.strptime(node.get('startDate'),  '%Y-%m-%d %H:%M:%S %z'))
            endDates.append(dt.datetime.strptime(node.get('endDate'), '%Y-%m-%d %H:%M:%S %z'))
            units.append(node.get('unit'))
            recordTypes.append(node.get('type'))

    cleaned_data_df = pd.DataFrame({"recordType" : recordTypes, "unit" : units, "creationDate" : credate, "startDate" : startDates, "endDate" : endDates, "value" : values}, 
                    columns=["recordType","unit","creationDate","startDate","endDate","value"])

    if save:
        cleaned_data_df.to_csv('cleaned_apple_steps.csv', index=False)

    return cleaned_data_df
    pass