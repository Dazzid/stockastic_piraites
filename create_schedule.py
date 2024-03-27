import string
import feedparser
import os
import shutil
import re
import random
import torch
import datetime
import json
import numpy as np
from songs.labels import all_labels
from songs import create_mix
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    HfArgumentParser,
    TrainingArguments,
    pipeline,
    logging,
)

styles = all_labels["jamendo"]
device = "cuda"
logging.set_verbosity_error()

# model_name = "mistralai/Mistral-7B-v0.1"
mistral_model_name = "mistralai/Mistral-7B-Instruct-v0.2"

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=False,
)
model = AutoModelForCausalLM.from_pretrained(
    mistral_model_name,
    quantization_config=bnb_config,
    torch_dtype=torch.bfloat16,
    device_map="auto",
    trust_remote_code=True,
)

tokenizer = AutoTokenizer.from_pretrained(mistral_model_name, trust_remote_code=True)


def sample_mistral(prompt):
    messages = [{"role": "user", "content": prompt}]
    encodeds = tokenizer.apply_chat_template(messages, return_tensors="pt")
    model_inputs = encodeds.to(device)
    generated_ids = model.generate(
        model_inputs,
        max_new_tokens=1000,
        do_sample=True,
        temperature=0.7,
        top_k=60,
        top_p=0.9,
    )
    decoded = tokenizer.batch_decode(generated_ids)
    answer = decoded[0].split("[/INST]")[-1][:-4]
    return answer


def generate_talk(session):
    previous = "(TALK 0)\nAnna: Hello Philip!\nPhilip: Hello Anna!\n"
    prompt = f"Generate a radio conversation of two commenters, Anna and Phillip. They are discussing {session['topic']}. Don't bring more people into the conversation, only two voices. Only refer to them with their names, avoid adding time or other elements. Start with greetings to the audience. The conversation should contain at least 1000 words. Following are earlier conversations from today {session['date']}. Avoid reusing the same topics, but reference what they said.\n(PREVIOUS CONVERSATIONS)\n{previous}\n(END OF PREVIOUS CONVERSATIONS).\nUse the tags 'Philip:' and 'Anna:' to indicate who is speaking. Introduce what is coming next, which is {session['next']}"

    answer = sample_mistral(prompt)

    answer = re.sub("\(.*?\)", "", answer)
    answer = re.sub("\[.*?\]", "", answer)
    answer = re.sub("\{.*?\}", "", answer)
    answer = re.sub("<.*?>", "", answer)
    answer = answer.replace("\n", "")
    answer = answer.replace("Anna:", "\nAnna:")
    answer = answer.replace("Philip:", "\nPhilip:")

    return answer


def generate_music(session):
    number = session["current_index"]
    args = {
        "filename": f"rendered/{number}_Music_0.wav",
        "length": MUSIC_MINUTES,
        "fade_duration": 3,
        "genre": session["genre"],
        "classes": "jamendo",
        "metadata_dir": "songs/metadata",
    }
    create_mix.main(args)


def generate_intro(session):
    prompt = f"You are a radio conductor. Introduce a radio program called 'Stochastic Pairate Radio'. Today is {session['date']}, time is {session['time']}. You are \"The Radio Guy\". Introduce yourself and introduce the day's topic, which is {session['topic']}. Introduce what music we'll listen to today, which is {session['genre']} music. The segment should be 1 minute long and in English. Introduce the next segment, which is {session['next']}. Use the tag <narrator> to specify who the speaker is."

    answer = sample_mistral(prompt)
    answer = re.sub("\(.*?\):", "", answer)
    answer = re.sub("\[.*?\]:", "", answer)
    answer = re.sub("\{.*?\}:", "", answer)
    answer = re.sub("<.*?>:", "", answer)

    answer = re.sub("\(.*?\)", "", answer)
    answer = re.sub("\[.*?\]", "", answer)
    answer = re.sub("\{.*?\}", "", answer)
    answer = re.sub("<.*?>", "", answer)
    answer = answer.replace("\n", "")

    return answer


def generate_weather(session):
    prompt = f"Create a weather forecast for a radio program. Today is {session['date']}. State the weather for today and for the upcoming days. The segment should be in English and at most 3 minutes long. Express temperatures in Celsius. Use the tag <narrator> to specify who the speaker is."

    answer = sample_mistral(prompt)
    answer = re.sub("\(.*?\):", "", answer)
    answer = re.sub("\[.*?\]:", "", answer)
    answer = re.sub("\{.*?\}:", "", answer)
    answer = re.sub("<.*?>:", "", answer)

    answer = re.sub("\(.*?\)", "", answer)
    answer = re.sub("\[.*?\]", "", answer)
    answer = re.sub("\{.*?\}", "", answer)
    answer = re.sub("<.*?>", "", answer)
    answer = answer.replace("\n", "")

    return answer


def generate_callsign(session):
    number = session["current_index"]
    jingle = f'jingles/{random.choice(os.listdir("jingles"))}'
    shutil.copyfile(jingle, f"rendered/{number}_Callsign_0.wav")

def generate_disclaimer(session):
    number = session["current_index"]
    disclaimer = f'complete/disclaimer.wav'
    shutil.copyfile(disclaimer, f"rendered/{number}_Disclaimer_0.wav")


def generate_invocation(session):
    # generate intro
    # generate invocation
    pass


def generate_news(session):
    with open("rss_feeds.txt", "r") as f:
        url = random.choice(f.read().split("\n"))
    print(url)
    feed = feedparser.parse(url)

    news = "\n".join(
        [f"{e['published']} - {e['title']}\n{e['summary']}" for e in feed["entries"]]
    )

    prompt = f"You are presenting the news as part of a radio program. The program is called Today's News. Your name is The News Guy. Today is {session['date']}. Present and discuss the following news:\n{news}\nUse the tag <narrator> to specify who the speaker is."

    answer = sample_mistral(prompt)
    answer = re.sub("\(.*?\):", "", answer)
    answer = re.sub("\[.*?\]:", "", answer)
    answer = re.sub("\{.*?\}:", "", answer)
    answer = re.sub("<.*?>:", "", answer)

    answer = re.sub("\(.*?\)", "", answer)
    answer = re.sub("\[.*?\]", "", answer)
    answer = re.sub("\{.*?\}", "", answer)
    answer = re.sub("<.*?>", "", answer)
    answer = answer.replace("\n", "")

    return answer


def generate_ad(session):
    prompt = f"Create an advertisement for a fictional product in a radio program. State the product name and what it can be used for. You can include price, contact information, slogans as you wish. Make the ad relevant to the day's topic, which is {session['topic']}. The advertisement should be in English and at most 1 minute long. Use the tag <narrator> to specify who the speaker is."

    answer = sample_mistral(prompt)
    answer = re.sub("\(.*?\):", "", answer)
    answer = re.sub("\[.*?\]:", "", answer)
    answer = re.sub("\{.*?\}:", "", answer)
    answer = re.sub("<.*?>:", "", answer)

    answer = re.sub("\(.*?\)", "", answer)
    answer = re.sub("\[.*?\]", "", answer)
    answer = re.sub("\{.*?\}", "", answer)
    answer = re.sub("<.*?>", "", answer)
    answer = answer.replace("\n", "")

    return answer


programs = {
    "Music": {"function": generate_music},
    "Talk": {"function": generate_talk},
    "Intro": {"function": generate_intro},
    "Weather": {"function": generate_weather},
    "Callsign": {"function": generate_callsign},
    "Invocation": {"function": generate_invocation},
    "Advertisement": {"function": generate_ad},
    "News": {"function": generate_news},
    "Disclaimer": {"function": generate_disclaimer},
}

schedule = [
    "Callsign",
    "Intro",
    "Advertisement",
    "Talk",
    "Music 10",
    "Invocation",
    "Callsign",
    "Advertisement",
    "News",
    "Weather",
    "Music 10",
    "Callsign",
    "Advertisement",
    "Music 10",
    "Talk",
    "Callsign",
    "Advertisement",
    "Talk",
    "Music 10",
    "Talk",
    "Callsign",
]

with open("schedule.txt", "r") as f:
    schedule = list(filter(None, f.read().split("\n")))

date = datetime.datetime.now()
scheduled_in = datetime.timedelta(minutes=30)
session_date = date + scheduled_in

with open("topics.txt", "r") as f:
    topics = f.read().split("\n")

session = {
    "date": f"{session_date.strftime('%A %d %B %Y')}",
    "time": f"{session_date.strftime('%H')}:00",
    "topic": random.choice(topics),
    "genre": random.choice(styles),
    "talks": [],
    "next": "",
    "current_index": "",
}
print(session)

session_schedule = list(filter(lambda x: (x != "Callsign"), schedule))
session_schedule = [
    s if not s.startswith("Music") else f"{session['genre']} music"
    for s in session_schedule
]
session_schedule.append("end of the program")
schedule_index = 0
# print(session_schedule)

os.system("rm session -fr")
os.system("mkdir session")
os.system("rm rendered -fr")
os.system("mkdir rendered")

for i, s in enumerate(schedule):
    if s != "Callsign":
        schedule_index += 1
    if s.startswith("Music"):
        MUSIC_MINUTES = int(s.split(" ")[1])
        s = s.split(" ")[0]

    session["next"] = session_schedule[schedule_index]
    session["current_index"] = i

    print(i, s)
    if s == "Talk":
        session["topic"] = random.choice(topics)
    generation = programs[s]["function"](session)
    if s == "Talk":
        session["talks"].append(generation)

    # print()

    if generation is None:
        continue
    with open(f"session/{i}_{s}.txt", "w") as file:
        file.write(generation)
