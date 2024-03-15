import os
import random
import argparse
import librosa
import numpy as np
from moviepy.editor import VideoFileClip
import soundfile as sf

def extract_audio(video_path):
    video_clip = VideoFileClip(video_path)
    audio_clip = video_clip.audio

    # Save temporary WAV file
    temp_wav_path = 'temp.wav'
    audio_clip.write_audiofile(temp_wav_path, codec='pcm_s16le')

    # Load audio using librosa
    y, sr = librosa.load(temp_wav_path, sr=None)

    # Remove temporary WAV file
    os.remove(temp_wav_path)

    return y, sr

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

def main():
    parser = argparse.ArgumentParser(description="Create an audio clip with fade in/out from random MP4 files.")
    parser.add_argument("folder", help="Path to the folder containing MP4 files")
    parser.add_argument("output", help="Path to the output WAV file")
    parser.add_argument("--duration", type=float, default=15, help="Desired final duration in minutes (default: 15)")
    parser.add_argument("--fade_duration", type=float, default=3.0, help="Fade in/out duration in seconds (default: 3.0)")
    args = parser.parse_args()

    folder_path = args.folder
    output_path = args.output
    target_duration = args.duration * 60  # Convert minutes to seconds
    fade_duration = args.fade_duration

    # Get all MP4 files in the folder
    mp4_files = [file for file in os.listdir(folder_path) if file.endswith(".mp4")]

    # Select random clips
    selected_clips = random.sample(mp4_files, min(len(mp4_files), round(target_duration/40) + 10))  # (clips are ~40s long, + 10 to make sure we have enough)

    # Extract audio from selected clips
    audio_data = [extract_audio(os.path.join(folder_path, clip)) for clip in selected_clips]
    sr = audio_data[0][1]
    audio_clips = [audio[0] for audio in audio_data]

    # Mix audio clips with fade in/out
    mixed_audio = mix_audio_clips(audio_clips, sr, fade_duration)

    # Make sure the final audio is the desired duration
    mixed_audio = mixed_audio[:int(target_duration * sr)]

    # Export the final audio to WAV
    sf.write(output_path, mixed_audio, sr)

    print(f"Final audio created and saved at: {output_path}")

if __name__ == "__main__":
    main()
