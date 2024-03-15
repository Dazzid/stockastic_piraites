import os
import random
import argparse
import librosa
import numpy as np
import soundfile as sf
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


def fade_in_fade_out(audio, sr, fade_duration):
    length = int(fade_duration * sr)

    # Fade in curve
    fade_in_curve = np.linspace(0.0, 1.0, length)

    # Fade out curve
    fade_out_curve = np.linspace(1.0, 0.0, length)

    # Apply fade in and fade out
    audio[:length] *= fade_in_curve
    audio[-length:] *= fade_out_curve

    return audio


def mix_audio_clips(audio_clips, sr, fade_duration):
    mixed_audio = []
    overlap = int((fade_duration - 1) * sr)

    for i, clip in enumerate(audio_clips):
        # Apply fade in/fade out
        audio = fade_in_fade_out(clip, sr, fade_duration)

        # Add the faded audio to mixed_audio with overlap
        if i > 0:
            mixed_audio[-overlap:] += audio[:overlap]  # Overlapping region

        mixed_audio.extend(audio[overlap:])

    return np.array(mixed_audio)


def get_similar_audios(metadata_file, num_similar, tags=None, reference_idx=None):
    df = pd.read_json(metadata_file)
    df = df.drop_duplicates(subset=["activations"])

    # drop all rows where 'style' doesn't contain any of the tags
    if tags:
        df = df[df["style"].apply(lambda x: any(tag in x for tag in tags))]

    # get all activations and retrieve the 10 most similar to the first one
    activations = df["activations"].values.tolist()

    for i, activation in enumerate(activations):
        if activation is None:
            print(i, "NONE")
            print(df.iloc[i])
            # replace none by zeroes
            activations[i] = [0] * 50

    if reference_idx is None:
        # get a random file
        reference_idx = random.randint(0, len(activations) - 1)

    reference_activation = activations[reference_idx]

    # get the num_similar most similar activations
    similarities = cosine_similarity([reference_activation], activations)
    similarities = similarities[0]

    # get the indices of the num_similar most similar activations
    indices = np.argpartition(similarities, -num_similar)[-num_similar:]

    # flip the indices so that the most similar activation is first
    indices = indices[::-1]

    audios = []
    similar_metadata_dict = {}

    # Add reference metadata to the dictionary
    similar_metadata_dict[reference_idx] = df.iloc[reference_idx].to_dict()

    for index in indices:
        audio_path = f'suno/{df.iloc[index]["audio_path"]}'
        audio, sr = librosa.load(audio_path, sr=16000)
        audios.append(audio)

        # Add metadata to the dictionary
        similar_metadata_dict[index] = df.iloc[index].to_dict()

    # Convert the dictionary to a DataFrame
    similar_metadata = pd.DataFrame.from_dict(similar_metadata_dict, orient="index")

    return audios, sr, similar_metadata


def main(args):
    # folder_path = args.folder
    audio_output_path = args["audio_output"]
    metadata_path = args["metadata_file"]
    metadata_output_path = args["metadata_output"]
    # Convert minutes to seconds
    target_duration = args["duration"] * 60
    fade_duration = args["fade_duration"]
    tags = args["tags"]

    # How many clips
    num_clips = (
        round(target_duration / 40) + 10
    )  # (clips are ~40s long, + 10 to make sure we have enough)

    # Get similar clips
    audio_clips, sr, metadata = get_similar_audios(
        metadata_path, num_clips - 1, tags=tags
    )

    # Mix audio clips with fade in/out
    mixed_audio = mix_audio_clips(audio_clips, sr, fade_duration)

    # Make sure the final audio is the desired duration
    mixed_audio = mixed_audio[: int(target_duration * sr)]

    # Export the final audio to WAV
    sf.write(audio_output_path, mixed_audio, sr)

    metadata.to_json(metadata_output_path)

    print(f"Final audio created and saved at: {audio_output_path}")
    print(f"Metadata saved at: {metadata_output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create an audio clip with fade in/out from random audio files in the metadata file."
    )
    # parser.add_argument("folder", help="Path to the folder containing MP4 files")
    parser.add_argument("audio_output", help="Path to the output WAV file")
    parser.add_argument("metadata_file", help="Json file with the metadata")
    parser.add_argument(
        "metadata_output", help="Json file with the metadata of the selected files"
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=15,
        help="Desired final duration in minutes (default: 15)",
    )
    parser.add_argument(
        "--fade_duration",
        type=float,
        default=3.0,
        help="Fade in/out duration in seconds (default: 3.0)",
    )
    parser.add_argument(
        "--tags", nargs="+", help="List of tags to filter metadata by style"
    )
    args = parser.parse_args()
    main(args)
