# Installation

## Python dependencies

```
pip3 install -r requirements.txt
```

## FFMPEG

Make sure to install FFMPEG on your system and have it in your PATH.
Note that ChoiceCam requires FFMPEG 4.2.2 or later. If it's not available from a standard repo, 
you might have to compile it yourself.

A decend guide for compiling on Raspberry Pi:
[https://pimylifeup.com/compiling-ffmpeg-raspberry-pi](https://pimylifeup.com/compiling-ffmpeg-raspberry-pi)

Note that to the FFMPEG configure phase the extra-libs flag might need to be changed so: `--extra-libs="-lpthread -lm -latomic"`

# Generating keys

```
python3 generate_keys.py
```

After this you can print the public key's QR code found under `config/server.pub.png` 

# Running

Only Mac (FaceTime) and Raspberry Pi cameras are supported.

```
python3 run.py
```


 