import os
import pandas as pd

def combine_csv_files(input_directory, output_file):
    # List all CSV files in the input directory
    csv_files = [f for f in os.listdir(input_directory) if f.endswith('.csv')]

    # Initialize a list to hold dataframes
    dataframes = []

    # Read each CSV file and append to the list
    for csv_file in csv_files:
        file_path = os.path.join(input_directory, csv_file)
        df = pd.read_csv(file_path)
        dataframes.append(df)

    # Concatenate all dataframes
    combined_df = pd.concat(dataframes, ignore_index=True)

    # Write the combined dataframe to a new CSV file
    combined_df.to_csv(output_file, index=False)

if __name__ == "__main__":
    combine_csv_files('data', 'app_data\\data.csv')