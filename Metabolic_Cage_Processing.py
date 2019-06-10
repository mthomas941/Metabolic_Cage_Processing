import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
import scipy.stats as stats
import datetime

#Read in files and put into dataframe
file_1 = pd.read_csv(str(input('File_1 Name: ')), skiprows=12, encoding='latin1') #Chow Cohort- Ghrelin pt. 1.csv
file_2 = pd.read_csv(str(input('File_2 Name: ')), skiprows=12, encoding='latin1') #Chow Cohort- Ghrelin pt. 2.csv

#Store and drop first row containing measurement units
measurement_units_dict = dict(zip(
    file_1.drop(['Date Time', 'Animal No.', 'Box', 'Unnamed: 25'], axis=1).fillna('[RER]').columns, 
    file_1.drop(['Date Time', 'Animal No.', 'Box', 'Unnamed: 25'], axis=1).fillna('[RER]').iloc[0].values)
                             )
file_1 = file_1.drop(index=0)
file_1.drop('Unnamed: 25', axis=1, inplace=True)
file_1 = file_1.reset_index(drop=True)
file_2 = file_2.drop(index=0)
file_2.drop('Unnamed: 25', axis=1, inplace=True)
file_2 = file_2.reset_index(drop=True)

#Convert Date Time to datetime and other columns to numeric (RER won't convert if an animal is missing...will convert later)
file_1 = file_1.apply(pd.to_numeric, errors='ignore')
file_1['Date Time'] = file_1['Date Time'].apply(pd.to_datetime)

file_2 = file_2.apply(pd.to_numeric, errors='ignore')
file_2['Date Time'] = file_2['Date Time'].apply(pd.to_datetime)

# Create new columns for date/hour/minute and then drop the earlier starting df rows until start hour is the same
file_1['date'] = file_1['Date Time'].dt.date
file_1['hour'] = file_1['Date Time'].dt.hour
file_1['minute'] = file_1['Date Time'].dt.minute

file_2['date'] = file_2['Date Time'].dt.date
file_2['hour'] = file_2['Date Time'].dt.hour
file_2['minute'] = file_2['Date Time'].dt.minute

# Drop the first time point for each animal until the HOURS are equal
time_start_file_1_hour = np.arange(0, len(file_1['hour']), (len(file_1['hour'])/8), dtype=int)
time_start_file_2_hour = np.arange(0, len(file_2['hour']), (len(file_2['hour'])/8), dtype=int)

while int(abs(file_2['hour'].iloc[0] - file_1['hour'].iloc[0])) != 0:
    time_start_file_1_hour = np.arange(0, len(file_1['hour']), (len(file_1['hour'])/8))
    time_start_file_2_hour = np.arange(0, len(file_2['hour']), (len(file_2['hour'])/8))
    file_1 = file_1.drop(index=time_start_file_1_hour)
    file_1 = file_1.reset_index(drop=True)
        
# Drop the first time point for each animal until the MINUTES are <30 min. apart (readings everfile_2 27)
time_start_file_1_minute = np.arange(0, len(file_1['minute']), (len(file_1['minute'])/8), dtype=int)
time_start_file_2_minute = np.arange(0, len(file_2['minute']), (len(file_2['minute'])/8), dtype=int)

while int(abs(file_2['minute'].iloc[0] - file_1['minute'].iloc[0])) > 30:
    time_start_file_1_minute = np.arange(0, len(file_1['minute']), (len(file_1['minute'])/8))
    time_start_file_2_minute = np.arange(0, len(file_2['minute']), (len(file_2['minute'])/8))
    file_1 = file_1.drop(index=time_start_file_1_minute)
    file_1 = file_1.reset_index(drop=True)
    
# Reduces number of time points for each animal in longer df to match animal value_counts in shorter df
time_matched_df = pd.DataFrame()
if len(file_2) > len(file_1):
    for i in file_2['Animal No.'].unique():
        time_matched_df = time_matched_df.append(file_2[file_2['Animal No.'] == i].iloc[:np.int(len(file_1)/8)])
        time_matched_df = time_matched_df.reset_index(drop=True)
    file_2 = time_matched_df

if len(file_2) < len(file_1):
    for i in file_1['Animal No.'].unique():
        time_matched_df = time_matched_df.append(file_1[file_1['Animal No.'] == i].iloc[:np.int(len(file_2)/8)])
        time_matched_df = time_matched_df.reset_index(drop=True)
    file_1 = time_matched_df

#Make Date Time for both files the same and concat files into single dataframe
file_2['Date Time'] = file_1['Date Time']
df = pd.concat([file_1, file_2]).reset_index(drop=True)

#Create lists for Cre+ and WT animal numbers (or any two groups)
group_1_list = input('Group_1 Animals (#, #, #...): ') #476, 481, 478, 487, 484, 491, 493
group_1_list = [int(s) for s in group_1_list.split(', ') if s.isdigit()]

group_2_list = input('Group_2 Animals (#, #, #...): ') #480, 477, 479, 482, 483, 489, 486
group_2_list = [int(s) for s in group_2_list.split(', ') if s.isdigit()]

#Create genotype identifiers for each group
group_1_genotype = input('Group_1 Genotype: ') #cre
group_2_genotype = input('Group_1 Genotype: ') #WT

#Create dict of animal id's and genotye to map
genotype_map_dict = dict(zip(group_1_list, [group_1_genotype for i in group_1_list]))
genotype_map_dict.update(dict(zip(group_2_list, [group_2_genotype for i in group_2_list])))

#Create new column for genotype and map each genotype according to animal id and corresponding group
df['Genotype'] = df['Animal No.'].map(genotype_map_dict)

#Drop any rows not containing an animal and convert RER to numeric
df = df.dropna().reset_index(drop=True)
df = df.apply(pd.to_numeric, errors='ignore')
df['Date Time'] = df['Date Time'].apply(pd.to_datetime)

#Drop unimportant columns and create .csv of combined, processed file
df = df.drop(columns=['date', 'hour', 'minute'])
combined_processed_file = str(input('Output File Name (*.csv): '))
df.to_csv(path_or_buf=combined_processed_file)
