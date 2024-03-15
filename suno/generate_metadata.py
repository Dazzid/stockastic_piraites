import os
import random
import argparse
import librosa
import numpy as np
from moviepy.editor import VideoFileClip
import soundfile as sf
import pandas as pd

def extract_audio(video_path, audio_path):
    video_clip = VideoFileClip(video_path)
    audio_clip = video_clip.audio

    # Save audio directly to the specified path
    audio_clip.write_audiofile(audio_path, codec='pcm_s16le', ffmpeg_params=["-loglevel", "quiet"])

    # return the length of the audio in seconds
    return audio_clip.duration


chirp_channels = ['chirp-beta-1', 'chirp-beta-2', 'chirp-beta-3', 'chirp-beta-4', 'chirp-beta-5', 'chirp-beta-6']

all_metadata = {}
video_idx = 0

# create audio folder if it doesn't exist
if not os.path.exists('audio'):
    os.makedirs('audio')

for chirp_channel in chirp_channels:
    csv_path = './csv/' + chirp_channel + '.csv'
    metadata = pd.read_csv(csv_path)

    # go through all the rows of the metadata
    for index, row in metadata.iterrows():
        # get the url of the mp4
        url = row['Descarga']
        # get the index of the row
        index = index
        # get the name of the mp4
        name = str(index) + '.mp4'

        # specify the audio path with the video_idx as name with 6 digits
        audio_path = 'audio/' + str(video_idx).zfill(6) + '.wav'

        # extract the audio from the mp4 and save it directly to the specified path
        duration = extract_audio(chirp_channel + '/' + name, audio_path)

        # remove all '</span><span>' from the style
        row['Style'] = row['Style'].replace('</span><span>', '')
        
        # add the metadata to the dictionary
        all_metadata[video_idx] = {'chirp_channel': chirp_channel, 'url': url, 'lyrics': row['Lyric'], 'style': row['Style'], 'audio_path': 'audio/' + str(video_idx).zfill(6) + '.wav', 'audio_seconds': duration}

        # increase the video_idx
        video_idx += 1

# save the dictionary to a csv file
df = pd.DataFrame.from_dict(all_metadata, orient='index')
print(df.head())
df.to_csv('metadata.csv', index=False)