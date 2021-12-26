#!/usr/bin/env /usr/bin/python3
import datetime
import json
import os.path


import upload_youtube
import config
import glob
import time
import subprocess

def get_meta(meta_file):
    with open(meta_file) as fh:
        meta = json.load(fh)
        if not 'done' in meta:
            meta['done'] = []
    return (meta)


def save_meta(meta_file, meta):
    with open(meta_file, 'w') as fh:
        json.dump(meta, fh)


def concat_videos(video_files, output):
    list_file_name = config.upload_dir + "files.txt"
    with open(list_file_name, "w") as fh:
        for video_file in video_files:
            fh.write("file '{}'\n".format(video_file))

    subprocess.check_call("ffmpeg -y -f concat -safe 0 -i '{}' -c copy '{}'".format(list_file_name, output), shell=True)


print("Scanning " + config.upload_dir)

meta_files = glob.glob(config.upload_dir + "*.meta")
meta_files.sort(key=os.path.getmtime)

prev_day = None
day_files = []

for meta_file in meta_files:
    print("Processing {} ...".format(meta_file))
    base_name = os.path.splitext(meta_file)[0]
    video_file = base_name + ".h264"
    meta = get_meta(meta_file)

    #get record day of file
    mtime=datetime.datetime.fromtimestamp(os.path.getmtime(meta_file))
    day = mtime.strftime("%m-%d-%Y")
    if prev_day == None:
        prev_day = day

    if day != prev_day:
        # upload
        output_file="{}My cats eating, {}.h264".format(config.upload_dir, prev_day)
        concat_videos(day_files, output_file)
        # if not 'youtube' in meta['done']:
        #     print("Uploading to youtube")
        #     # upload_youtube.upload(video_file,**meta)
        #     # meta['done'].append('youtube')
        #     save_meta(meta_file, meta)
        #     print("Done")

        prev_day = day
        day_files = []

    day_files.append(video_file)
