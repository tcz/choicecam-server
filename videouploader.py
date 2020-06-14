import shlex
import os
import subprocess
from crypto import encrypt_file
from config import \
    SYMMETRIC_KEY_FILE_PATH, \
    VIDEO_OUTPUT_PATH, \
    PLAYLIST_FILE_PATH, \
    provider_from_config
from urllib.request import urlopen
from urllib.error import HTTPError
import time

def load_segment_list_from_storage(provider):
    base_path = provider.base_path()
    segment_list = []

    try:
        segment_list_string = urlopen(base_path + 'segment_list').read().decode('utf-8')
        segment_list = segment_list_string.split("\n")
    except HTTPError as http_error:
        if http_error.code not in [404, 400, 403]:
            raise http_error

    return segment_list

def last_segment_from_segment_list(segment_list):
    if len(segment_list) == 0:
        return 0
    return int(max(segment_list))

def extract_thumbnail(video_file):
    segment_name = os.path.basename(video_file).replace('.ts', '')
    thumbnail_filename = os.path.join(VIDEO_OUTPUT_PATH, segment_name + '.jpg')
    unencrypted_thumbnail_filename = os.path.join(VIDEO_OUTPUT_PATH, segment_name + '.unencrypted.jpg')
    playlist_filename = os.path.join(VIDEO_OUTPUT_PATH, segment_name + '.m3u8')

    playlist = """\
#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:3
#EXT-X-MEDIA-SEQUENCE:1
#EXT-X-KEY:METHOD=AES-128,URI="{key_file}"
#EXTINF:3,
{segment_file}
#EXT-X-ENDLIST
    """.format(key_file=SYMMETRIC_KEY_FILE_PATH, segment_file=video_file)

    with open(playlist_filename, 'w') as playlist_file:
        playlist_file.write(playlist)

    if not os.path.isfile(unencrypted_thumbnail_filename):
        cmd = 'ffmpeg' + \
              ' -allowed_extensions ALL' + \
              ' -i ' + shlex.quote(playlist_filename) + \
              ' -vframes 1 -q:v 2 ' + unencrypted_thumbnail_filename

        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        process.wait()

    if not os.path.isfile(thumbnail_filename):
        encrypt_file(SYMMETRIC_KEY_FILE_PATH, unencrypted_thumbnail_filename, thumbnail_filename)
    os.remove(unencrypted_thumbnail_filename)
    os.remove(playlist_filename)
    return thumbnail_filename

def get_next_segment_file_to_sync(last_synced_segment_number):
    while True:
        next_unsynced_file = None
        for filename in sorted(os.listdir(VIDEO_OUTPUT_PATH)):
            if filename.endswith(".ts") and int(filename.replace('.ts', '')) > last_synced_segment_number:
                next_unsynced_file = os.path.join(VIDEO_OUTPUT_PATH, filename)
                break

        if next_unsynced_file is None or not os.path.isfile(PLAYLIST_FILE_PATH):
            time.sleep(0.1)
            continue

        return next_unsynced_file


def watch_directory():
    provider = provider_from_config()
    segment_list = load_segment_list_from_storage(provider)
    last_synced_segment_number = last_segment_from_segment_list(segment_list)

    while True:
        segment_filename = get_next_segment_file_to_sync(last_synced_segment_number)
        thumbnail_filename = extract_thumbnail(segment_filename)

        provider.sync_file(key=os.path.basename(segment_filename),
                           path=segment_filename,
                           content_type='video/MP2T')

        provider.sync_file(key=os.path.basename(thumbnail_filename),
                           path=thumbnail_filename,
                           content_type='image/jpeg')

        segment_name = os.path.basename(segment_filename).replace('.ts', '')
        segment_list.append(segment_name)
        last_synced_segment_number = last_segment_from_segment_list(segment_list)

        provider.sync_string(key='segment_list',
                             content="\n".join(segment_list),
                             content_type='text/plain')

        os.remove(segment_filename)
        os.remove(thumbnail_filename)

def run():
    watch_directory()