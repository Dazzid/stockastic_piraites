from essentia.standard import (
    MonoLoader,
    TensorflowPredictEffnetDiscogs,
    TensorflowPredict2D,
)
import os
import pandas as pd
import numpy as np
from labels import all_labels
import argparse

labels = all_labels["jamendo"]

embedding_model = TensorflowPredictEffnetDiscogs(
    graphFilename="models/discogs-effnet-bs64-1.pb", output="PartitionedCall:1"
)

"""
model = TensorflowPredict2D(
    graphFilename="models/genre_discogs400-discogs-effnet-1.pb",
    input="serving_default_model_Placeholder",
    output="PartitionedCall:0",
)
"""

model = TensorflowPredict2D(
    graphFilename="models/mtg_jamendo_genre-discogs-effnet-1.pb"
)


metadata_folders = os.listdir("metadata/jamendo")
for folder in os.listdir("audio"):
    dataframe = {l: [] for l in labels}
    dataframe["path"] = []
    dataframe["duration"] = []
    if f"{folder}.csv" in metadata_folders:
        continue
    for audio in os.listdir(f"audio/{folder}"):
        file = f"audio/{folder}/{audio}"
        dataframe["path"].append(file)

        audio = MonoLoader(filename=file, sampleRate=16000, resampleQuality=4)()
        dataframe["duration"].append(len(audio) / 16000)

        embeddings = embedding_model(audio)

        predictions = model(embeddings)
        predictions = np.mean(predictions, axis=0)
        for i, l in zip(range(len(predictions)), labels):
            dataframe[l].append(predictions[i])
    dataframe = pd.DataFrame(dataframe)
    dataframe.to_csv(f"metadata/jamendo/{folder}.csv")
