import pandas as pd


df = pd.read_csv('metadata.csv')
print(df.head())
print(df.describe())

# check which styles are in the dataset with their count
print(df['style'].value_counts())