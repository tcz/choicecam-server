import shlex
import os
import subprocess
from config import \
    SYMMETRIC_KEY_INFO_FILE_PATH, \
    VIDEO_OUTPUT_PATH, \
    PLAYLIST_FILE_PATH, \
    FONT_PATH
import time

def is_raspberry_pi():
    return os.uname().nodename == 'raspberrypi'

def get_unix_timestamp_with_timezone_offset():
    is_dst = time.daylight and time.localtime().tm_isdst > 0
    utc_offset = time.altzone if is_dst else time.timezone
    timestamp = round(time.time()) - utc_offset
    return timestamp

def construct_command():
    start_timestamp = get_unix_timestamp_with_timezone_offset()

    if is_raspberry_pi():
        command = 'raspivid -n -w 640 -h 360 -fps 25 -vf -t 86400000 -b 1800000 -ih -o - | ffmpeg -y -i - '
        codec = 'h264_omx'
    else:
        command = 'ffmpeg -y -f avfoundation -framerate 30 -i "FaceTime:MacBook" '
        codec = 'libx264'

    command = command + \
          ' -b 500k' + \
          ' -vf scale=640:360' + \
          ' -c:v ' + codec + \
          ' -pix_fmt yuv420p' + \
          ' -preset superfast' + \
          ' -tune zerolatency' + \
          ' -vf "drawtext=fontfile=' + shlex.quote(FONT_PATH) + ': text=\'%{pts\:gmtime\:' + \
          str(start_timestamp) + '\:%d-%m-%Y %T}\':' + \
          ' fontcolor=white: fontsize=h/10: x=(w-tw)/2: y=h-(2*lh):' + \
          ' box=1: boxcolor=0x00000000@1: boxborderw=5: alpha=0.5"' + \
          ' -f hls' + \
          ' -hls_time 3' + \
          ' -hls_list_size 1' + \
          ' -hls_start_number_source epoch ' + \
          ' -hls_flags temp_file' + \
          ' -hls_segment_filename ' + shlex.quote(os.path.join(VIDEO_OUTPUT_PATH, "%012d.ts")) + \
          ' -hls_segment_type mpegts' + \
          ' -hls_key_info_file ' + shlex.quote(SYMMETRIC_KEY_INFO_FILE_PATH) + \
          ' ' + shlex.quote(PLAYLIST_FILE_PATH)
          # ' -hide_banner -loglevel panic' + \

    return command


def run():
    command = construct_command()
    process = subprocess.Popen(command, shell=True)
    process.wait()