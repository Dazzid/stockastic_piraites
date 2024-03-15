import os
import numpy as np
from essentia.standard import TensorflowPredictMusiCNN, MonoLoader
import pandas as pd
import json

# Our models take audio streams at 16kHz
sr = 16000

def extract_features(audio_path):
    # Load audio
    audio = MonoLoader(filename=audio_path, sampleRate=sr)()
    activations = TensorflowPredictMusiCNN(graphFilename='models/mtt-musicnn-1.pb')(audio)
    return activations

# load the metadata
df = pd.read_csv('metadata.csv')

# add the activations as a column
df['activations'] = None

# go through all the rows of the metadata
for index, row in df.iterrows():
    # get the audio path
    audio_path = row['audio_path']

    # extract the activations from the audio
    activations = np.mean(extract_features(audio_path), axis=0)

    # save the activations to the dataframe
    df.at[index, 'activations'] = activations.tolist()

# save the dataframe to a json file
df.to_json('metadata2.json', orient='records')