import pandas as pd
import pydub as pb
import pydub.effects as pbe
import os
import numpy as np
import argparse
from .labels import all_labels


def softmax(x):
    """Compute softmax values for each sets of scores in x."""
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()


def main(args):
    classification = args["classes"]
    labels = all_labels[classification]
    metadata = pd.DataFrame()
    for file in os.listdir(f"{args['metadata_dir']}/{classification}/"):
        if not ".csv" in file:
            continue
        metadata = pd.concat(
            [metadata, pd.read_csv(f"{args['metadata_dir']}/{classification}/{file}")]
        )

    length = args["length"] * 60
    fade_duration = args["fade_duration"]
    genre = args["genre"]
    filename = args["filename"]
    num = 200

    metadata = metadata.loc[round(metadata["duration"]) >= 30]
    print(len(metadata))

    weights = np.array(metadata[genre])
    weights **= 3
    weights /= weights.sum()
    paths = metadata["path"]

    mix = np.random.choice(a=paths, size=min(num, len(paths)), replace=False, p=weights)

    audio = pb.AudioSegment.from_file(f"songs/{mix[0]}")
    for song in mix[1:]:
        song = pb.AudioSegment.from_file(f"songs/{song}")
        song = pbe.normalize(song)
        audio = audio.append(song, crossfade=fade_duration * 1000)
        if audio.duration_seconds > length:
            break

    audio.export(filename, format="wav")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--length", type=int, default=10)
    parser.add_argument("--fade_duration", type=int, default=3)
    parser.add_argument("--genre", type=str, default=None)
    parser.add_argument("--filename", type=str, default="out.mp3")
    parser.add_argument("--classes", type=str, default="discogs")
    parser.add_argument("--metadata_dir", type=str, default="metadata")
    args = vars(parser.parse_args())

    assert args["length"] > 0
    assert args["fade_duration"] > 0
    assert args["genre"] in all_labels[args["classes"]]

    main(args)
