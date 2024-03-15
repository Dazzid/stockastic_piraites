import pandas as pd

df = pd.read_json('metadata2.json')

# find duplicates to the activations and remove them
df = df.drop_duplicates(subset=['activations'])

# get all activations and retrieve the 10 most similar to the first one
activations = df['activations'].values.tolist()

for i, activation in enumerate(activations):
    if activation is None:
        print(i, 'NONE')
        print(df.iloc[i])
        # replace none by zeroes
        activations[i] = [0] * 50

# get the first activation
first_activation = activations[0]

# get the 10 most similar activations
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

similarities = cosine_similarity([first_activation], activations)
similarities = similarities[0]

num_similar = 10
# get the indices of the 10 most similar activations
indices = np.argpartition(similarities, -num_similar)[-num_similar:]

# flip the indices so that the most similar activation is first
indices = indices[::-1]

# print the audio paths of the 10 most similar activations
for index in indices:
    print(index, df.iloc[index]['audio_path'])


# cross-fade the 10 most similar activations
import librosa
import soundfile as sf

audios = []
for index in indices:
    audio_path = df.iloc[index]['audio_path']
    audio, sr = librosa.load(audio_path, sr=16000)
    audios.append(audio)

# append the audios by crossfading them with a duration of 3 seconds
crossfaded_audio = audios[0]
overlap = int((3 - 1) * 16000)
for i, audio in enumerate(audios[1:]):
    # Fade in curve
    fade_in_curve = np.linspace(0.0, 1.0, overlap)

    # Fade out curve
    fade_out_curve = np.linspace(1.0, 0.0, overlap)

    crossfaded_audio[-overlap:] *= fade_out_curve
    crossfaded_audio[-overlap:] += audio[:overlap] * fade_in_curve  # Overlapping region
    crossfaded_audio = np.append(crossfaded_audio, audio[overlap:])

# save the crossfaded audio
sf.write('similar_mix.wav', crossfaded_audio, 16000)