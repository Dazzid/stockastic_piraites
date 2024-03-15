import os
import random
import pygame

def play_random_subset(folder_path, subset_size=100):
    # Get a list of all wav files in the folder
    wav_files = [file for file in os.listdir(folder_path) if file.endswith('.wav')]

    # Ensure that subset_size is not greater than the total number of wav files
    subset_size = min(subset_size, len(wav_files))

    # Select a random subset of files
    selected_files = random.sample(wav_files, subset_size)

    # Shuffle the selected subset to play in random order
    random.shuffle(selected_files)

    # Initialize the mixer module from pygame
    pygame.mixer.init()

    try:
        for wav_file in selected_files:
            # Construct the full path to the wav file
            file_path = os.path.join(folder_path, wav_file)

            # Load and play the wav file
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()

            # Wait for the file to finish playing before moving to the next one
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

    except pygame.error as e:
        print("Error occurred:", e)
    finally:
        # Clean up and quit pygame
        pygame.mixer.quit()

# Specify the folder path where your wav files are located
folder_path = 'audio/'

# Call the function to play a random subset of 100 wav files
play_random_subset(folder_path, subset_size=100)
