# %%
import requests
import os
import pandas as pd

def download_all(chirp_channel):
    df = pd.read_csv('./csv/' + chirp_channel+'.csv')
    # mkdir chirp-beta-1
    if not os.path.exists(chirp_channel):
        os.makedirs(chirp_channel)

    for index, row in df.iterrows():
        # print(index)
        # print(row['Descarga'])
        # print(row['Lyric'])
        # print(row['Style'])
        
        # get the url of the mp4
        url = row['Descarga']
        # get the index of the row
        index = index
        # get the name of the mp4
        name = str(index) + '.mp4'

        # download the mp4
        r = requests.get(url, allow_redirects=True)
        open(chirp_channel + '/' + name, 'wb').write(r.content)

chirp_channel = 'chirp-beta-6'
download_all(chirp_channel)
# chirp_channel = 'chirp-beta-2'
# download_all(chirp_channel)
# chirp_channel = 'chirp-beta-3'
# download_all(chirp_channel)