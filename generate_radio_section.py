#%% import section
import torch
# Imports used through the rest of the notebook.
import torch
import torchaudio
import torch.nn as nn
import torch.nn.functional as F

from tortoise.api import TextToSpeech
from tortoise.utils.audio import load_audio, load_voice, load_voices
from ctransformers import AutoModelForCausalLM
from tqdm import tqdm
from datetime import datetime
from pydub import AudioSegment
from pydub.effects import normalize

import os

#preset super_fast, fast, standard, high_quality
preset = "fast"

# This will download all the models used by Tortoise from the HF hub.
# tts = TextToSpeech()
# If you want to use deepspeed the pass use_deepspeed=True nearly 2x faster than normal
tts = TextToSpeech(use_deepspeed=False, kv_cache=True, device='cuda')

# Set gpu_layers to the number of layers to offload to GPU. Set to 0 if no GPU acceleration is available on your system.
llm = AutoModelForCausalLM.from_pretrained("/workspace/data/Mistral-7B-Instruct-v0.1-GGUF", model_file="mistral-7b-instruct-v0.1.Q4_K_M.gguf", model_type="mistral", gpu_layers=50)

def checkVersion():
    print(torch.__version__)
    # Check if CUDA is available
    cuda_available = torch.cuda.is_available()

    # Print the result
    if cuda_available:
        print("CUDA is available in your PyTorch installation.")
        print("CUDA version:", torch.version.cuda)
    else:
        print("CUDA is not available in your PyTorch installation.")
        
#%% run topics   

import datetime

def get_day_of_week():
    # Get the current date and time
    current_datetime = datetime.datetime.now()

    # Use the strftime method to format the date and extract the day of the week
    day_of_week = current_datetime.strftime("%A")

    return day_of_week

# Call the function and print the result
day = get_day_of_week()
print("Today is", day)

#Create a list of topics
generalTopics = ["God", "chat G.P.T. religion", "quantum physics", "A.I. will make human useless", "descoveries in the human brain", "close the program"]

listOFTopics = ["They talk about if god exist or not, for instance if God created the universe and god is omniscient, omnipotent and omnibenevolent, why is needed a simulation? make it funny",
                "They talk about chat G.P.T. inventing a new religion that all humans are going to follow blindly",
                "They explain quantum physics for advanced audience, use complex terms",
                "They talk about A.I. will make humans useless, for instance, if A.I. can do everything, why do we need humans?",
                "They talk about recent descoveries in the human brain, make it funny",
                "They close the program, the Radio program is called 'Stockastic Piraites', make it funny"]

print("number of topics", len(listOFTopics))
preTopic = "Generate a radio conversation of two commentators, Anna and Phillip. "
topic = ""
postTopic = ". Don't bring more people into the conversation, only two voices. Only refers to them with their names, avoid adding time or other elements."

#Generate the conversations and save them in the data folder

mistral_generation = ""
changeTopic = ""
day = get_day_of_week()

for i in tqdm(range(len(listOFTopics))):
    print(i, "\n--------------------------------------")
    if i == 0:
        changeTopic = "Start with greetings too all the audience, knowing that today is " + day + ". "
    else:
        changeTopic = "No greetings, don't say hey. They were talking about " + generalTopics[i-1] + " and now they change to " + generalTopics[i] + ". "
    prompt =  preTopic + changeTopic + listOFTopics[i] + postTopic
    print(prompt+"\n")
    generate=llm(prompt, stream=False, max_new_tokens=512)
    print(generate, "\n")
    mistral_generation += generate
    
#Fix some text errors 
replacements = {
    "Anna:": "\nAnna:",
    "Phillip:": "\nPhillip:",
    "(laughing)": "hahahaha",
    "(laugh)": "hahaha",
    "(laughs)": "hahaha",
    "(smiling)": "hahaa",
    "(smile)": "hahaha",
    "(smiles)": "hahaha",
    "(chuckles)": "haha",
    "\n\n": "\n",
}
#Fix expressions 
final_text = mistral_generation
for old, new in replacements.items():
    final_text = final_text.replace(old, new)

final_text = final_text.replace("\n\n", "\n")
# Split the text into lines and get the first line
lines = final_text.splitlines()

# Check if the first line starts with "Anna:" or "Phillip:"
if lines and (lines[0].startswith("Anna:") or lines[0].startswith("Phillip:")):
    # Print the first line
    print("First line error fixed:", lines[0])
else:
    # Erase the first line
    lines.pop(0)

# Print the modified text (without the erased line)
final_text = '\n'.join(lines)

print(final_text)

#%% run audio generation  
def generateVoice(voice, text, preset, fileName):
    # Pick one of the voices from the output above
    # Load it and send it through Tortoise.
    voice_samples, conditioning_latents = load_voice(voice)
    gen = tts.tts_with_preset(text, voice_samples=voice_samples, conditioning_latents=conditioning_latents, preset=preset)
    torchaudio.save(fileName, gen.squeeze(0).cpu(), 24000)
    print("Saved to " + fileName)
    #IPython.display.Audio(fileName)
    

# Get the current date and time
def getCurrentTime():
    current_datetime = datetime.now()

    # Extract the date, hour, minute, and second components
    current_date = current_datetime.strftime("%d%m%y")
    current_hour = current_datetime.hour
    current_minute = current_datetime.minute
    current_second = current_datetime.second

    # Calculate the current second of the day
    current_second_of_day = current_hour * 3600 + current_minute * 60 + current_second

    # Create a unique ID for naming files
    file_id = f"{current_second_of_day}_{current_date}"
    return file_id


#generate the audio samples
def audioGeneration(voice, text, preset):
    print("----------------------------")
    print("speaker:", voice, "\n", text)
    path = "../workspace/data/presenters/"
    time = getCurrentTime()
    fileName =  path + time +"_"+ voice + '.wav'
    generateVoice(voice, text, preset, fileName)
    
# Specify the path to the 'data' folder
folder_path = '/workspace/data/presenters'

# Check if the folder exists before attempting to remove its contents
if os.path.exists(folder_path):
    # Get a list of all files in the 'data' folder
    files = os.listdir(folder_path)
    print(f"Removing {len(files)} files from {folder_path}...")
    # Iterate through the files and remove each one
    for file in files:
        file_path = os.path.join(folder_path, file)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Successfully deleted {file_path}")
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")
else:
    # If the folder doesn't exist, create it
    os.makedirs(folder_path)
    
#Split text into two sections dictionary, one for Anna and one for Phillip
lines = final_text.split('\n')

# Flag to determine the current speaker
current_speaker = None

# Iterate through lines and populate dictionaries
for line in lines:
    if line.startswith("Anna:"):
        current_speaker = "emma" #this is the voice name in the dataset
        text = line[len("anna:"):].strip()
        audioGeneration(current_speaker, text, preset)
        
    elif line.startswith("Phillip:"):
        current_speaker = "tom" #this is the voice name in the dataset
        text = line[len("phillip:"):].strip()
        audioGeneration(current_speaker, text, preset)
        
folder_path = "/workspace/data/presenters/"

# Get a list of all files in the folder
file_names = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

# Print the list of file names
# print("File names in the folder:")
# for file_name in file_names:
#     print(file_name)

#----------------------------------------------------------------------
print("Generating audio files...")

sourceFolder = "../workspace/data/rendered_audio/"

audio_segment = AudioSegment.silent(duration=0)
# Create an empty audio segment to hold the concatenated audio
concatenated_audio = AudioSegment.silent(duration=4000)

# Iterate through each audio file and concatenate it
for file in file_names:
    audio_segment = AudioSegment.from_file(folder_path+file, format="wav")
    # Normalize the audio to increase volume
    audio_segment = normalize(audio_segment)
    concatenated_audio += audio_segment

# Export the concatenated audio to a new file
concatenated_audio.export(sourceFolder+"concatenated_output_1.mp3", format="wav")

#----------------------------------------------------------------------
print("Generating background music...")

pathBackground = "../workspace/data/audio_background/"

# Load your audio tracks
track0 = AudioSegment.from_file(pathBackground+"opening_news.mp3", format="mp3")
track1 = AudioSegment.from_file(pathBackground+"Pop.mp3", format="mp3")
track2 = AudioSegment.from_file(pathBackground+"japanese_pop.mp3", format="mp3")
track3 = AudioSegment.from_file(pathBackground+"cumbia_3.mp3", format="mp3")

# Add the tracks together
combined_track = track0 + track1 + track2 + track3 + track0

# Reduce the volume to half with a ramp of 1 second after 2 seconds
ramp_duration = 2000  # 1 second in milliseconds
start_time = 2000  # 2 seconds in milliseconds

# Extract the part of the audio before the volume reduction
audio_before_ramp = combined_track[:start_time]

# Extract the part of the audio during the volume reduction and apply fade-out
audio_ramp = combined_track[start_time:start_time + ramp_duration].fade_out(ramp_duration)

# Extract the part of the audio after the volume reduction
audio_after_ramp = combined_track[start_time + ramp_duration:]

# Decrease the gain by 12 dB to reduce volume to half
audio_half_volume = audio_after_ramp - 13

# Combine the audio segments
final_audio = audio_before_ramp + audio_ramp + audio_half_volume 

# Export the modified audio to a new file
final_audio.export(pathBackground+"new_background.mp3", format="mp3")

#----------------------------------------------------------------------
print("Mixing background music with conversation...")
# Mix the background music with the conversation
background_music = AudioSegment.from_file(pathBackground+"new_background.mp3", format="mp3")

mixed_audio = concatenated_audio.overlay(background_music)  # Add more overlay calls for additional tracks
# Export the mixed audio to a new file
time = getCurrentTime()
fileName = sourceFolder+time+"_mixed_output.mp3"
mixed_audio.export(fileName, format="wav")
print(fileName)
