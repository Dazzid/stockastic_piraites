import os
import signal
import subprocess
import argparse
import traceback

parser = argparse.ArgumentParser()
parser.add_argument("--stream_url")
args = parser.parse_args()

children = {}

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
    if not loop:
        # -stream_loop
        command.pop(6)
        # 1
        command.pop(6)

    print(command)
    return subprocess.Popen(command, shell=False)


try:
    if "next_session.wav" not in os.listdir("complete"):
        print("Generating first session")
        generator_proc = subprocess.Popen(["sh", "radio.sh"], shell=False)
        children[generator_proc.pid] = generator_proc

        # play emergency session
        emergency_proc = play(
            audio="complete/emergency.wav", image="complete/kspr.png", loop=True
        )
        children[emergency_proc.pid] = emergency_proc

        # wait for generator
        os.waitpid(generator_proc.pid, os.WUNTRACED)
        del children[generator_proc.pid]

        # kill emergency music
        emergency_proc.kill()
        del children[emergency_proc.pid]

    while True:
        os.rename("complete/next_session.wav", "complete/current_session.wav")

        print("Playing...")
        #player_proc = subprocess.Popen(["aplay", "complete/current_session.wav", "--device", device], shell=False)
        player_proc = play(audio="complete/current_session.wav", image="complete/kspr.png")
        children[player_proc.pid] = player_proc

        print("Generating new session...")
        generator_proc = subprocess.Popen(["sh", "radio.sh"], shell=False)
        children[generator_proc.pid] = generator_proc

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
            del children[pid]
            print("Generator done. Waiting for player.")

            # wait for player
            os.waitpid(player_id, os.WUNTRACED)
        elif pid == player_id:
            # player ended before generator
            del children[pid]

            # emergency music
            # emergency_proc = subprocess.Popen( ["aplay", "complete/emergency.wav", "--device", device], shell=False)
            emergency_proc = play(
                audio="complete/emergency.wav", image="complete/kspr.png", loop=True
            )
            children[emergency_proc.pid] = emergency_proc

            # wait for generator
            os.waitpid(generator_id, os.WUNTRACED)
            del children[generator_id]

            # kill emergency music
            emergency_proc.kill()
            del children[emergency_proc.pid]

        else:
            raise Exception

        print("All processes returned. Moving on.")

except Exception as e:
    traceback.print_exception(e)
finally:
    print("Terminating children.")
    print(children)
    for proc in children.values():
        print("Killing ", proc.pid)
        proc.kill()

