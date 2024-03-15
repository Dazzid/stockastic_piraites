#%%

chirp_channel = 'chirp-beta-6'
with open('./html/' + chirp_channel + '.html', 'r') as f:
    html = f.read()

#%%
# get all of '.mp4' files
import re

mp4s = re.findall(r'href=[\'"]?([^\'" >]+)', html)
mp4s = [mp4 for mp4 in mp4s if '.mp4' in mp4]

print(len(mp4s))

# %%
# find the pattern ""Descargar" href=" and get the next characters until the next ;

descargas = re.findall(r'Descargar" href="([^;]+)', html)
# get the indices where the pattern "Descargar" href=" is found
indices_descargas = [m.start() for m in re.finditer('Descargar" href="', html)]
descargas = [descarga for descarga in descargas if '.mp4' in descarga]

print(len(descargas))
print(indices_descargas[0:3])

# %%
# find the pattern "<span>Text</span>" and get the next characters until the next '</span></div></div><div class="embedField_'

lyrics = re.findall(r'<span>Text</span>([^;]+)</span></div></div><div class="embedField_', html)
# get the indices where the pattern "<span>Text</span>" is found
indices_lyrics = [m.start() for m in re.finditer('<span>Text</span>', html)]
# remove all "</span>" and "<span>" from all lyrics
lyrics = [lyric.replace('</span>', '') for lyric in lyrics]
lyrics = [lyric.replace('<span>', '') for lyric in lyrics]
# remove all characters before the first '">'
lyrics = [lyric[lyric.find('">')+2:] for lyric in lyrics]
print(len(lyrics))
print(indices_lyrics[0:2])

# %%
# find the pattern '<span>Style of Music</span>' and get the next characters until the next '</div></div></div></div></div></article>'

styles = re.findall(r'<span>Style of Music</span>([^;]+)</div></div></div></div></div></article>', html)
# get the indices where the pattern '<span>Style of Music</span>' is found
indices_styles = [m.start() for m in re.finditer('<span>Style of Music</span>', html)]
# for all styles, get all styles between '<span>' and '</span>'
styles = [re.findall(r'<span>([^;]+)</span>', style) for style in styles]

print(len(styles))
print(indices_styles[0:2])

# %%
# create a dataframe with all the information, grouping multiple descargas to their lyrics and style according to the indices
import pandas as pd

# Create a list of dictionaries containing the information
data = []

# Iterate over the indices of descargas
for idx_descarga in indices_descargas:
    # Find the closest index of lyrics
    closest_lyrics = min(indices_lyrics, key=lambda x: abs(x - idx_descarga))
    
    # Find the closest index of styles
    closest_styles = min(indices_styles, key=lambda x: abs(x - idx_descarga))
    
    print("Descarga Index:", idx_descarga)
    print("Closest Lyrics Index:", closest_lyrics)
    print("Closest Styles Index:", closest_styles)

    try:
        # Extract the corresponding descarga, lyrics, and styles
        descarga = descargas[indices_descargas.index(idx_descarga)]
        lyric = lyrics[indices_lyrics.index(closest_lyrics)]
        style = styles[indices_styles.index(closest_styles)]
        
        print("Descarga:", descarga)
        print("Lyric:", lyric)
        print("Style:", style)

        # Append the information to the data list
        data.append({'Descarga': descarga, 'Lyric': lyric, 'Style': style})
    except:
        print("Error")
        pass

# %%
# Create a DataFrame from the list of dictionaries
df = pd.DataFrame(data)

# save the dataframe
df.to_csv('./csv/' + chirp_channel + '.csv', index=False)

# %%
#%%
print(descargas[0])
print(lyrics[0])
print(styles[0])