import pandas as pd
import os

#csv = pd.read_csv("suno_v3.5_ids.csv")
folder = "/home/marco/Desktop/stockastic_piraites/songs/metadata/json/"

#for r in csv["id"]:
for f in os.listdir(folder):
    name = f.replace('.json','.mp3')
    os.system(
        f"cp /media/marco/My\ Passport/suno/audio/{name} ~/Desktop/stockastic_piraites/songs/audio/suno_v3.5/ -f"
    )
