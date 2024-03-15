import os
import random
import librosa
from collections import defaultdict
import numpy as np
import soundfile as sf


def normalize(audio):
    return audio / np.max(np.abs(audio))

if not 'complete' in os.listdir():
    os.makedirs('complete')

SAMPLE_RATE = 24000

files = os.listdir("./rendered")
files.sort(key=lambda x: int(x.split("_")[0]))

programs = defaultdict(list)

for f in files:
    programs[f.split("_")[0]].append(f)


all_loops = os.listdir("loops")

complete_audio = np.zeros((1))
for p in programs:
    programs[p].sort(key=lambda x: int(x.split(".")[0].split("_")[-1]))
    audio = np.zeros((1))
    for part in programs[p]:
        a, _ = librosa.load(f"rendered/{part}", sr=SAMPLE_RATE)
        a = normalize(a)
        audio = np.concatenate((audio, a))

    program_type = part.split("_")[1]
    if program_type == "Advertisement" or program_type == "Talk":
        loop, _ = librosa.load(f"loops/{random.choice(all_loops)}", sr=SAMPLE_RATE)
        loop = normalize(loop)
        background = np.tile(loop, 1 + len(audio) // len(loop))
        background = background[: len(audio)]
        audio *= 0.9
        background *= 0.1
        audio += background
    complete_audio = np.concatenate((complete_audio, audio))

sf.write(f"complete/session.mp3", complete_audio, SAMPLE_RATE, format="mp3")


print(programs)
