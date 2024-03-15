import string
import feedparser
import os
import shutil
import re
import random
import nltk
import torch
import datetime
import json
import numpy as np
from suno import suno_mix
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    HfArgumentParser,
    TrainingArguments,
    pipeline,
    logging,
)

nltk.download("punkt")
nltk.download("averaged_perceptron_tagger")

with open("suno/metadata2.json", "r") as f:
    styles = json.load(f)

styles = [s["style"] for s in styles]
styles = ", ".join(styles).lower()
for s in string.punctuation.replace(",", ""):
    styles = styles.replace(s, "")

# print(styles)
tokens = nltk.word_tokenize(styles)
tokens = nltk.pos_tag(tokens)
allowed_pos_tags = ["FW", "JJ", "JJR", "JJS", "NN", "NNS", "NNP", "NNPS"]
tokens = list(filter(lambda x: x[1] in allowed_pos_tags, tokens))
styles = list(map(lambda x: x[0], tokens))
styles = np.unique(styles, return_counts=True)
indexes = np.flip(np.argsort(styles[1]))
styles = styles[0][indexes][styles[1][indexes] >= 25]


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
        "audio_output": f"rendered/{number}_Music_0.wav",
        "metadata_file": "suno/metadata2.json",
        "metadata_output": f"session/{number}_Music_0.json",
        "duration": 10,
        "fade_duration": 5,
        "tags": session["genre"],
    }
    suno_mix.main(args)


def generate_intro(session):
    prompt = f"You are a radio conductor. Introduce a radio program called 'Stochastic Pairate Radio'. Today is {session['date']}, time is {session['time']}. Introduce yourself and introduce the day's topic, which is {session['topic']}. Introduce what music we'll listen to today, which is {session['genre']} music. The segment should be 1 minute long and in English. Introduce the next segment, which is {session['next']}. Use the tag <narrator> to specify who the speaker is."

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


def generate_invocation(session):
    # generate intro
    # generate invocation
    pass


def generate_news(session):
    with open("rss_feeds.txt", "r") as f:
        url = random.choice(f.read().split('\n'))
    print(url)
    feed = feedparser.parse(url)

    news = "\n".join(
        [f"{e['published']} - {e['title']}\n{e['summary']}" for e in feed["entries"]]
    )

    prompt = f"You are presenting the news as part of a radio program. The program is called Improbable News. Your name is The News Guy. Today is {session['date']}. Present and discuss the following news:\n{news}\nUse the tag <narrator> to specify who the speaker is."

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
    prompt = f"Create an advertisement for a fictional product in a radio program. State the product name and what it can be used for. You can include price, contact information, slogans as you wish. Make sure to make it different from previous ads. The advertisement should be in English and at most 1 minute long. Use the tag <narrator> to specify who the speaker is."

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
    "Music": {"function": generate_music, "duration": 5},
    "Talk": {"function": generate_talk, "duration": 5},
    "Intro": {"function": generate_intro, "duration": 1},
    "Weather": {"function": generate_weather, "duration": 3},
    "Callsign": {"function": generate_callsign, "duration": 1},
    "Invocation": {"function": generate_invocation, "duration": 2},
    "Advertisement": {"function": generate_ad, "duration": 1},
    "News": {"function": generate_news, "duration": 1},
}

schedule = [
    "Callsign",
    "Intro",
    "Advertisement",
    "Talk",
    "Music",
    "Invocation",
    "Callsign",
    "Advertisement",
    "News",
    "Weather",
    "Music",
    "Callsign",
    "Advertisement",
    "Music",
    "Talk",
    "Callsign",
    "Advertisement",
    "Talk",
    "Music",
    "Talk",
    "Callsign",
]


date = datetime.datetime.now()
scheduled_in = datetime.timedelta(hours=1)
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
    s if s != "Music" else f"{session['genre']} music" for s in session_schedule
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
