import pandas
import functions as func
import pandas as pd

def main():
    # the cleaning step is commented out since the data only needs to be cleaned once and outputted 
    # to a csv for reuse. 
    steps_data_df = func.load_and_clean_xml('export.xml')

    steps_data_df = pd.read_csv('cleaned_apple_steps.csv', index_col='creationDate')

    print(steps_data_df.head())


main()