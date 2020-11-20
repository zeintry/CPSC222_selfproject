import functions as func
import pandas as pd
import matplotlib.pyplot as plt

def main():
    # the cleaning step is commented out since the data only needs to be cleaned once and outputted 
    # to a csv for reuse. 
    steps_data_df = func.clean_xml('export.xml', save=True)
    
    plt.figure()  
    # plot the month versus number of steps
    for key, group in steps_data_df.groupby(pd.Grouper(key='creationDate', freq='D')):
        plt.bar(str(key.month) + '/' + str(key.day), sum(group['value']))
    plt.xticks(spacing=1.1, rotation='90')
    plt.xlabel('Days since 7/01/2020')
    plt.ylabel('Number of steps')
    plt.show()

    plt.figure()
    # plot the month versus number of steps
    for key, group in steps_data_df.groupby(pd.Grouper(key='creationDate', freq='W')):
        plt.bar(str(key.week - 27), sum(group['value']))
    plt.xlabel('Weeks since 7/01/2020')
    plt.ylabel('Number of steps')
    plt.show()

    plt.figure()  
    # plot the month versus number of steps
    for key, group in steps_data_df.groupby(pd.Grouper(key='creationDate', freq='M')):
        plt.bar(str(key.month), sum(group['value']))
    plt.xlabel('Month')
    plt.ylabel('Number of steps')
    plt.show()

main()