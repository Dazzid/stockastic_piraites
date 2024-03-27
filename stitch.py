import os
import random
import librosa
from collections import defaultdict
import numpy as np
import pydub as pb
import pydub.effects as pbe
import soundfile as sf


if not "complete" in os.listdir():
    os.makedirs("complete")

SAMPLE_RATE = 24000

files = os.listdir("./rendered")
files.sort(key=lambda x: int(x.split("_")[0]))

programs = defaultdict(list)

for f in files:
    programs[f.split("_")[0]].append(f)


all_loops = os.listdir("loops")

ramp_duration = 2000  # 1 second in milliseconds
start_time = 2000  # 2 seconds in milliseconds
threshold = -20.0  # Adjust the compression threshold (in dBFS) as needed
ratio = 4.0  # Adjust the compression ratio as needed

complete_audio = pb.AudioSegment.empty()
for p in programs:
    programs[p].sort(key=lambda x: int(x.split(".")[0].split("_")[-1]))
    audio = pb.AudioSegment.empty()
    for part in programs[p]:
        print(part)
        a = pb.AudioSegment.from_file(f"rendered/{part}", part.split(".")[-1])
        a = pbe.normalize(a)
        audio += a

    program_type = part.split("_")[1]
    if (
        program_type == "Advertisement"
        or program_type == "Talk"
        or program_type == "Weather"
        or program_type == "Disclaimer"
    ):
        loop = pb.AudioSegment.from_file(f"loops/{random.choice(all_loops)}")
        loop = pbe.normalize(loop)
        loop *= 1 + round(audio.duration_seconds / loop.duration_seconds)
        audio_before_ramp = loop[:start_time]
        audio_ramp = loop[start_time : start_time + ramp_duration].fade_out(
            ramp_duration
        )
        audio_after_ramp = loop[start_time + ramp_duration :]
        audio_half_volume = audio_after_ramp - 14
        background = audio_before_ramp + audio_ramp + audio_half_volume

        audio = pb.AudioSegment.silent(duration=start_time + ramp_duration) + audio
        audio = pbe.compress_dynamic_range(audio, threshold=threshold, ratio=ratio)
        audio = pbe.normalize(audio)
        audio = audio.overlay(background)

    complete_audio += audio

complete_audio.export(f"complete/next_session.wav", format="wav")


print(programs)
