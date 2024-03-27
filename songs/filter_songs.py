import os
import pandas as pd
import json


def read_json_files(directory):
    data = []
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            with open(os.path.join(directory, filename), "r", encoding="utf-8") as file:
                json_data = json.load(file)
                # Extract required fields
                if "song_id" in json_data and "lyrics" in json_data:
                    data.append(
                        {"song_id": json_data["song_id"], "lyrics": json_data["lyrics"]}
                    )
    return data


def json_files_to_dataframe(directory):
    data = read_json_files(directory)
    df = pd.DataFrame(data)
    return df


def contains_inappropriate_language(lyrics, explicit_words):
    for word in explicit_words:
        if word in lyrics.lower():
            return True
    return False


directory_path = "./metadata/json"
explicit_word_path = "./wordlist.txt"


def read_explicit_word_list(file_path):
    words = []
    with open(file_path, "r") as file:
        for line in file:
            words.append(line.strip())
    return words


dataframe = json_files_to_dataframe(directory_path)
explicit_words = read_explicit_word_list(explicit_word_path)


inappropriate_songs = []
for index, row in dataframe.iterrows():
    if contains_inappropriate_language(row["lyrics"], explicit_words):
        inappropriate_songs.append(index)

# open csv
csv_metadata = pd.read_csv("./metadata/jamendo/suno.csv")
names = [
    f"audio/suno/{id}.mp3"
    for id in dataframe.iloc[inappropriate_songs]["song_id"].to_list()
]
print(csv_metadata)
indexes = csv_metadata[csv_metadata["path"].isin(names)].index.tolist()
print(indexes)
csv_metadata = csv_metadata.drop(indexes)
print(csv_metadata)
csv_metadata.to_csv("./metadata/jamendo/filtered_suno.csv")
