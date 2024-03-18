from TTS.api import TTS
import os

device = "cuda"
# use_tortoise = True
use_tortoise = True
if use_tortoise:
    tts_model_name = "tts_models/en/multi-dataset/tortoise-v2"
else:
    tts_model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
tts = TTS(model_name=tts_model_name, progress_bar=False).to(device)


def render_segment(text, speaker="emma", output_path="speech_test.wav"):
    if use_tortoise:
        tts.tts_to_file(
            text=text,
            file_path=output_path,
            num_autoregressive_samples=1,
            diffusion_iterations=10,
            voice_dir="./voices",
            speaker=speaker,
            preset="ultra_fast",
        )
    else:
        tts.tts_to_file(
            text=text, speaker=speaker, language="en", file_path=output_path
        )


# intro & weather
speaker_0 = []
# ads
speaker_1 = []
# anna
speaker_2 = []
# philip
speaker_3 = []
# open all files
files = os.listdir("session")
files.sort(key=lambda x: int(x.split("_")[0]))
for file in files:
    if not ".txt" in file:
        continue
    with open(f"session/{file}", "r") as f:
        data = f.read()
    number = file.split("_")[0]
    program = file.split(".")[0].split("_")[-1]

    obj = (number, program, data, 0)
    if program == "Intro" or program == "Weather" or program == 'News':
        speaker_0.append(obj)
    elif program == "Advertisement":
        speaker_1.append(obj)
    elif program == "Talk":
        for pos, line in enumerate(data.split("\n")):
            obj = (number, program, line, pos)
            if line.startswith("Anna:"):
                speaker_2.append(obj)
            elif line.startswith("Philip:"):
                speaker_3.append(obj)

for s in speaker_0:
    text = s[2].replace("?", "?\n").replace("!", "!\n")
    name = f"rendered/{s[0]}_{s[1]}_{s[3]}.wav"
    if use_tortoise:
        render_segment(text, speaker="daniel", output_path=name)
    else:
        render_segment(text, speaker="Craig Gutsy", output_path=name)

for s in speaker_1:
    text = s[2].replace("?", "?\n").replace("!", "!\n")
    name = f"rendered/{s[0]}_{s[1]}_{s[3]}.wav"
    if use_tortoise:
        render_segment(text, speaker="halle", output_path=name)
    else:
        render_segment(text, speaker="Chandra MacFarland", output_path=name)

for s in speaker_2:
    text = s[2].replace("Anna:", "").replace("?", "?\n").replace("!", "!\n")
    name = f"rendered/{s[0]}_{s[1]}_{s[3]}.wav"
    if use_tortoise:
        render_segment(text, speaker="emma", output_path=name)
    else:
        render_segment(text, speaker="Lilya Stainthorpe", output_path=name)

for s in speaker_3:
    text = s[2].replace("Philip:", "").replace("?", "?\n").replace("!", "!\n")
    name = f"rendered/{s[0]}_{s[1]}_{s[3]}.wav"
    if use_tortoise:
        render_segment(text, speaker="tom", output_path=name)
    else:
        render_segment(text, speaker="Torcull Diarmuid", output_path=name)
