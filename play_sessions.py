import os
import signal
import subprocess
import argparse

"""
print("Before you proceed, have you checked that:")
a = input('you have executed "sudo modprobe snd-aloop"? y/n')
a = input('you have executed "sudo alsactl init"? y/n')
a = input("OBS is running and streaming? y/n")
a = input("OBS has an Audio Capture Source(ALSA) active? y/n")
a = input("you are recording on a custom device set on plughw:CARD=Loopback,DEV=1? y/n")
device = "plughw:CARD=Loopback,DEV=0"
"""

parser = argparse.ArgumentParser()
parser.add_argument("--stream_url")
args = parser.parse_args()


def play(audio="test.mp3", image="image.png", loop=False):
    global args
    command = [
        "ffmpeg",
        "-loop",
        "1",
        "-i",
        image,
        "-re",
        "-stream_loop",
        "1",
        "-i",
        audio,
        "-c:v",
        "libx264",
        "-b:v",
        "12000k",
        "-preset",
        "veryfast",
        "-maxrate",
        "13500k",
        "-bufsize",
        "27000k",
        "-pix_fmt",
        "yuv420p",
        "-g",
        "50",
        "-c:a",
        "aac",
        "-b:a",
        "160k",
        "-ar",
        "48000",
        "-shortest",
        "-f",
        "flv",
        "-loglevel",
        "error",
        args.stream_url,
    ]
    if loop:
        # -loop
        command.pop(1)
        # 1
        command.pop(1)
        # -stream_loop
        command.pop(4)
        # 1
        command.pop(4)
    return subprocess.Popen(command, shell=False)


if "next_session.wav" not in os.listdir("complete"):
    print("Generating first session")
    generator_proc = subprocess.Popen(["sh", "radio.sh"], shell=False)
    os.waitpid(generator_proc.pid, os.WUNTRACED)

while True:
    os.rename("complete/next_session.wav", "complete/current_session.wav")

    print("Playing...")
    # player_proc = subprocess.Popen(["aplay", "complete/current_session.wav", "--device", device], shell=False)
    player_proc = play(audio="complete/current_session.wav", image="complete/kspr.png")

    print("Generating new session...")
    generator_proc = subprocess.Popen(["sh", "radio.sh"], shell=False)

    generator_id = generator_proc.pid
    player_id = player_proc.pid

    print(f"Generator process PID: {generator_id}")
    print(f"Player process PID: {player_id}")

    # who terminates first?
    waiting_for_child = False
    while not waiting_for_child:
        pid, _ = os.waitpid(0, os.WUNTRACED)
        waiting_for_child = pid == generator_id or pid == player_id
    print(f"Process PID {pid} returned.")

    if pid == generator_id:
        # generator ended before player
        # all good
        print("Generator done. Waiting for player.")

        # wait for player
        os.waitpid(player_id, os.WUNTRACED)
    elif pid == player_id:
        # player ended before generator
        # emergency music
        # emergency_proc = subprocess.Popen( ["aplay", "complete/emergency.wav", "--device", device], shell=False)
        emergency_proc = play(
            audio="complete/emergency.wav", image="complete/kspr.png", loop=True
        )

        # wait for generator
        os.waitpid(generator_id, os.WUNTRACED)
        # kill emergency music
        emergency_proc.kill()

    else:
        raise Exception

    print("All processes returned. Moving on.")
