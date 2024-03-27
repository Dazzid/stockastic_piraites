import os
import signal
import subprocess

print("Before you proceed, have you checked that:")
a = input('you have executed "sudo modprobe snd-aloop"? y/n')
a = input('you have executed "sudo alsactl init"? y/n')
a = input("OBS is running and streaming? y/n")
a = input("OBS has an Audio Capture Source(ALSA) active? y/n")
a = input("you are recording on a custom device set on plughw:CARD=Loopback,DEV=1? y/n")
device = "plughw:CARD=Loopback,DEV=0"

print("Generating first session")
generator_proc = subprocess.Popen(["sh", "radio.sh"], shell=False)
os.waitpid(generator_proc.pid, os.WUNTRACED)

while True:
    os.rename("complete/next_session.wav", "complete/current_session.wav")

    print("Playing...")
    player_proc = subprocess.Popen(
        ["aplay", "complete/current_session.wav", "--device", device], shell=False
    )

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
        emergency_proc = subprocess.Popen(
            ["aplay", "complete/emergency.wav", "--device", device], shell=False
        )

        # wait for generator
        os.waitpid(generator_id, os.WUNTRACED)
        # kill emergency music
        emergency_proc.kill()

    else:
        raise Exception

    print("All processes returned. Moving on.")
