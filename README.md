# KSPR Stochastic Pirate Radio 🦜🏴‍☠️

To generate a new session:
```
sh radio.sh
```

## Environment

In a terminal:
```
python3 -m venv radio-env
source radio-env/bin/activate
pip install -r requirements.txt
```

## Use

The folders `jingles` and `loops` contain pre-generated material to be used as jingles and background music respectively.

The folder `suno` should contain the suno sogns to be used for the music mixes.

The files `topics.txt` and `rss_feeds.txt` should contain one entry per line and are used for topics of conversation and rss URLs respectively.

The folder `voices` should contain folders for each speaker with clean voice excerpts named sequentially `speaker_0/1.wav`, `speaker_0/2.wav` etc.

The generated session will be found in `complete/session.mp3`.

